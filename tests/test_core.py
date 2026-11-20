"""Unit tests for Kasuality Archiver core engine."""

import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import (  # noqa: E402
    create_archive,
    list_entries,
    read_entry_bytes,
    safe_extract,
    scan_archive,
    search_in_archive,
)


class TestKasualityArchiverCore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "sample_project"
        (self.src / "src").mkdir(parents=True)
        (self.src / "node_modules" / "pkg").mkdir(parents=True)
        (self.src / ".git").mkdir(parents=True)

        (self.src / "README.md").write_text("# Sample Project\nKasuality test token: K-UDA\n", encoding="utf-8")
        (self.src / "src" / "main.py").write_text("print('hello by Kasuality')\n", encoding="utf-8")
        (self.src / "node_modules" / "pkg" / "index.js").write_text("module.exports = 1;\n", encoding="utf-8")
        (self.src / ".git" / "config").write_text("[core]\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_list_search_extract_all_formats(self) -> None:
        for fmt in ("zip", "7z", "tar.zst", "tar.gz"):
            out_file = self.root / f"out.{fmt}"
            path, sha, count = create_archive([self.src], out_file, fmt=fmt, smart_dev_exclude=True)
            self.assertTrue(path.exists())
            self.assertEqual(len(sha), 64)
            self.assertEqual(count, 2)  # node_modules and .git excluded

            entries = list_entries(out_file)
            names = [e.name for e in entries]
            self.assertTrue(any("README.md" in n for n in names))
            self.assertFalse(any("node_modules" in n for n in names))
            self.assertFalse(any(".git" in n for n in names))

            matches = search_in_archive(out_file, "K-UDA")
            self.assertEqual(len(matches), 1)
            self.assertIn("README.md", matches[0].entry_name)

            readme_entry = next(n for n in names if n.endswith("README.md"))
            raw = read_entry_bytes(out_file, readme_entry)
            self.assertIn(b"Kasuality", raw)

            extract_dir = self.root / f"extracted_{fmt.replace('.', '_')}"
            safe_extract(out_file, extract_dir)
            self.assertTrue((extract_dir / "sample_project" / "src" / "main.py").exists())

            partial_dir = self.root / f"partial_{fmt.replace('.', '_')}"
            extracted_n = safe_extract(out_file, partial_dir, selected_entries=[readme_entry])
            self.assertEqual(extracted_n, 1)
            self.assertTrue((partial_dir / readme_entry).exists())
            self.assertFalse((partial_dir / "sample_project" / "src" / "main.py").exists())

    def test_security_scanner_and_safe_extract_block_traversal(self) -> None:
        evil_zip = self.root / "evil.zip"
        with zipfile.ZipFile(evil_zip, "w") as zf:
            zf.writestr("../../outside.txt", "evil")
            zf.writestr("fattura.pdf.exe", "MZ")

        report = scan_archive(evil_zip)
        self.assertEqual(report.status, "DANGER")
        self.assertGreaterEqual(len(report.findings), 2)

        with self.assertRaises(ValueError):
            safe_extract(evil_zip, self.root / "safe_dest")


if __name__ == "__main__":
    unittest.main()
