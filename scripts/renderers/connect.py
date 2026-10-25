"""
Connect Box Renderer.
Renders social and connection badges in a 2-column grid.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from PIL import ImageDraw

from scripts.config import COLOR_OSU_BLUE
from scripts.fonts import load_system_font, scroll_text
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


class ConnectRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int = 360,
        h: int = 116,
        title: str = "connect",
        badges: Optional[List[Tuple[str, Tuple[int, int, int]]]] = None,
        font_small: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.badges = badges or []
        self.font_small = font_small or load_system_font(10, bold=False)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_OSU_BLUE
        )
        b_col_w = 162
        for b_idx, (b_text, b_color) in enumerate(self.badges[:6]):
            b_col = b_idx % 2
            b_row = b_idx // 2
            bx = self.x + 12 + b_col * (b_col_w + 12)
            by = self.y + 16 + b_row * 30
            draw.rectangle(
                [bx, by, bx + b_col_w, by + 21],
                fill=(36, 24, 54, 200),
                outline=(85, 60, 120),
                width=1,
            )
            safe_b_text = scroll_text(draw, b_text, self.font_small, b_col_w - 14, frame.t)
            draw.text((bx + 8, by + 4), safe_b_text, font=self.font_small, fill=b_color)

