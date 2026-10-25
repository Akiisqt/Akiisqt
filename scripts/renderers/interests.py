"""
Interests & Vibes Box Renderer.
Renders symmetric 2-column grid of pill tags with morphing star icons.
"""

from __future__ import annotations

from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import COLOR_OSU_PINK, COLOR_PILL_BG, COLOR_PILL_BORDER, COLOR_TEXT_PINK
from scripts.fonts import load_system_font, scroll_text
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


class InterestsRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int = 360,
        h: int = 115,
        title: str = "interests",
        interests: Optional[List[str]] = None,
        star_morph_glyphs: Optional[List[str]] = None,
        font_small: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.interests = interests or []
        self.star_morph_glyphs = star_morph_glyphs or ["✦", "✧", "+", "★"]
        self.font_small = font_small or load_system_font(10, bold=False)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_OSU_PINK
        )

        num_interests = len(self.interests)
        if num_interests == 0:
            return

        cols = 2
        rows = (num_interests + cols - 1) // cols
        pad_x = 14
        pad_top = 18
        pad_bot = 14
        avail_w = self.w - 2 * pad_x
        avail_h = self.h - pad_top - pad_bot
        row_h = 24
        row_gap = (avail_h - rows * row_h) // max(1, rows - 1) if rows > 1 else 0
        col_gap = 10
        col_w = (avail_w - (cols - 1) * col_gap) // cols
        glyph_count = len(self.star_morph_glyphs)

        for p_idx, it in enumerate(self.interests):
            r = p_idx // cols
            c = p_idx % cols
            px = self.x + pad_x + c * (col_w + col_gap)
            py = self.y + pad_top + r * (row_h + row_gap)

            pill_star_idx = int((frame.t * 5 + p_idx * 1.6) % glyph_count) if glyph_count > 0 else 0
            pop_star = self.star_morph_glyphs[pill_star_idx] if glyph_count > 0 else "✦"
            ptxt = f"{pop_star} {it}"

            draw.rectangle(
                [px, py, px + col_w, py + row_h],
                fill=COLOR_PILL_BG,
                outline=COLOR_PILL_BORDER,
                width=1,
            )
            safe_ptxt = scroll_text(draw, ptxt, self.font_small, col_w - 12, frame.t)
            tw = draw.textlength(safe_ptxt, font=self.font_small)
            tx = px + int((col_w - tw) / 2)
            draw.text((tx, py + 5), safe_ptxt, font=self.font_small, fill=COLOR_TEXT_PINK)

