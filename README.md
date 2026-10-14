# DALI-Toolkit server releases

Public signed binaries for Linux x64, Linux aarch64, and Windows x64. Download
either a raw executable or its ZIP (which also contains VERSION and signatures).
Servers need no GitHub credentials to check or download published releases.

## Ubuntu one-command installation

```bash
curl -fsSL https://raw.githubusercontent.com/tonylu00/DALI-Toolkit-server-build/main/install.sh | sudo bash
```

The single script contains every setup template, detects Linux x64/aarch64,
downloads a raw executable, verifies its Ed25519 signature and SHA-256, and
configures PostgreSQL over its local socket and the systemd daemon. It prefers
stable releases and falls back to the latest signed public dev prerelease when
no stable release is published. Use `--channel stable` to require stable only.

Defaults: HTTP `127.0.0.1:8189`, public URL `https://dali.tonycloud.cn:28443`, and
entry point `/usr/local/bin/dali-toolkit-server`. HAProxy, certificates, DNS and
firewall configuration remain node-specific and are not modified.

Without a machine licence, installation finishes with the service stopped,
prints the machine hash and returns exit status 2. Obtain a signed licence for
that machine and rerun:

```bash
curl -fsSL https://raw.githubusercontent.com/tonylu00/DALI-Toolkit-server-build/main/install.sh | sudo bash -s -- --license ./server-license.json
```

Pass `--public-url https://node2.tonycloud.cn:30443` for another node's URL,
`--channel dev` to include prereleases, or `--use-mirror` to try the TonyCloud
mirror before GitHub. All downloads have mirror fallback and mandatory signature
verification. Reruns preserve existing binaries, secrets and update preferences.
Run the script with `--help` for local-binary and PostgreSQL options.

Only missing components are installed. Existing PostgreSQL is detected from
version-specific packages (such as `postgresql-16`), server binaries, registered
clusters and the selected socket, so the generic `postgresql` package is not
required. Missing PostgreSQL client tools are handled separately from the server.
When every dependency is available, apt is skipped entirely. Use `--pg-socket`
and `--pg-port` to select an existing non-default cluster; `--skip-packages` is
available to bypass dependency installation explicitly.

The public script is generated from an explicit deployment-file allow-list in
the private server repository (`deploy/ubuntu/build_installer.py`). It includes
installation code and public verification keys only; no backend source or issuer
secrets. Normal commits publishing installer changes do not trigger builds.

## Release pipeline

Stable versions are published from `v*` source tags; manual builds are public dev
prereleases. Normal branch commits never trigger a build. A draft is used only
while assets are uploading. One Linux runner cross-compiles all three targets.

The private source repository sends annotated trigger tags containing its exact
commit. This repository can also be dispatched manually with `source_ref`.
Required Actions secrets: `SERVER_SOURCE_SSH_KEY` (read-only source deploy key)
and `SERVER_UPDATE_SIGNING_KEY` (Ed25519 update seed). Neither secret is published.
Private backend source, signing keys, build caches and issuer tools are never release assets.

Update signatures cover the exact manifest bytes prefixed by
`dali-server/update/v1\n`; manifests bind version, channel, filename, size and SHA-256.
Verification key: `zGWiiF8JL4iWertPBL30lmn97WGs/Jy7w8ofiOFvm6E=`.
The server verifies signatures even when downloading through the mirror.

Offline licences bind to Linux machine-id or Windows MachineGuid. Request and
install a licence with `--license-request` and `--license-install FILE`.
