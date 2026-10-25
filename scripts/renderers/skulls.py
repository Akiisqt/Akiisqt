"""
Floating Skulls Renderer.
Renders ethereal cyber-skeleton skulls drifting in the void.
"""

from __future__ import annotations

from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import HEIGHT, WIDTH
from scripts.fonts import load_system_font, twinkle
from scripts.models import FloatingSkeletonSkull, FrameContext, build_floating_skulls
from scripts.renderers.base import BaseRenderer


class FloatingSkullsRenderer(BaseRenderer):
    def __init__(
        self,
        floating_skulls: Optional[List[FloatingSkeletonSkull]] = None,
        font_bold: Any = None,
    ) -> None:
        self.font_bold = font_bold or load_system_font(12, bold=True)
        self.floating_skulls = (
            floating_skulls if floating_skulls is not None else build_floating_skulls(self.font_bold)
        )

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        for sk in self.floating_skulls:
            sk_y = (sk.y + sk.vy * frame.frame_idx) % HEIGHT
            sk_x = sk.x % WIDTH
            tw_val = twinkle(sk.freq, frame.t, sk.offset)
            sk_alpha = int(sk.alpha * (0.2 + 0.8 * tw_val))
            draw.text((int(sk_x), int(sk_y)), sk.glyph, font=self.font_bold, fill=(240, 240, 255, sk_alpha))

