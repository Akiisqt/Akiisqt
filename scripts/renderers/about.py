"""
About Me Box Renderer.
Renders bio bullet lines cleanly wrapped inside a glass container.
"""

from __future__ import annotations

from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import COLOR_OSU_BLUE, COLOR_TEXT_WHITE
from scripts.fonts import load_system_font, wrap_text
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


class AboutRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int = 360,
        h: int = 145,
        title: str = "about",
        about_lines: Optional[List[str]] = None,
        font_body: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.about_lines = about_lines or []
        self.font_body = font_body or load_system_font(12, bold=False)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_OSU_BLUE
        )
        line_offset = self.y + 16
        for bullet in self.about_lines:
            wrapped_sublines = wrap_text(draw, bullet, self.font_body, self.w - 30)
            for s_idx, s_line in enumerate(wrapped_sublines):
                prefix = "» " if s_idx == 0 else "  "
                draw.text(
                    (self.x + 12, line_offset),
                    f"{prefix}{s_line}",
                    font=self.font_body,
                    fill=COLOR_TEXT_WHITE,
                )
                line_offset += 15
            line_offset += 2

