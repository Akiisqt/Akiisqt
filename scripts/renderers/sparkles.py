"""
Sparkles Renderer.
Renders floating star sparkles that dynamically pop/morph between star glyphs.
"""

from __future__ import annotations

from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import HEIGHT, WIDTH
from scripts.fonts import load_system_font, twinkle
from scripts.models import FrameContext, OsuSparkle, build_osu_sparkles
from scripts.renderers.base import BaseRenderer


class SparklesRenderer(BaseRenderer):
    def __init__(
        self,
        sparkles: Optional[List[OsuSparkle]] = None,
        star_morph_glyphs: Optional[List[str]] = None,
        font_small: Any = None,
    ) -> None:
        self.sparkles = sparkles if sparkles is not None else build_osu_sparkles()
        self.star_morph_glyphs = star_morph_glyphs or ["✦", "✧", "+", "★"]
        self.font_small = font_small or load_system_font(10, bold=False)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        glyph_count = len(self.star_morph_glyphs)
        if glyph_count == 0:
            return

        for sp in self.sparkles:
            sy = (sp.y + sp.vy * frame.frame_idx) % HEIGHT
            sx = sp.x % WIDTH
            tw_val = twinkle(sp.freq, frame.t, sp.offset)
            alpha = int(190 * tw_val)
            morph_idx = int((frame.t * sp.freq * glyph_count + sp.offset) % glyph_count)
            cur_star = self.star_morph_glyphs[morph_idx]
            draw.text((int(sx), int(sy)), cur_star, font=self.font_small, fill=(255, 255, 255, alpha))

