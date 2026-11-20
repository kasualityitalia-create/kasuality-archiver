"""Core archive engine for Kasuality Archiver.

Supports inspecting, previewing, full-text searching, security scanning,
safe extracting, and creating .zip, .7z, .tar.zst, .tar.gz, and .tar archives.
"""

from __future__ import annotations

import fnmatch
import hashlib
import io
import os
import posixpath
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Optional

import py7zr
import zstandard as zstd

SUPPORTED_OPEN_EXTENSIONS = (
    ".zip",
    ".7z",
    ".tar.zst",
    ".tzst",
    ".tar.gz",
    ".tgz",
    ".tar.bz2",
    ".tar.xz",
    ".tar",
    ".zst",
)

SUPPORTED_CREATE_FORMATS = ("zip", "7z", "tar.zst", "tar.gz")

DEFAULT_SMART_EXCLUDES = (
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".cache",
    ".DS_Store",
    "Thumbs.db",
)

DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".vbe", ".js", ".jse",
    ".wsf", ".wsh", ".hta", ".scr", ".pif", ".msi", ".msp", ".com",
    ".dll", ".cpl", ".reg", ".lnk",
}

TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".css",
    ".scss", ".html", ".htm", ".xml", ".svg", ".csv", ".log", ".yml",
    ".yaml", ".toml", ".ini", ".cfg", ".conf", ".env", ".sh", ".bat",
    ".ps1", ".sql", ".c", ".cpp", ".h", ".rs", ".go", ".java",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico"}

MAX_PREVIEW_BYTES = 2 * 1024 * 1024  # 2 MB cap for in-memory preview/search


@dataclass
class ArchiveEntry:
    name: str
    size: int
    compressed_size: int
    is_dir: bool
    format_name: str


@dataclass
class SecurityFinding:
    level: str  # "WARNING" or "DANGER"
    entry: str
    reason: str


@dataclass
class SecurityReport:
    status: str  # "SAFE", "WARNING", "DANGER"
    findings: List[SecurityFinding] = field(default_factory=list)
    total_entries: int = 0
    total_uncompressed: int = 0
    total_compressed: int = 0


@dataclass
class SearchMatch:
    entry_name: str
    line_number: int
    line_preview: str


def detect_archive_format(path: str | Path) -> str:
    lower = str(path).lower()
    if lower.endswith(".tar.zst") or lower.endswith(".tzst"):
        return "tar.zst"
    if lower.endswith(".tar.gz") or lower.endswith(".tgz"):
        return "tar.gz"
    if lower.endswith(".tar.bz2"):
        return "tar.bz2"
    if lower.endswith(".tar.xz"):
        return "tar.xz"
    if lower.endswith(".tar"):
        return "tar"
    if lower.endswith(".zip"):
        return "zip"
    if lower.endswith(".7z"):
        return "7z"
    if lower.endswith(".zst"):
        return "zst"
    raise ValueError(f"Formato archivio non supportato: {path}")


def _open_tar_from_zst(path: Path) -> tuple[tarfile.TarFile, io.BytesIO]:
    dctx = zstd.ZstdDecompressor()
    with open(path, "rb") as fh:
        with dctx.stream_reader(fh) as reader:
            raw = reader.read()
    buf = io.BytesIO(raw)
    tf = tarfile.open(fileobj=buf, mode="r:")
    return tf, buf


def list_entries(archive_path: str | Path) -> List[ArchiveEntry]:
    path = Path(archive_path)
    fmt = detect_archive_format(path)
    entries: List[ArchiveEntry] = []

    if fmt == "zip":
        with zipfile.ZipFile(path, "r") as zf:
            for info in zf.infolist():
                entries.append(
                    ArchiveEntry(
                        name=info.filename,
                        size=info.file_size,
                        compressed_size=info.compress_size,
                        is_dir=info.is_dir(),
                        format_name="zip",
                    )
                )
    elif fmt == "7z":
        with py7zr.SevenZipFile(path, "r") as sz:
            for info in sz.list():
                entries.append(
                    ArchiveEntry(
                        name=info.filename,
                        size=info.uncompressed or 0,
                        compressed_size=info.compressed or 0,
                        is_dir=info.is_directory,
                        format_name="7z",
                    )
                )
    elif fmt == "tar.zst":
        tf, _ = _open_tar_from_zst(path)
        with tf:
            for member in tf.getmembers():
                entries.append(
                    ArchiveEntry(
                        name=member.name,
                        size=member.size,
                        compressed_size=0,
                        is_dir=member.isdir(),
                        format_name="tar.zst",
                    )
                )
    elif fmt.startswith("tar"):
        mode = "r:*" if fmt != "tar" else "r:"
        with tarfile.open(path, mode) as tf:
            for member in tf.getmembers():
                entries.append(
                    ArchiveEntry(
                        name=member.name,
                        size=member.size,
                        compressed_size=0,
                        is_dir=member.isdir(),
                        format_name=fmt,
                    )
                )
    elif fmt == "zst":
        inner_name = path.stem or "payload"
        entries.append(
            ArchiveEntry(
                name=inner_name,
                size=0,
                compressed_size=path.stat().st_size,
                is_dir=False,
                format_name="zst",
            )
        )
    return entries


