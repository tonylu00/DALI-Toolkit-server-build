"""One runner, three cross builds. Only explicit binary artifacts are published."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / 'source'
dist = root / 'dist'
dist.mkdir(exist_ok=True)
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
now = datetime.datetime.now(datetime.timezone.utc)
version = (source / 'VERSION').read_text().strip()
tag = os.environ.get('GITHUB_REF_NAME', '')
if os.environ.get('GITHUB_REF_TYPE') == 'tag' and tag.startswith('v'):
    version = tag
else:
    # Next patch dev versions sort above the current stable release.
    match = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        raise SystemExit('VERSION must contain a stable vMAJOR.MINOR.PATCH')
    major, minor, patch = map(int, match.groups())
    version = f'v{major}.{minor}.{patch + 1}-dev.{now:%Y%m%d%H%M%S}.{commit[:12]}'
if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?(?:\+[A-Za-z0-9.-]+)?', version):
    raise SystemExit('Invalid version tag')
channel = 'dev' if '-' in version else 'stable'
(dist / 'VERSION').write_text(version + '\n')
environment = dict(os.environ, CGO_ENABLED='0')
# The issuer seed stays in a temporary file, never in flags or artifact paths.
with tempfile.TemporaryDirectory() as temporary:
    key = Path(temporary) / 'update.key'
    key.write_text(os.environ['SERVER_UPDATE_SIGNING_KEY'].strip())
    key.chmod(0o600)
    signer = Path(temporary) / 'server-sign'
    subprocess.run(['go', 'build', '-trimpath', '-o', str(signer), './cmd/server-sign'], cwd=source, env=environment, check=True)
    for system, arch, label in [('linux', 'amd64', 'x64'), ('linux', 'arm64', 'aarch64'), ('windows', 'amd64', 'x64')]:
        name = f'dali-toolkit-server-{system}-{label}' + ('.exe' if system == 'windows' else '')
        binary = dist / name
        subprocess.run(['go', 'build', '-mod=readonly', '-trimpath',
                        f'-ldflags=-s -w -X main.Version={version} -X main.BuildTime={now:%Y-%m-%dT%H:%M:%SZ}',
                        '-o', str(binary), './cmd/server'], cwd=source,
                       env=dict(environment, GOOS=system, GOARCH=arch), check=True)
        manifest = dist / (name + '.manifest.json')
        manifest.write_bytes(json.dumps(dict(version=version, channel=channel, asset=name,
                                 sha256=hashlib.sha256(binary.read_bytes()).hexdigest(), size=binary.stat().st_size),
                                 separators=(',', ':')).encode())
        signature = dist / (name + '.sig')
        subprocess.run([str(signer), '-key', str(key), '-input', str(manifest), '-output', str(signature)], check=True)
        with zipfile.ZipFile(dist / f'dali-toolkit-server-{system}-{label}.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for item in [binary, manifest, signature, dist / 'VERSION']:
                archive.write(item, item.name)
(dist / 'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(dist.iterdir()) if p.name != 'SHA256SUMS'))
(root / 'dist-notes.md').write_text(f'Source commit: `{commit}`.\n\nSigned raw executables and ZIP archives for Linux x64/aarch64 and Windows x64. Each ZIP includes the executable, VERSION, manifest and signature. A machine licence is required.\n\nFor a raw Linux download, run `chmod +x dali-toolkit-server-linux-*`.\n')
