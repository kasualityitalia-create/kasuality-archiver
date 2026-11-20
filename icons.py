"""Crisp vector-style (SVG-like) icons rendered via Pillow supersampling."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageTk


def _new_canvas(size: int, scale: int = 4) -> tuple[Image.Image, ImageDraw.ImageDraw, int]:
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw, scale


def _finish(img: Image.Image, size: int) -> ImageTk.PhotoImage:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized)


def render_brand_pil(size: int = 256) -> Image.Image:
    scale = 4
    s = (size * scale) / 256.0
    img = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def r(val: float) -> int:
        return max(1, int(round(val * s)))

    # 3 stacked compressed layers (Indigo, Electric Blue, Emerald)
    d.rounded_rectangle([r(24), r(34), r(232), r(88)], radius=r(16), fill="#4F46E5", outline="#C7D2FE", width=r(4))
    d.rounded_rectangle([r(24), r(101), r(232), r(155)], radius=r(16), fill="#2563EB", outline="#BFDBFE", width=r(4))
    d.rounded_rectangle([r(24), r(168), r(232), r(222)], radius=r(16), fill="#059669", outline="#A7F3D0", width=r(4))

    # Spine highlights
    d.rounded_rectangle([r(40), r(48), r(52), r(74)], radius=r(5), fill="#E0E7FF")
    d.rounded_rectangle([r(40), r(115), r(52), r(141)], radius=r(5), fill="#DBEAFE")
    d.rounded_rectangle([r(40), r(182), r(52), r(208)], radius=r(5), fill="#D1FAE5")

    # Central compression strap + buckle clasp + K monogram
    d.rounded_rectangle([r(92), r(22), r(164), r(234)], radius=r(14), fill="#0F172A", outline="#93C5FD", width=r(5))
    d.rounded_rectangle([r(82), r(82), r(174), r(174)], radius=r(18), fill="#0F172A", outline="#F8FAFC", width=r(6))
    d.line([r(108), r(104), r(108), r(152)], fill="#93C5FD", width=r(12))
    d.line([r(108), r(128), r(146), r(104)], fill="#93C5FD", width=r(12))
    d.line([r(108), r(128), r(146), r(152)], fill="#93C5FD", width=r(12))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def make_brand_icon(size: int = 24, color: str = "#93C5FD", accent: str = "#1D4ED8") -> ImageTk.PhotoImage:
    return ImageTk.PhotoImage(render_brand_pil(size))


def make_folder_icon(size: int = 16, color: str = "#F8FAFC") -> ImageTk.PhotoImage:
    img, d, s = _new_canvas(size)
    d.polygon([1 * s, 3 * s, 6 * s, 3 * s, 8 * s, 5 * s, 15 * s, 5 * s, 15 * s, 13 * s, 1 * s, 13 * s], outline=color, width=2 * s)
    return _finish(img, size)


def make_plus_box_icon(size: int = 16, color: str = "#F8FAFC") -> ImageTk.PhotoImage:
    img, d, s = _new_canvas(size)
    d.rounded_rectangle([2 * s, 2 * s, 14 * s, 14 * s], radius=2 * s, outline=color, width=2 * s)
    d.line([8 * s, 5 * s, 8 * s, 11 * s], fill=color, width=2 * s)
    d.line([5 * s, 8 * s, 11 * s, 8 * s], fill=color, width=2 * s)
    return _finish(img, size)


def make_extract_icon(size: int = 16, color: str = "#F8FAFC") -> ImageTk.PhotoImage:
    img, d, s = _new_canvas(size)
    d.line([8 * s, 2 * s, 8 * s, 10 * s], fill=color, width=2 * s)
    d.line([5 * s, 7 * s, 8 * s, 10 * s, 11 * s, 7 * s], fill=color, width=2 * s)
    d.line([2 * s, 11 * s, 2 * s, 14 * s, 14 * s, 14 * s, 14 * s, 11 * s], fill=color, width=2 * s)
    return _finish(img, size)


def make_shield_icon(size: int = 16, color: str = "#F8FAFC") -> ImageTk.PhotoImage:
    img, d, s = _new_canvas(size)
    d.polygon([8 * s, 1 * s, 14 * s, 3 * s, 13 * s, 10 * s, 8 * s, 14 * s, 3 * s, 10 * s, 2 * s, 3 * s], outline=color, width=2 * s)
    d.line([5 * s, 8 * s, 7 * s, 10 * s, 11 * s, 6 * s], fill=color, width=2 * s)
    return _finish(img, size)


def make_hash_icon(size: int = 16, color: str = "#F8FAFC") -> ImageTk.PhotoImage:
    img, d, s = _new_canvas(size)
    d.line([5 * s, 2 * s, 4 * s, 14 * s], fill=color, width=2 * s)
    d.line([11 * s, 2 * s, 10 * s, 14 * s], fill=color, width=2 * s)
    d.line([2 * s, 6 * s, 14 * s, 6 * s], fill=color, width=2 * s)
    d.line([2 * s, 10 * s, 14 * s, 10 * s], fill=color, width=2 * s)
    return _finish(img, size)


def make_search_icon(size: int = 16, color: str = "#F8FAFC") -> ImageTk.PhotoImage:
    img, d, s = _new_canvas(size)
    d.ellipse([2 * s, 2 * s, 11 * s, 11 * s], outline=color, width=2 * s)
    d.line([10 * s, 10 * s, 14 * s, 14 * s], fill=color, width=2 * s)
    return _finish(img, size)


def make_globe_icon(size: int = 16, color: str = "#93C5FD") -> ImageTk.PhotoImage:
    img, d, s = _new_canvas(size)
    d.ellipse([2 * s, 2 * s, 14 * s, 14 * s], outline=color, width=2 * s)
    d.ellipse([5 * s, 2 * s, 11 * s, 14 * s], outline=color, width=1 * s)
    d.line([2 * s, 8 * s, 14 * s, 8 * s], fill=color, width=1 * s)
    return _finish(img, size)