def _is_unsafe_path(entry_name: str) -> bool:
    normalized = entry_name.replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) >= 2 and normalized[1] == ":"):
        return True
    parts = [p for p in normalized.split("/") if p not in ("", ".")]
    return ".." in parts


def _has_double_extension(filename: str) -> bool:
    base = posixpath.basename(filename.replace("\\", "/"))
    parts = base.lower().split(".")
    if len(parts) < 3:
        return False
    return f".{parts[-1]}" in DANGEROUS_EXTENSIONS


def scan_archive(archive_path: str | Path) -> SecurityReport:
    entries = list_entries(archive_path)
    findings: List[SecurityFinding] = []
    total_uncompressed = 0
    total_compressed = 0

    for entry in entries:
        total_uncompressed += entry.size
        total_compressed += entry.compressed_size

        if _is_unsafe_path(entry.name):
            findings.append(
                SecurityFinding(
                    level="DANGER",
                    entry=entry.name,
                    reason="Path traversal rilevato (tentativo di scrittura fuori dalla cartella).",
                )
            )
        if entry.is_dir:
            continue

        lower_name = entry.name.lower()
        ext = Path(lower_name).suffix
        if _has_double_extension(lower_name):
            findings.append(
                SecurityFinding(
                    level="DANGER",
                    entry=entry.name,
                    reason="Doppia estensione sospetta su file eseguibile/script.",
                )
            )
        elif ext in DANGEROUS_EXTENSIONS:
            findings.append(
                SecurityFinding(
                    level="WARNING",
                    entry=entry.name,
                    reason=f"File potenzialmente eseguibile o script ({ext}).",
                )
            )

        if entry.compressed_size > 0 and entry.size / entry.compressed_size > 150 and entry.size > 50 * 1024 * 1024:
            findings.append(
                SecurityFinding(
                    level="WARNING",
                    entry=entry.name,
                    reason="Rapporto di compressione anomalo (possibile zip bomb).",
                )
            )

    status = "SAFE"
    if any(f.level == "DANGER" for f in findings):
        status = "DANGER"
    elif findings:
        status = "WARNING"

    return SecurityReport(
        status=status,
        findings=findings,
        total_entries=len(entries),
        total_uncompressed=total_uncompressed,
        total_compressed=total_compressed,
    )


def read_entry_bytes(
    archive_path: str | Path,
    entry_name: str,
    max_bytes: int = MAX_PREVIEW_BYTES,
) -> bytes:
    path = Path(archive_path)
    fmt = detect_archive_format(path)

    if fmt == "zip":
        with zipfile.ZipFile(path, "r") as zf:
            with zf.open(entry_name, "r") as fh:
                return fh.read(max_bytes)
    elif fmt == "7z":
        with tempfile.TemporaryDirectory() as tmp_dir:
            with py7zr.SevenZipFile(path, "r") as sz:
                sz.extract(path=tmp_dir, targets=[entry_name])
            extracted_file = Path(tmp_dir) / entry_name
            if not extracted_file.is_file():
                raise FileNotFoundError(entry_name)
            with open(extracted_file, "rb") as fh:
                return fh.read(max_bytes)
    elif fmt == "tar.zst":
        tf, _ = _open_tar_from_zst(path)
        with tf:
            fh = tf.extractfile(entry_name)
            if fh is None:
                raise FileNotFoundError(entry_name)
            return fh.read(max_bytes)
    elif fmt.startswith("tar"):
        mode = "r:*" if fmt != "tar" else "r:"
        with tarfile.open(path, mode) as tf:
            fh = tf.extractfile(entry_name)
            if fh is None:
                raise FileNotFoundError(entry_name)
            return fh.read(max_bytes)
    elif fmt == "zst":
        dctx = zstd.ZstdDecompressor()
        with open(path, "rb") as fh:
            with dctx.stream_reader(fh) as reader:
                return reader.read(max_bytes)
    raise ValueError(f"Formato non supportato: {fmt}")


