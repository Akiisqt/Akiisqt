"""
Typography and text rendering helpers with guaranteed glyph support.
"""

from __future__ import annotations

import math
import os
from typing import Any, List

from PIL import ImageDraw, ImageFont


def load_system_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend([
            "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Bold.ttf",
            "/usr/share/fonts/source-foundry-hack-fonts/Hack-Bold.ttf",
            "/usr/share/fonts/liberation-mono-fonts/LiberationMono-Bold.ttf",
            "/usr/share/fonts/google-noto/NotoSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        ])
    else:
        candidates.extend([
            "/usr/share/fonts/adwaita-mono-fonts/AdwaitaMono-Regular.ttf",
            "/usr/share/fonts/source-foundry-hack-fonts/Hack-Regular.ttf",
            "/usr/share/fonts/liberation-mono-fonts/LiberationMono-Regular.ttf",
            "/usr/share/fonts/google-noto/NotoSansMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ])

    for path in candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                if font.getmask("✦").size != (0, 0):
                    return font
            except OSError:
                continue

    return ImageFont.load_default()


def fit_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> str:
    if draw.textlength(text, font=font) <= max_width:
        return text

    ellipsis = "..."
    ellipsis_w = draw.textlength(ellipsis, font=font)
    avail = max_width - ellipsis_w
    if avail <= 0:
        return ellipsis

    for i in range(len(text), 0, -1):
        candidate = text[:i]
        if draw.textlength(candidate, font=font) <= avail:
            return candidate.rstrip() + ellipsis
    return ellipsis


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> List[str]:
    """Wraps text cleanly across multiple lines without exceeding max_width."""
    words = text.split()
    lines: List[str] = []
    curr: List[str] = []
    for w in words:
        test = " ".join(curr + [w])
        if draw.textlength(test, font=font) <= max_width:
            curr.append(w)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    return lines


def glyph_supported(font: Any, char: str) -> bool:
    """Returns True if the font can render this character (non-empty mask)."""
    try:
        return font.getmask(char).size != (0, 0)
    except Exception:
        return False


def text_renderable(font: Any, text: str) -> bool:
    """True if every non-space character in text is supported by font."""
    return all(glyph_supported(font, ch) for ch in text if not ch.isspace())


def clip_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> str:
    """Hard-clips text to fit within max_width with no ellipsis added."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    for i in range(len(text), 0, -1):
        if draw.textlength(text[:i], font=font) <= max_width:
            return text[:i]
    return ""


def scroll_text(
    draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int, anim_t: float
) -> str:
    """Returns a scrolling window into text when it overflows max_width.
    Loops seamlessly over one full animation cycle (anim_t 0.0 → 1.0).
    If text fits, returns it unchanged."""
    if draw.textlength(text, font=font) <= max_width:
        return text

    sep = "   "
    marquee = text + sep
    marquee_w = draw.textlength(marquee, font=font)
    if marquee_w <= 0:
        return text

    px_off = marquee_w * anim_t

    char_off = 0
    for i in range(1, len(marquee) + 1):
        if draw.textlength(marquee[:i], font=font) > px_off:
            char_off = i - 1
            break

    visible = (marquee + text)[char_off:]
    return clip_text(draw, visible, font, max_width)


def twinkle(freq: float, anim_t: float, offset: float) -> float:
    """Smooth oscillating value in [0.0, 1.0] for sparkle/star effects."""
    return 0.5 + 0.5 * math.sin(2.0 * math.pi * freq * anim_t + offset)

