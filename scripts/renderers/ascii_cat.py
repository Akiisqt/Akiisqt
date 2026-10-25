"""
ASCII Cat Box Renderer.
Renders dedicated glass container with glowing animated cyber-red ASCII cat.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import ASCII_CAT
from scripts.fonts import load_system_font
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


class AsciiCatRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str = "cat",
        ascii_lines: Optional[List[str]] = None,
        font_cat: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.ascii_lines = ascii_lines or ASCII_CAT
        self.font_cat = font_cat or load_system_font(12, bold=True)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, (244, 63, 94)
        )
        cat_glow = int(210 + 45 * math.sin(frame.glow_phase))
        cat_color = (cat_glow, 45, 70, 245)
        for idx, line in enumerate(self.ascii_lines):
            draw.text(
                (self.x + 12, self.y + 12 + idx * 13),
                line,
                font=self.font_cat,
                fill=cat_color,
            )

