"""
Base renderer interface and core UI primitives (angled tabs, glass boxes).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Tuple

from PIL import ImageDraw

from scripts.config import COLOR_GLASS_BOX, COLOR_OSU_PINK
from scripts.models import FrameContext


class BaseRenderer(ABC):
    """Abstract base class for all profile card rendering components."""

    @abstractmethod
    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        """Render this component onto the given ImageDraw context for the specified frame."""
        pass


def draw_osu_angled_tab(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    font: Any,
    color: Tuple[int, int, int] = COLOR_OSU_PINK,
    skew: int = 8,
) -> None:
    poly = [
        (x + skew, y),
        (x + w, y),
        (x + w - skew, y + h),
        (x, y + h),
    ]
    draw.polygon(poly, fill=(*color, 235))
    text_w = draw.textlength(title, font=font)
    tx = x + (w - int(text_w)) // 2
    draw.text((tx, y + 2), title, font=font, fill=(10, 8, 16))


def draw_osu_glass_box(
    glass_draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    font_title: Any,
    accent_color: Tuple[int, int, int] = COLOR_OSU_PINK,
) -> None:
    # Base glass container
    glass_draw.rectangle([x, y, x + w, y + h], fill=COLOR_GLASS_BOX, outline=(*accent_color, 200), width=1)
    glass_draw.rectangle([x, y, x + 4, y + h], fill=(*accent_color, 240))

    # Cyberpunk / Ghost in the Shell HUD Corner Brackets
    c_len = 8
    # Top-right bracket
    glass_draw.line([(x + w - c_len, y), (x + w, y)], fill=(*accent_color, 255), width=2)
    glass_draw.line([(x + w, y), (x + w, y + c_len)], fill=(*accent_color, 255), width=2)
    # Bottom-left bracket
    glass_draw.line([(x, y + h - c_len), (x, y + h)], fill=(*accent_color, 255), width=2)
    glass_draw.line([(x, y + h), (x + c_len, y + h)], fill=(*accent_color, 255), width=2)
    # Bottom-right bracket
    glass_draw.line([(x + w - c_len, y + h), (x + w, y + h)], fill=(*accent_color, 255), width=2)
    glass_draw.line([(x + w, y + h - c_len), (x + w, y + h)], fill=(*accent_color, 255), width=2)

    # Angled header tab
    tab_w = int(glass_draw.textlength(title, font=font_title)) + 24
    draw_osu_angled_tab(glass_draw, x + 12, y - 9, tab_w, 18, title, font_title, color=accent_color)

