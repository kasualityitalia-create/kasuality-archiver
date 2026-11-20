"""Kasuality Archiver — Free, Zero-Trust Desktop Archiver by Kasuality."""

from __future__ import annotations

import ctypes
import io
import sys
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from core import (
    IMAGE_EXTENSIONS,
    SUPPORTED_CREATE_FORMATS,
    TEXT_EXTENSIONS,
    ArchiveEntry,
    SecurityReport,
    compute_sha256,
    create_archive,
    format_bytes,
    list_entries,
    read_entry_bytes,
    safe_extract,
    scan_archive,
    search_in_archive,
)
from i18n import SUPPORTED_LANGS, detect_default_lang, tr
from icons import (
    make_brand_icon,
    make_extract_icon,
    make_folder_icon,
    make_globe_icon,
    make_hash_icon,
    make_info_icon,
    make_plus_box_icon,
    make_search_icon,
    make_shield_icon,
)

# High-contrast accessible palette (WCAG AA+/AAA)
BG_DARK = "#0A0E17"
BG_PANEL = "#111827"
BG_CARD = "#1E293B"
BG_CARD_HOVER = "#334155"
BORDER_COLOR = "#475569"
FG_TEXT = "#F8FAFC"       # ~18:1 on BG_DARK
FG_MUTED = "#CBD5E1"      # ~11.8:1 on BG_PANEL (AAA)
LINK_BLUE = "#93C5FD"     # ~9.6:1 on BG_PANEL (AAA)
ACCENT = "#1D4ED8"        # ~6.7:1 with #FFFFFF (AA+/AAA bold)
ACCENT_HOVER = "#1E40AF"
SAFE_BG = "#064E3B"
SAFE_FG = "#A7F3D0"       # ~10.2:1 on SAFE_BG
WARN_BG = "#451A03"
WARN_FG = "#FDE68A"       # ~12.4:1 on WARN_BG
DANGER_BG = "#450A0A"
DANGER_FG = "#FECACA"     # ~11.9:1 on DANGER_BG