def search_in_archive(
    archive_path: str | Path,
    query: str,
    case_sensitive: bool = False,
    max_matches: int = 200,
) -> List[SearchMatch]:
    if not query:
        return []
    entries = list_entries(archive_path)
    matches: List[SearchMatch] = []
    needle = query if case_sensitive else query.lower()

    for entry in entries:
        if entry.is_dir or entry.size > MAX_PREVIEW_BYTES:
            continue
        ext = Path(entry.name.lower()).suffix
        if ext and ext not in TEXT_EXTENSIONS:
            continue
        try:
            raw = read_entry_bytes(archive_path, entry.name, MAX_PREVIEW_BYTES)
            text = raw.decode("utf-8", errors="ignore")
        except Exception:
            continue

        for idx, line in enumerate(text.splitlines(), start=1):
            hay = line if case_sensitive else line.lower()
            if needle in hay:
                matches.append(
                    SearchMatch(
                        entry_name=entry.name,
                        line_number=idx,
                        line_preview=line.strip()[:160],
                    )
                )
                if len(matches) >= max_matches:
                    return matches
    return matches


def _safe_target_path(dest_dir: Path, member_name: str) -> Path:
    if _is_unsafe_path(member_name):
        raise ValueError(f"Estrazione bloccata per path traversal: {member_name}")
    dest_resolved = dest_dir.resolve()
    target = (dest_resolved / member_name.replace("\\", "/")).resolve()
    if os.path.commonpath([str(dest_resolved), str(target)]) != str(dest_resolved):
        raise ValueError(f"Percorso non sicuro rilevato: {member_name}")
    return target


