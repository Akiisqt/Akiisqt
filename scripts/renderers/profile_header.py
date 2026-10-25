"""
Profile Header Renderer.
Renders profile title with morphing star icons and scrolling tagline.
"""

from __future__ import annotations

from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import COLOR_EVA_PURPLE, COLOR_TEXT_WHITE
from scripts.fonts import load_system_font, scroll_text
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer


class ProfileHeaderRenderer(BaseRenderer):
    def __init__(
        self,
        cx: int,
        cy: int,
        p_name: str,
        p_tagline: str,
        star_morph_glyphs: Optional[List[str]] = None,
        font_huge: Any = None,
        font_body: Any = None,
    ) -> None:
        self.cx = cx
        self.cy = cy
        self.p_name = p_name
        self.p_tagline = p_tagline
        self.star_morph_glyphs = star_morph_glyphs or ["✦", "✧", "+", "★"]
        self.font_huge = font_huge or load_system_font(24, bold=True)
        self.font_body = font_body or load_system_font(12, bold=False)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        glyph_count = len(self.star_morph_glyphs)
        header_star = (
            self.star_morph_glyphs[int((frame.t * glyph_count) % glyph_count)]
            if glyph_count > 0
            else "✦"
        )
        draw.text(
            (self.cx, self.cy),
            f"{header_star} {self.p_name} {header_star}",
            font=self.font_huge,
            fill=COLOR_TEXT_WHITE,
        )
        safe_tagline = scroll_text(draw, self.p_tagline, self.font_body, 255, frame.t)
        draw.text((self.cx, self.cy + 32), safe_tagline, font=self.font_body, fill=COLOR_EVA_PURPLE)

