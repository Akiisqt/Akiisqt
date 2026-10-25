"""
Bottom Ledge Characters Renderer.
Renders mini ASCII characters sitting and standing on the bottom window ledge with bounce.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import BOTTOM_CHARACTERS
from scripts.fonts import load_system_font
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer


class BottomCharactersRenderer(BaseRenderer):
    def __init__(
        self,
        card_x: int,
        card_y: int,
        card_w: int,
        card_h: int,
        bottom_chars: Optional[List[List[str]]] = None,
        font_small: Any = None,
    ) -> None:
        self.card_x = card_x
        self.card_y = card_y
        self.card_w = card_w
        self.card_h = card_h
        self.bottom_chars = bottom_chars if bottom_chars is not None else BOTTOM_CHARACTERS
        self.font_small = font_small or load_system_font(10, bold=False)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        if not self.bottom_chars:
            return

        ledge_y = self.card_y + self.card_h - 14
        num_chars = len(self.bottom_chars)

        for c_idx, c_lines in enumerate(self.bottom_chars):
            slot_center = self.card_x + (c_idx + 0.5) * (self.card_w / num_chars)
            max_line_w = max(draw.textlength(line_str, font=self.font_small) for line_str in c_lines)
            cx_char = int(slot_center - max_line_w / 2)

            bounce = int(2 * math.sin(2 * math.pi * frame.t * 2 + c_idx * 1.2))
            c_alpha = int(210 + 45 * math.sin(frame.glow_phase + c_idx * 0.8))
            c_red = int(210 + 45 * math.sin(frame.glow_phase + c_idx * 0.6))
            c_color = (c_red, 45, 65)

            for l_idx, line_str in enumerate(c_lines):
                line_y = ledge_y - (len(c_lines) - 1 - l_idx) * 11 + bounce
                draw.text((cx_char, line_y), line_str, font=self.font_small, fill=(*c_color, c_alpha))

