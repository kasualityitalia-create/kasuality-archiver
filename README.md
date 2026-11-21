![Kasuality Archiver](docs/social-preview.png)

# Kasuality Archiver — by Kasuality

[Download Page (Auto-Detect OS)](https://kasualityitalia-create.github.io/kasuality-archiver/) | [Open Mobile Web App (Android / iOS / iPadOS)](https://kasualityitalia-create.github.io/kasuality-archiver/app.html) | [Latest Desktop Releases (v1.0.1)](https://github.com/kasualityitalia-create/kasuality-archiver/releases/latest)

**Languages:** English | [Italiano](README.it.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md)

**Kasuality Archiver** is a 100% free, zero-ads, zero-nag-screen archive manager built by [Kasuality](https://www.kasuality.com/en/) for developers, designers, agencies, and everyday users.

## Key Advantages Over Legacy Archivers
- **100% Free, Zero Ads, Zero Nag Screens**: No trial popups, no upsells, no bundled adware.
- **Quick Look Without Extracting**: Preview text, code, JSON, Markdown, and images directly in memory without leaving temporary files on disk.
- **Zero-Trust Security Scan**: Automatically detects path traversal (`../../`), suspicious double extensions (such as `invoice.pdf.exe`), and zip-bomb anomalies before extraction.
- **Full-Text Search Inside Archives**: Search keywords or lines of code inside compressed files without unpacking.
- **Extract All or Selected Only**: Extract the entire archive or select specific files (`Ctrl + Click` or right-click -> *Extract selected only*).
- **Modern Formats + Smart Dev Exclude**: Supports `.zip`, `.7z`, `.tar.zst` (Zstandard), `.tar.gz`, `.tar`, `.tar.bz2`, `.tar.xz`, and `.zst`. Automatically skips `node_modules`, `.git`, `__pycache__`, `dist`, and `.venv`.
- **SHA-256 Verification + Built-In `(i)` User Guide**: Instant integrity hash copy and 5-language UI (`EN`, `IT`, `FR`, `ES`, `DE`).

## Mobile, Tablet, and Browser Use (No Installation)
Use **Kasuality Archiver Web** directly in your browser on **Android, iPhone, iPad, or Desktop** with zero server uploads (100% local processing via `CompressionStream` / `DecompressionStream`):
- Open: [https://kasualityitalia-create.github.io/kasuality-archiver/app.html](https://kasualityitalia-create.github.io/kasuality-archiver/app.html)
- Supports opening and creating `.zip` files, Quick Look, Full-Text search, Zero-Trust scan, selective download, and SHA-256.

## Desktop Installation (Windows, macOS, Linux)
Download the prebuilt package from [Releases](https://github.com/kasualityitalia-create/kasuality-archiver/releases/latest) or run from source:

```bash
pip install -r requirements.txt