def _enable_dpi_awareness() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class KasualityArchiverApp(tk.Tk):
    def __init__(self, initial_file: str | None = None, lang: str | None = None) -> None:
        _enable_dpi_awareness()
        super().__init__()
        self.lang = lang if lang in SUPPORTED_LANGS else detect_default_lang()
        self.title(self.t("app_title"))
        self.geometry("1120x720")
        self.minsize(640, 520)
        self.configure(bg=BG_DARK)

        self.current_archive: Path | None = None
        self.entries: list[ArchiveEntry] = []
        self.security_report: SecurityReport | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None
        self._sash_initialized = False

        # Keep strong references to all PhotoImages
        self._icons = {
            "brand": make_brand_icon(24),
            "open": make_folder_icon(16),
            "new": make_plus_box_icon(16),
            "extract": make_extract_icon(16),
            "shield": make_shield_icon(16),
            "hash": make_hash_icon(16),
            "search": make_search_icon(16),
            "globe": make_globe_icon(16),
            "info": make_info_icon(16),
        }
        self.iconphoto(True, self._icons["brand"])

        self.search_var = tk.StringVar()
        self.search_mode_var = tk.StringVar(value="filename")
        self.status_var = tk.StringVar(value=self.t("ready_status"))

        self._setup_styles()
        self._build_ui()

        if initial_file and Path(initial_file).exists():
            self.after(150, lambda: self.load_archive(Path(initial_file)))

    def t(self, key: str, **kwargs) -> str:
        return tr(self.lang, key, **kwargs)

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=BG_PANEL,
            foreground=FG_TEXT,
            fieldbackground=BG_PANEL,
            borderwidth=0,
            rowheight=28,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=BG_CARD,
            foreground=FG_TEXT,
            relief="flat",
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#FFFFFF")],
        )

    def _make_btn(
        self,
        parent: tk.Widget,
        text: str,
        command,
        icon_key: str | None = None,
        primary: bool = False,
    ) -> tk.Button:
        bg = ACCENT if primary else BG_CARD
        active = ACCENT_HOVER if primary else BG_CARD_HOVER
        kwargs = {
            "text": f" {text}" if icon_key else text,
            "command": command,
            "bg": bg,
            "fg": "#FFFFFF" if primary else FG_TEXT,
            "activebackground": active,
            "activeforeground": "#FFFFFF",
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 1,
            "highlightbackground": "#60A5FA" if primary else BORDER_COLOR,
            "padx": 10,
            "pady": 6,
            "cursor": "hand2",
            "font": ("Segoe UI Semibold", 9),
        }
        if icon_key:
            kwargs["image"] = self._icons[icon_key]
            kwargs["compound"] = "left"
        return tk.Button(parent, **kwargs)

    def _build_ui(self) -> None:
        # Header Bar
        header = tk.Frame(self, bg=BG_PANEL, height=54, highlightthickness=1, highlightbackground=BORDER_COLOR)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        brand_frame = tk.Frame(header, bg=BG_PANEL)
        brand_frame.pack(side="left", padx=14)

        tk.Label(brand_frame, image=self._icons["brand"], bg=BG_PANEL).pack(side="left", padx=(0, 8))

        tk.Label(
            brand_frame,
            text="Kasuality Archiver",
            bg=BG_PANEL,
            fg=FG_TEXT,
            font=("Segoe UI Bold", 12),
        ).pack(side="left")

        brand_link = tk.Label(
            brand_frame,
            text="by Kasuality",
            bg=BG_PANEL,
            fg=LINK_BLUE,
            font=("Segoe UI Semibold", 9),
            cursor="hand2",
        )
        brand_link.pack(side="left", padx=(8, 0), pady=(2, 0))
        brand_link.bind("<Button-1>", lambda _e: webbrowser.open(f"https://www.kasuality.com/{self.lang}/"))

        right_hdr = tk.Frame(header, bg=BG_PANEL)
        right_hdr.pack(side="right", padx=14)

        self.security_badge = tk.Label(
            right_hdr,
            text=self.t("no_archive"),
            bg=BG_CARD,
            fg=FG_MUTED,
            padx=10,
            pady=4,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            font=("Segoe UI Semibold", 9),
        )
        self.security_badge.pack(side="left", padx=(0, 10))

        # High-contrast Language Selector Menubutton
        self.lang_btn = tk.Menubutton(
            right_hdr,
            text=f" {self.lang.upper()} ▾",
            image=self._icons["globe"],
            compound="left",
            bg=BG_CARD,
            fg=FG_TEXT,
            activebackground=BG_CARD_HOVER,
            activeforeground="#FFFFFF",
            relief="flat",
            highlightthickness=1,
            highlightbackground=LINK_BLUE,
            padx=10,
            pady=4,
            cursor="hand2",
            font=("Segoe UI Semibold", 9),
        )
        lang_menu = tk.Menu(
            self.lang_btn,
            tearoff=0,
            bg=BG_CARD,
            fg=FG_TEXT,
            activebackground=ACCENT,
            activeforeground="#FFFFFF",
            font=("Segoe UI Semibold", 9),
        )
        lang_names = {
            "en": "EN — English",
            "it": "IT — Italiano",
            "fr": "FR — Français",
            "es": "ES — Español",
            "de": "DE — Deutsch",
        }
        for code in SUPPORTED_LANGS:
            lang_menu.add_command(
                label=lang_names[code],
                command=lambda c=code: self.set_language(c),
            )
        self.lang_btn.configure(menu=lang_menu)
        self.lang_btn.pack(side="left", padx=(0, 8))

        self.btn_info = tk.Button(
            right_hdr,
            image=self._icons["info"],
            command=self.on_show_help,
            bg=BG_CARD,
            activebackground=BG_CARD_HOVER,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=LINK_BLUE,
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.btn_info.pack(side="left")

        # Toolbar Row 1 (Primary Actions with SVG-style icons)
        toolbar_row1 = tk.Frame(self, bg=BG_DARK, pady=6, padx=14)
        toolbar_row1.pack(fill="x")

        self.btn_open = self._make_btn(toolbar_row1, self.t("btn_open"), self.on_open_archive, "open", primary=True)
        self.btn_open.pack(side="left", padx=(0, 6))
        self.btn_new = self._make_btn(toolbar_row1, self.t("btn_new"), self.on_new_archive, "new")
        self.btn_new.pack(side="left", padx=(0, 6))
        self.btn_extract = self._make_btn(toolbar_row1, self.t("btn_extract"), self.on_extract_archive, "extract")
        self.btn_extract.pack(side="left", padx=(0, 6))
        self.btn_security = self._make_btn(toolbar_row1, self.t("btn_security"), self.on_show_security_report, "shield")
        self.btn_security.pack(side="left", padx=(0, 6))
        self.btn_sha = self._make_btn(toolbar_row1, self.t("btn_sha"), self.on_show_sha256, "hash")
        self.btn_sha.pack(side="left")

        # Toolbar Row 2 (Search Bar — never clips)
        toolbar_row2 = tk.Frame(self, bg=BG_DARK, pady=4, padx=14)
        toolbar_row2.pack(fill="x")

        self.rb_name = tk.Radiobutton(
            toolbar_row2,
            text=self.t("mode_filename"),
            variable=self.search_mode_var,
            value="filename",
            bg=BG_DARK,
            fg=FG_MUTED,
            selectcolor=BG_CARD,
            activebackground=BG_DARK,
            activeforeground=FG_TEXT,
            font=("Segoe UI", 9),
            command=self.on_search,
        )
        self.rb_name.pack(side="left", padx=(0, 6))

        self.rb_content = tk.Radiobutton(
            toolbar_row2,
            text=self.t("mode_content"),
            variable=self.search_mode_var,
            value="content",
            bg=BG_DARK,
            fg=FG_MUTED,
            selectcolor=BG_CARD,
            activebackground=BG_DARK,
            activeforeground=FG_TEXT,
            font=("Segoe UI", 9),
            command=self.on_search,
        )
        self.rb_content.pack(side="left", padx=(0, 10))

        self.btn_search = self._make_btn(toolbar_row2, self.t("btn_search"), self.on_search, "search")
        self.btn_search.pack(side="right")

        search_entry = tk.Entry(
            toolbar_row2,
            textvariable=self.search_var,
            bg=BG_CARD,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=LINK_BLUE,
            font=("Segoe UI", 10),
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))
        search_entry.bind("<Return>", lambda _e: self.on_search())

        # Main Split Pane (50% left / 50% right)
        self.paned = tk.PanedWindow(
            self,
            orient="horizontal",
            bg=BORDER_COLOR,
            sashwidth=4,
            bd=0,
        )
        self.paned.pack(fill="both", expand=True, padx=14, pady=(4, 6))

        left_frame = tk.Frame(self.paned, bg=BG_PANEL)
        self.paned.add(left_frame, minsize=260)

        cols = ("name", "size", "compressed", "type")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("name", text=self.t("col_path"))
        self.tree.heading("size", text=self.t("col_size"))
        self.tree.heading("compressed", text=self.t("col_comp"))
        self.tree.heading("type", text=self.t("col_type"))
        self.tree.column("name", width=220, minwidth=110, stretch=True, anchor="w")
        self.tree.column("size", width=92, minwidth=80, stretch=False, anchor="e")
        self.tree.column("compressed", width=92, minwidth=80, stretch=False, anchor="e")
        self.tree.column("type", width=64, minwidth=52, stretch=False, anchor="center")

        yscroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select_entry)
        self.tree.bind("<Configure>", self._on_tree_resize)
        self.tree.bind("<Button-3>", self._on_tree_right_click)

        right_frame = tk.Frame(self.paned, bg=BG_PANEL)
        self.paned.add(right_frame, minsize=240)
        self.paned.bind("<Configure>", self._balance_paned)

        preview_hdr = tk.Frame(right_frame, bg=BG_CARD, height=32)
        preview_hdr.pack(fill="x")
        preview_hdr.pack_propagate(False)
        self.preview_title = tk.Label(
            preview_hdr,
            text=self.t("quick_look"),
            bg=BG_CARD,
            fg=FG_TEXT,
            font=("Segoe UI Semibold", 9),
        )
        self.preview_title.pack(side="left", padx=10, pady=5)

        self.preview_container = tk.Frame(right_frame, bg=BG_PANEL)
        self.preview_container.pack(fill="both", expand=True)

        self.preview_image_label = tk.Label(self.preview_container, bg=BG_PANEL)
        self.preview_text = tk.Text(
            self.preview_container,
            bg=BG_PANEL,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief="flat",
            wrap="word",
            font=("Consolas", 9),
            padx=10,
            pady=10,
        )
        self._show_text_preview(self.t("welcome_text"))

        # Footer Status Bar
        footer = tk.Frame(self, bg=BG_PANEL, height=30, highlightthickness=1, highlightbackground=BORDER_COLOR)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            textvariable=self.status_var,
            bg=BG_PANEL,
            fg=FG_MUTED,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=14)

        self.footer_brand = tk.Label(
            footer,
            text=self.t("footer_brand"),
            bg=BG_PANEL,
            fg=LINK_BLUE,
            font=("Segoe UI Semibold", 8),
            cursor="hand2",
        )
        self.footer_brand.pack(side="right", padx=14)
        self.footer_brand.bind("<Button-1>", lambda _e: webbrowser.open(f"https://www.kasuality.com/{self.lang}/"))

    def _balance_paned(self, event=None) -> None:
        if not self._sash_initialized and event and event.width > 200:
            self._sash_initialized = True
            self.paned.sash_place(0, int(event.width * 0.52), 0)

    def _on_tree_resize(self, event=None) -> None:
        if not event or event.width < 260:
            return
        avail = event.width - 4
        size_w = 92
        comp_w = 92
        type_w = 64
        name_w = max(110, avail - size_w - comp_w - type_w)
        self.tree.column("name", width=name_w)
        self.tree.column("size", width=size_w)
        self.tree.column("compressed", width=comp_w)
        self.tree.column("type", width=type_w)

    def set_language(self, lang_code: str) -> None:
        if lang_code not in SUPPORTED_LANGS:
            return
        self.lang = lang_code
        self.lang_btn.configure(text=f" {self.lang.upper()} ▾")
        self.title(self.t("app_title"))
        self.btn_open.configure(text=f" {self.t('btn_open')}")
        self.btn_new.configure(text=f" {self.t('btn_new')}")
        self.btn_extract.configure(text=f" {self.t('btn_extract')}")
        self.btn_security.configure(text=f" {self.t('btn_security')}")
        self.btn_sha.configure(text=f" {self.t('btn_sha')}")
        self.rb_name.configure(text=self.t("mode_filename"))
        self.rb_content.configure(text=self.t("mode_content"))
        self.btn_search.configure(text=f" {self.t('btn_search')}")
        self.tree.heading("name", text=self.t("col_path"))
        self.tree.heading("size", text=self.t("col_size"))
        self.tree.heading("compressed", text=self.t("col_comp"))
        self.tree.heading("type", text=self.t("col_type"))
        self.footer_brand.configure(text=self.t("footer_brand"))
        if self.security_report:
            self._update_security_badge(self.security_report)
        else:
            self.security_badge.configure(text=self.t("no_archive"))
            self.preview_title.configure(text=self.t("quick_look"))
            self._show_text_preview(self.t("welcome_text"))
            self.status_var.set(self.t("ready_status"))

    def on_open_archive(self) -> None:
        file_path = filedialog.askopenfilename(
            title=self.t("app_title"),
            filetypes=[
                ("Supported archives", "*.zip *.7z *.tar *.gz *.tgz *.bz2 *.xz *.zst *.tzst"),
                ("ZIP", "*.zip"),
                ("7-Zip", "*.7z"),
                ("Zstandard", "*.zst *.tar.zst *.tzst"),
                ("TAR / GZ / XZ", "*.tar *.tar.gz *.tgz *.tar.bz2 *.tar.xz"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.load_archive(Path(file_path))

    def load_archive(self, path: Path) -> None:
        try:
            self.entries = list_entries(path)
            self.security_report = scan_archive(path)
            self.current_archive = path
        except ValueError:
            if path.is_file() and messagebox.askyesno(
                self.t("new_title"),
                self.t("not_archive_prompt", name=path.name),
            ):
                self._open_create_dialog([path], path.stem, path.parent)
            return
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._populate_tree(self.entries)
        self._update_security_badge(self.security_report)
        total_size = format_bytes(sum(e.size for e in self.entries))
        self.status_var.set(f"{path.name} — {len(self.entries)} items ({total_size})")

    def _populate_tree(self, entries: list[ArchiveEntry]) -> None:
        self.tree.delete(*self.tree.get_children())
        for entry in entries:
            kind = self.t("folder") if entry.is_dir else (Path(entry.name).suffix.lower() or self.t("file"))
            size_str = "-" if entry.is_dir else format_bytes(entry.size)
            comp_str = "-" if (entry.is_dir or entry.compressed_size == 0) else format_bytes(entry.compressed_size)
            self.tree.insert("", "end", values=(entry.name, size_str, comp_str, kind))

    def _update_security_badge(self, report: SecurityReport) -> None:
        if report.status == "SAFE":
            self.security_badge.configure(
                text=self.t("badge_safe", n=report.total_entries),
                bg=SAFE_BG,
                fg=SAFE_FG,
                highlightbackground="#34D399",
            )
        elif report.status == "WARNING":
            self.security_badge.configure(
                text=self.t("badge_warn", n=len(report.findings)),
                bg=WARN_BG,
                fg=WARN_FG,
                highlightbackground="#F59E0B",
            )
        else:
            self.security_badge.configure(
                text=self.t("badge_danger", n=len(report.findings)),
                bg=DANGER_BG,
                fg=DANGER_FG,
                highlightbackground="#EF4444",
            )

    def on_select_entry(self, _event=None) -> None:
        if not self.current_archive:
            return
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if not values:
            return
        entry_name = values[0]
        entry = next((e for e in self.entries if e.name == entry_name), None)
        if not entry or entry.is_dir:
            return

        ext = Path(entry_name.lower()).suffix
        self.preview_title.configure(text=f"Quick Look: {entry_name}")

        if ext in IMAGE_EXTENSIONS:
            try:
                raw = read_entry_bytes(self.current_archive, entry_name)
                img = Image.open(io.BytesIO(raw))
                img.thumbnail((400, 400))
                self.preview_photo = ImageTk.PhotoImage(img)
                self.preview_text.pack_forget()
                self.preview_image_label.configure(image=self.preview_photo, text="")
                self.preview_image_label.pack(fill="both", expand=True, padx=12, pady=12)
                return
            except Exception as exc:
                self._show_text_preview(f"Preview error: {exc}")
                return

        if ext in TEXT_EXTENSIONS or entry.size < 256 * 1024:
            try:
                raw = read_entry_bytes(self.current_archive, entry_name)
                if b"\x00" in raw[:1024]:
                    self._show_text_preview(self.t("binary_preview", size=format_bytes(entry.size)))
                    return
                text = raw.decode("utf-8", errors="replace")
                self._show_text_preview(text)
            except Exception as exc:
                self._show_text_preview(f"Preview error: {exc}")
        else:
            self._show_text_preview(self.t("non_text_preview", name=entry_name, size=format_bytes(entry.size)))

    def _show_text_preview(self, content: str) -> None:
        self.preview_image_label.pack_forget()
        self.preview_text.pack(fill="both", expand=True)
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", content)
        self.preview_text.configure(state="disabled")

    def on_search(self) -> None:
        if not self.current_archive:
            return
        query = self.search_var.get().strip()
        if not query:
            self._populate_tree(self.entries)
            self.status_var.set(f"{self.current_archive.name} — {len(self.entries)} items")
            return

        mode = self.search_mode_var.get()
        if mode == "filename":
            filtered = [e for e in self.entries if query.lower() in e.name.lower()]
            self._populate_tree(filtered)
            self.status_var.set(f"Filter '{query}': {len(filtered)} results")
        else:
            matches = search_in_archive(self.current_archive, query)
            matched_names = {m.entry_name for m in matches}
            filtered = [e for e in self.entries if e.name in matched_names]
            self._populate_tree(filtered)
            summary = "\n".join(
                f"{m.entry_name}:{m.line_number} -> {m.line_preview}" for m in matches
            ) or "No matches found."
            self.preview_title.configure(text=f"Full-Text '{query}' ({len(matches)})")
            self._show_text_preview(summary)
            self.status_var.set(f"Full-Text '{query}': {len(matches)} matches in {len(filtered)} files")

    def _get_selected_entry_names(self) -> list[str]:
        names: list[str] = []
        for item_id in self.tree.selection():
            vals = self.tree.item(item_id, "values")
            if vals:
                names.append(vals[0])
        return names

    def _on_tree_right_click(self, event) -> None:
        row_id = self.tree.identify_row(event.y)
        if row_id and row_id not in self.tree.selection():
            self.tree.selection_set(row_id)
        selected = self._get_selected_entry_names()
        if not selected:
            return
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=BG_CARD,
            fg=FG_TEXT,
            activebackground=ACCENT,
            activeforeground="#FFFFFF",
            font=("Segoe UI Semibold", 9),
        )
        menu.add_command(
            label=self.t("ctx_extract_selected"),
            command=lambda: self._run_extract(selected),
        )
        menu.tk_popup(event.x_root, event.y_root)

    def on_extract_archive(self) -> None:
        if not self.current_archive:
            messagebox.showinfo(self.t("app_title"), self.t("no_archive"))
            return

        selected = self._get_selected_entry_names()
        targets: list[str] | None = None
        if selected and len(selected) < len(self.entries):
            choice = messagebox.askyesnocancel(
                self.t("btn_extract"),
                self.t("extract_selected_prompt", n=len(selected)),
            )
            if choice is None:
                return
            if choice is True:
                targets = selected

        self._run_extract(targets)

    def _run_extract(self, selected_targets: list[str] | None) -> None:
        if not self.current_archive:
            return

        if self.security_report and self.security_report.status == "DANGER":
            proceed = messagebox.askyesno(
                "Security Alert",
                "This archive contains dangerous entries (path traversal or double extension).\n"
                "Safe Extract will block any path traversal attempt.\n\nContinue?",
            )
            if not proceed:
                return

        dest = filedialog.askdirectory(title=self.t("btn_extract"))
        if not dest:
            return

        target_dir = Path(dest) / self.current_archive.stem.replace(".tar", "")
        self.status_var.set("Extracting...")

        def worker() -> None:
            try:
                count = safe_extract(
                    self.current_archive,
                    target_dir,
                    selected_entries=selected_targets,
                )
                self.after(0, lambda: self._on_extract_done(target_dir, count))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Error", str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_extract_done(self, target_dir: Path, count: int) -> None:
        self.status_var.set(f"{count} -> {target_dir}")
        messagebox.showinfo(self.t("btn_extract"), self.t("extract_done", count=count, path=target_dir))

    def on_show_security_report(self) -> None:
        if not self.security_report or not self.current_archive:
            messagebox.showinfo(self.t("btn_security"), self.t("no_archive"))
            return
        rep = self.security_report
        if not rep.findings:
            messagebox.showinfo(
                self.t("btn_security"),
                f"{self.current_archive.name}\nEntries: {rep.total_entries}\nStatus: SAFE",
            )
            return
        details = "\n".join(f"[{f.level}] {f.entry}\n  -> {f.reason}" for f in rep.findings[:25])
        messagebox.showwarning(f"{self.t('btn_security')} — {rep.status}", details)

    def on_show_help(self) -> None:
        win = tk.Toplevel(self)
        win.title(self.t("help_title"))
        win.geometry("620x520")
        win.configure(bg=BG_PANEL)
        win.transient(self)
        win.grab_set()

        txt = tk.Text(
            win,
            bg=BG_PANEL,
            fg=FG_TEXT,
            relief="flat",
            wrap="word",
            font=("Segoe UI", 10),
            padx=18,
            pady=16,
        )
        txt.insert("1.0", self.t("help_body"))
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True)

        bottom = tk.Frame(win, bg=BG_CARD, height=48)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)
        self._make_btn(bottom, self.t("close_btn"), win.destroy, primary=True).pack(side="right", padx=14, pady=8)

    def on_show_sha256(self) -> None:
        if not self.current_archive:
            messagebox.showinfo(self.t("btn_sha"), self.t("no_archive"))
            return
        digest = compute_sha256(self.current_archive)
        self.clipboard_clear()
        self.clipboard_append(digest)
        messagebox.showinfo(
            "SHA-256",
            self.t("sha_copied", name=self.current_archive.name, sha=digest),
        )

    def on_new_archive(self) -> None:
        folder = filedialog.askdirectory(title=self.t("btn_new"))
        if not folder:
            return
        src_path = Path(folder)
        self._open_create_dialog([src_path], src_path.name, src_path.parent)

    def _open_create_dialog(self, sources: list[Path], default_name: str, initial_dir: Path) -> None:
        dialog = tk.Toplevel(self)
        dialog.title(self.t("new_title"))
        dialog.geometry("460x300")
        dialog.configure(bg=BG_PANEL)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=self.t("source_label", name=sources[0].name),
            bg=BG_PANEL,
            fg=FG_TEXT,
            font=("Segoe UI Bold", 10),
        ).pack(anchor="w", padx=18, pady=(16, 8))

        fmt_var = tk.StringVar(value="zip")
        tk.Label(dialog, text=self.t("format_label"), bg=BG_PANEL, fg=FG_MUTED).pack(anchor="w", padx=18)
        fmt_combo = ttk.Combobox(dialog, textvariable=fmt_var, values=SUPPORTED_CREATE_FORMATS, state="readonly")
        fmt_combo.pack(fill="x", padx=18, pady=(4, 12))

        smart_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            dialog,
            text=self.t("smart_dev_label"),
            variable=smart_var,
            bg=BG_PANEL,
            fg=FG_TEXT,
            selectcolor=BG_CARD,
            activebackground=BG_PANEL,
            activeforeground=FG_TEXT,
            wraplength=410,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        level_var = tk.IntVar(value=6)
        tk.Label(dialog, text=self.t("level_label"), bg=BG_PANEL, fg=FG_MUTED).pack(anchor="w", padx=18)
        tk.Scale(
            dialog,
            from_=1,
            to=9,
            orient="horizontal",
            variable=level_var,
            bg=BG_PANEL,
            fg=FG_TEXT,
            troughcolor=BG_CARD,
            highlightthickness=0,
        ).pack(fill="x", padx=18, pady=(2, 16))

        def start_create() -> None:
            fmt = fmt_var.get()
            ext = f".{fmt}"
            out_file = filedialog.asksaveasfilename(
                title=self.t("btn_create"),
                initialdir=str(initial_dir),
                initialfile=f"{default_name}{ext}",
                defaultextension=ext,
            )
            if not out_file:
                return
            dialog.destroy()
            self.status_var.set("Compressing...")

            def worker() -> None:
                try:
                    out_p, sha, count = create_archive(
                        sources,
                        out_file,
                        fmt=fmt,
                        smart_dev_exclude=smart_var.get(),
                        compression_level=level_var.get(),
                    )
                    self.after(0, lambda: self._on_create_done(out_p, sha, count))
                except Exception as exc:
                    self.after(0, lambda: messagebox.showerror("Error", str(exc)))

            threading.Thread(target=worker, daemon=True).start()

        self._make_btn(dialog, self.t("btn_create"), start_create, primary=True).pack(pady=6)

    def _on_create_done(self, out_path: Path, sha256: str, count: int) -> None:
        self.load_archive(out_path)
        messagebox.showinfo(
            self.t("new_title"),
            self.t(
                "created_msg",
                name=out_path.name,
                count=count,
                size=format_bytes(out_path.stat().st_size),
                sha=sha256,
            ),
        )


def main() -> None:
    initial = sys.argv[1] if len(sys.argv) > 1 else None
    app = KasualityArchiverApp(initial_file=initial)
    app.mainloop()


if __name__ == "__main__":
    main()
