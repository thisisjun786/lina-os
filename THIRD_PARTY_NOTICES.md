# Third-party sources and components

The project license covers original Lina OS source and documentation. It does
not relicense third-party software, user data, credentials or future OS images.

| Source | Relationship | License / terms |
| --- | --- | --- |
| [Lina](https://github.com/thisisjun786/lina) | Product contracts and composition dependency, pinned in `modules.json`; runtime code is not vendored | [Apache-2.0](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/LICENSE) |
| [Omarchy](https://github.com/omacom/omarchy) | Planned desktop foundation; no OS package or image is included here | [MIT](https://github.com/omacom/omarchy/blob/a703092631599de5e70c5d3d2be4fbb268f8639b/LICENSE) |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Checksum-verified CI scanner downloaded at execution | [MIT](https://github.com/gitleaks/gitleaks/blob/v8.30.1/LICENSE) |
| [actionlint](https://github.com/rhysd/actionlint) | Checksum-verified CI workflow checker downloaded at execution | [MIT](https://github.com/rhysd/actionlint/blob/v1.7.12/LICENSE.txt) |

The OS plans also refer to Tailscale, OpenCodex, OmO Native, KasmVNC and wayvnc.
They are planned external components or backend candidates. No executable from
those projects is bundled in this source tree. Before copying or distributing
them, review the exact selected version and retain all required notices.

Before releasing an OS image, inventory every included component and its
redistribution/source obligations. Omarchy's license alone does not describe
all packages in a composed OS. Record artifact digests and source provenance
with that release; this file is not a completed distribution license audit.
