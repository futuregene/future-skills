# Lightweight catalog

This catalog is most useful after platform detection and a discussion of the intended change. Package IDs and repositories can change, so package-manager search is a helpful fallback when an exact ID no longer works.

## Core utilities

| Capability | Windows | macOS | Debian/Ubuntu |
|---|---|---|---|
| Homebrew bootstrap | Not applicable | Read the mainland reference or use the official installer | Avoid unless the user explicitly requests Linuxbrew |
| Git | `winget install --id Git.Git -e` | `brew install git` | `sudo apt install git` |
| GitHub CLI | `winget install --id GitHub.cli -e` | `brew install gh` | Follow the GitHub CLI official repository instructions |
| Python | `winget install 9NQ7512CXL7T -e`, then `py install` | `brew install python` | `sudo apt install python3 python3-venv python3-pip` |
| uv | `winget install --id astral-sh.uv -e` | `brew install uv` | `pipx install uv`; the distribution package manager can provide `pipx` when needed |
| jq | `winget install --id jqlang.jq -e` | `brew install jq` | `sudo apt install jq` |
| ripgrep | `winget install --id BurntSushi.ripgrep.MSVC -e` | `brew install ripgrep` | `sudo apt install ripgrep` |
| fd | `winget install --id sharkdp.fd -e` | `brew install fd` | `sudo apt install fd-find`; command may be `fdfind` |
| 7-Zip | `winget install --id 7zip.7zip -e` | `brew install sevenzip` | `sudo apt install p7zip-full` |
| SQLite CLI | `winget install --id SQLite.SQLite -e` | `brew install sqlite` | `sudo apt install sqlite3` |
| FFmpeg | `winget install --id Gyan.FFmpeg -e` | `brew install ffmpeg` | `sudo apt install ffmpeg` |
| ImageMagick | `winget install --id ImageMagick.ImageMagick -e` | `brew install imagemagick` | `sudo apt install imagemagick` |

FFmpeg and ImageMagick are typically relevant to a concrete media or image task.

## Chrome and Chromium

Check for a browser first:

- macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Windows: `%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe` or `%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe`
- Linux: `google-chrome-stable`, `google-chrome`, `chromium`, or `chromium-browser`

When Chrome is needed, these are common installation paths:

| Platform | Preferred method |
|---|---|
| Windows | `winget install --id Google.Chrome -e` |
| macOS | `brew install --cask google-chrome`; otherwise use the [official Google China download page](https://www.google.cn/chrome/) |
| Debian/Ubuntu x86-64 | Use the official Chrome `.deb`; if unavailable, install signed distribution Chromium |
| Linux ARM64 | Distribution Chromium is the compatible choice; AMD64 Chrome packages target a different architecture |

The resolved browser path and `--version` offer a simple verification. Reusing that browser for automation can avoid a second browser download; Playwright Chromium is useful when the existing browser cannot meet the task.

## Lightweight document libraries

Install these in an isolated Python environment, not globally:

| Format/task | Preferred libraries | Notes |
|---|---|---|
| PDF read, render, split, merge | `pymupdf`, `pypdf`, `pdfplumber` | Use OCR separately for scanned documents |
| PDF generation | `reportlab` | Build pages directly |
| DOCX read/write | `python-docx` | Does not render pages faithfully |
| DOCX semantic HTML/text | `mammoth` | Not a page-layout renderer |
| XLSX read/write | `openpyxl`, `xlsxwriter` | Libraries do not recalculate all Excel formulas |
| PPTX read/write | `python-pptx` | Does not render slides faithfully |

LibreOffice is a possible option when a library cannot provide the requested fidelity, especially for layout-sensitive conversion or rendering.