def safe_extract(
    archive_path: str | Path,
    dest_dir: str | Path,
    selected_entries: Optional[Iterable[str]] = None,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> int:
    path = Path(archive_path)
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    fmt = detect_archive_format(path)
    selected_set = set(selected_entries) if selected_entries is not None else None
    extracted_count = 0

    if fmt == "zip":
        with zipfile.ZipFile(path, "r") as zf:
            infos = [
                i for i in zf.infolist()
                if selected_set is None or i.filename in selected_set
            ]
            total = len(infos)
            for idx, info in enumerate(infos, start=1):
                target = _safe_target_path(dest, info.filename)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(info, "r") as src, open(target, "wb") as dst:
                        dst.write(src.read())
                extracted_count += 1
                if progress_cb:
                    progress_cb(idx, total, info.filename)
    elif fmt == "7z":
        with py7zr.SevenZipFile(path, "r") as sz:
            all_infos = sz.list()
            targets = [
                i.filename for i in all_infos
                if selected_set is None or i.filename in selected_set
            ]
            for name in targets:
                _safe_target_path(dest, name)
            if selected_set is None:
                sz.extractall(path=dest)
            elif targets:
                sz.extract(path=dest, targets=targets)
            extracted_count = len(targets)
    elif fmt == "tar.zst":
        tf, _ = _open_tar_from_zst(path)
        with tf:
            members = [
                m for m in tf.getmembers()
                if selected_set is None or m.name in selected_set
            ]
            total = len(members)
            for idx, member in enumerate(members, start=1):
                if member.issym() or member.islnk():
                    raise ValueError(f"Symlink bloccato per sicurezza: {member.name}")
                target = _safe_target_path(dest, member.name)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    src = tf.extractfile(member)
                    if src is not None:
                        with open(target, "wb") as dst:
                            dst.write(src.read())
                extracted_count += 1
                if progress_cb:
                    progress_cb(idx, total, member.name)
    elif fmt.startswith("tar"):
        mode = "r:*" if fmt != "tar" else "r:"
        with tarfile.open(path, mode) as tf:
            members = [
                m for m in tf.getmembers()
                if selected_set is None or m.name in selected_set
            ]
            total = len(members)
            for idx, member in enumerate(members, start=1):
                if member.issym() or member.islnk():
                    raise ValueError(f"Symlink bloccato per sicurezza: {member.name}")
                target = _safe_target_path(dest, member.name)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    src = tf.extractfile(member)
                    if src is not None:
                        with open(target, "wb") as dst:
                            dst.write(src.read())
                extracted_count += 1
                if progress_cb:
                    progress_cb(idx, total, member.name)
    elif fmt == "zst":
        out_name = path.stem or "output"
        target = _safe_target_path(dest, out_name)
        dctx = zstd.ZstdDecompressor()
        with open(path, "rb") as src, open(target, "wb") as dst:
            dctx.copy_stream(src, dst)
        extracted_count = 1
    return extracted_count


def _should_exclude(rel_path: Path, exclude_patterns: Iterable[str]) -> bool:
    for part in rel_path.parts:
        for pat in exclude_patterns:
            if fnmatch.fnmatch(part, pat):
                return True
    return False


def collect_source_files(
    sources: Iterable[str | Path],
    smart_dev_exclude: bool = False,
    extra_excludes: Iterable[str] = (),
) -> List[tuple[Path, str]]:
    patterns = list(extra_excludes)
    if smart_dev_exclude:
        patterns.extend(DEFAULT_SMART_EXCLUDES)

    collected: List[tuple[Path, str]] = []
    for raw_src in sources:
        src = Path(raw_src).resolve()
        if src.is_file():
            collected.append((src, src.name))
        elif src.is_dir():
            base_parent = src.parent
            for root, dirs, files in os.walk(src):
                root_path = Path(root)
                rel_root = root_path.relative_to(base_parent)
                if patterns:
                    dirs[:] = [
                        d for d in dirs
                        if not _should_exclude(rel_root / d, patterns)
                    ]
                for fname in files:
                    fpath = root_path / fname
                    rel_file = fpath.relative_to(base_parent)
                    if patterns and _should_exclude(rel_file, patterns):
                        continue
                    collected.append((fpath, rel_file.as_posix()))
    return collected


def create_archive(
    sources: Iterable[str | Path],
    output_path: str | Path,
    fmt: str = "zip",
    smart_dev_exclude: bool = True,
    compression_level: int = 6,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> tuple[Path, str, int]:
    """Create an archive and return (output_path, sha256_hex, file_count)."""
    if fmt not in SUPPORTED_CREATE_FORMATS:
        raise ValueError(f"Formato non supportato: {fmt}")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    items = collect_source_files(sources, smart_dev_exclude=smart_dev_exclude)
    total = len(items)

    if fmt == "zip":
        lvl = max(0, min(9, compression_level))
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=lvl) as zf:
            for idx, (src, arcname) in enumerate(items, start=1):
                zf.write(src, arcname=arcname)
                if progress_cb:
                    progress_cb(idx, total, arcname)
    elif fmt == "7z":
        with py7zr.SevenZipFile(out, "w") as sz:
            for idx, (src, arcname) in enumerate(items, start=1):
                sz.write(src, arcname=arcname)
                if progress_cb:
                    progress_cb(idx, total, arcname)
    elif fmt == "tar.gz":
        lvl = max(1, min(9, compression_level))
        with tarfile.open(out, "w:gz", compresslevel=lvl) as tf:
            for idx, (src, arcname) in enumerate(items, start=1):
                tf.add(src, arcname=arcname)
                if progress_cb:
                    progress_cb(idx, total, arcname)
    elif fmt == "tar.zst":
        tar_buf = io.BytesIO()
        with tarfile.open(fileobj=tar_buf, mode="w:") as tf:
            for idx, (src, arcname) in enumerate(items, start=1):
                tf.add(src, arcname=arcname)
                if progress_cb:
                    progress_cb(idx, total, arcname)
        tar_buf.seek(0)
        z_lvl = max(1, min(19, compression_level * 2))
        cctx = zstd.ZstdCompressor(level=z_lvl, threads=-1)
        with open(out, "wb") as dst:
            cctx.copy_stream(tar_buf, dst)

    sha256 = compute_sha256(out)
    return out, sha256, total


def compute_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def format_bytes(num: int) -> str:
    value = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024.0
    return f"{num} B"
