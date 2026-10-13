# DALI-Toolkit server releases

Public signed binaries for Linux x64, Linux aarch64, and Windows x64. Download
either a raw executable or its ZIP (which also contains VERSION and signatures).
Servers need no GitHub credentials to check or download published releases.

Stable versions are published from `v*` source tags; manual builds are public dev
prereleases. Normal branch commits never trigger a build. A draft is used only
while assets are uploading. One Linux runner cross-compiles all three targets.

The private source repository sends annotated trigger tags containing its exact
commit. This repository can also be dispatched manually with `source_ref`.
Required Actions secrets: `SERVER_SOURCE_SSH_KEY` (read-only source deploy key)
and `SERVER_UPDATE_SIGNING_KEY` (Ed25519 update seed). Neither secret is published.
Private source, signing keys, build caches and issuer tools are never release assets.

Update signatures cover the exact manifest bytes prefixed by
`dali-server/update/v1\n`; manifests bind version, channel, filename, size and SHA-256.
Verification key: `zGWiiF8JL4iWertPBL30lmn97WGs/Jy7w8ofiOFvm6E=`.
The server verifies signatures even when downloading through the mirror.

Offline licences bind to Linux machine-id or Windows MachineGuid. Request and
install a licence with `--license-request` and `--license-install FILE`.
