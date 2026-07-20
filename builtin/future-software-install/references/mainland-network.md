# Mainland China network guidance

These sources are best suited to public packages and public metadata. Temporary configuration keeps the change scoped; a persistent mirror setting is easier to maintain when its rollback command is recorded alongside it.

## Contents

- [Mirror pairs at a glance](#mirror-pairs-at-a-glance)
- [Homebrew](#homebrew)
- [Python and uv](#python-and-uv)
- [npm and Node.js](#npm-and-nodejs)
- [WinGet](#winget)
- [Linux distribution repositories](#linux-distribution-repositories)
- [Chrome and browser binaries](#chrome-and-browser-binaries)

## Source policy

1. Try the official HTTPS source first when it is reachable.
2. Prefer official China endpoints, university mirrors, or ecosystem mirrors with a named operator.
3. Verify signatures or checksums provided by the upstream project.
4. Anonymous GitHub acceleration domains, unverified software-download sites, and HTTP-only endpoints offer less traceability than the sources above.
5. System security repositories are commonly left on their official source because mirrors can lag security updates.

## Mirror pairs at a glance

Choose one mirror for a task and keep the other as a fallback when connectivity or synchronization is poor. Mixing two public indexes in one dependency resolution can make results harder to reproduce.

| Repository | Primary | Fallback |
|---|---|---|
| Homebrew API and Bottles | TUNA | USTC |
| PyPI / uv | TUNA | USTC |
| npm registry | npmmirror | Huawei Cloud Mirrors |
| Node.js distributions | TUNA | USTC |
| WinGet source | Nanjing University | USTC |
| Debian/Ubuntu/Chromium system packages | TUNA | USTC |

## Homebrew

Homebrew is most common on macOS; Linuxbrew is available when a Linux setup calls for it. Command Line Tools are useful to check first. If `xcode-select -p` fails, `xcode-select --install` opens a system dialog.

For a temporary TUNA configuration:

```bash
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
```

The USTC alternative uses:

```bash
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
```

TUNA provides a bootstrap path when the official installer is not reachable:

```bash
BREW_INSTALL_DIR="$(mktemp -d)"
git clone --depth=1 https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/install.git "$BREW_INSTALL_DIR"
/bin/bash "$BREW_INSTALL_DIR/install.sh"
```

USTC also mirrors the bootstrap script at `https://mirrors.ustc.edu.cn/misc/brew-install.sh` when its source endpoint is selected. Its current Homebrew reference is <https://mirrors.ustc.edu.cn/help/brew.git.html>.

After installation, the appropriate `brew shellenv` path depends on the current shell. Shell-profile edits are a persistent change and are useful to review with the user. TUNA publishes current Homebrew and Bottle configuration at <https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/> and <https://mirrors.tuna.tsinghua.edu.cn/help/homebrew-bottles/>.

## Python and uv

Use TUNA PyPI for a one-off public package install:

```bash
PACKAGE_NAME="python-docx"
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "$PACKAGE_NAME"
```

The USTC alternative is:

```bash
PACKAGE_NAME="python-docx"
python -m pip install -i https://mirrors.ustc.edu.cn/pypi/simple "$PACKAGE_NAME"
```

For a FutureOS-managed uv environment, configure its managed `uv.toml`:

```toml
[[index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple/"
default = true
```

For USTC, replace the URL with `https://mirrors.ustc.edu.cn/pypi/simple`. USTC documents both pip and uv settings at <https://mirrors.ustc.edu.cn/help/pypi.html>.

Task-local pip or uv configuration keeps the user's existing global setup unchanged. TUNA maintains current pip and uv instructions at <https://mirrors.tuna.tsinghua.edu.cn/help/pypi/>.

## npm and Node.js

Use npmmirror for a one-off public npm installation:

```bash
PACKAGE_NAME="mammoth"
npm --registry=https://registry.npmmirror.com install "$PACKAGE_NAME"
```

Huawei Cloud Mirrors provides a second public registry endpoint:

```bash
PACKAGE_NAME="mammoth"
npm --registry=https://repo.huaweicloud.com/repository/npm/ install "$PACKAGE_NAME"
```

Public npm packages fit this mirror model best; private scopes and registries generally remain with their original or user-managed source. A global npm setting can be restored with:

```bash
npm config set registry https://registry.npmjs.org
```

When a package manager does not provide the needed Node version, TUNA and USTC both mirror Node.js distributions:

```bash
# TUNA
export NVM_NODEJS_ORG_MIRROR="https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/"

# USTC
export NVM_NODEJS_ORG_MIRROR="https://mirrors.ustc.edu.cn/node/"
```

Their direct download directories are <https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/> and <https://mirrors.ustc.edu.cn/node/>. Upstream checksums provide an additional integrity check.

## WinGet

Windows Package Manager supports named sources, so a mainland mirror can coexist with the default `winget` source. This is useful for comparing availability or using a mirror for a specific installation without replacing the existing configuration.

Adding or removing a source can prompt for elevation or source-agreement acceptance, depending on the Windows and WinGet configuration.

Inspect the current source list:

```powershell
winget source list
```

The following examples add an explicit source. Explicit sources are addressed with `--source`, which keeps ordinary WinGet commands on their existing source configuration:

```powershell
# Nanjing University mirror
winget source add --name winget-nju `
  --arg https://mirror.nju.edu.cn/winget-source `
  --trust-level trusted --explicit

# University of Science and Technology of China mirror
winget source add --name winget-ustc `
  --arg https://mirrors.ustc.edu.cn/winget-source `
  --trust-level trusted --explicit
```

Then search or install from the selected source:

```powershell
$PackageName = "jq"
$PackageId = "jqlang.jq"
winget search --source winget-nju $PackageName
winget install --source winget-ustc --id $PackageId -e
```

Useful maintenance commands:

```powershell
winget source update --name winget-nju
winget source remove --name winget-nju
winget source list --name winget-ustc
```

Using the mirror in place of the default source is another option. That change affects ordinary WinGet searches and installs, so it is helpful to show the current source list and discuss it with the user first. `winget source reset --force` restores WinGet's default sources, while also resetting custom source configuration.

These mirrors provide a WinGet source endpoint. Package metadata and cache retrieval can become faster, while the availability and origin of an individual installer still depend on that package's manifest. The mirror pages are <https://mirror.nju.edu.cn/winget-source/> and <https://mirrors.ustc.edu.cn/help/winget-source.html>. Microsoft documents source management, source trust, and reset behavior at <https://learn.microsoft.com/windows/package-manager/winget/source>.

## Linux distribution repositories

Before editing APT sources, inspect the distribution, version, architecture, and current source layout. Back up the exact source file and obtain approval. TUNA provides distinct Ubuntu and Ubuntu Ports endpoints; ARM systems require the ports endpoint. Keep the official security repository unless the user explicitly accepts mirror freshness tradeoffs.

Read the current mirror instructions rather than hard-coding a release codename. TUNA and USTC are the two reference choices:

- TUNA Ubuntu: <https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/>
- USTC Ubuntu: <https://mirrors.ustc.edu.cn/help/ubuntu.html>
- TUNA Ubuntu Ports: <https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu-ports/>
- USTC Ubuntu Ports: <https://mirrors.ustc.edu.cn/ubuntu-ports/>
- TUNA Debian: <https://mirrors.tuna.tsinghua.edu.cn/help/debian/>
- USTC Debian: <https://mirrors.ustc.edu.cn/help/debian.html>

## Chrome and browser binaries

WinGet is a convenient Windows route. On macOS, the official Google China download page is an alternative when Homebrew cannot obtain Chrome. Official Chrome packages provide clearer provenance than third-party DMG or EXE mirrors.

On Linux, Google's official x86-64 package is one route. If it is unreachable, the distribution's signed Chromium package can come from the configured TUNA or USTC system mirror. On ARM64, Chromium matches the available distribution architecture more naturally than an AMD64 Chrome package.

For browser automation, reusing system Chrome or Chromium can avoid downloading a separate Playwright browser. When a Playwright browser is useful, an internal artifact repository is often the most controllable source; a community mirror benefits from clear disclosure and temporary configuration.
