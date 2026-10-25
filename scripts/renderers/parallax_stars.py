"""
Parallax Stars Renderer.
Renders multi-layer depth drifting, twinkling stars.
"""

from __future__ import annotations

from typing import List, Optional

from PIL import ImageDraw

from scripts.config import HEIGHT, WIDTH
from scripts.fonts import twinkle
from scripts.models import ParallaxStar, build_parallax_stars
from scripts.renderers.base import BaseRenderer
from scripts.models import FrameContext


class ParallaxStarsRenderer(BaseRenderer):
    def __init__(self, stars: Optional[List[ParallaxStar]] = None) -> None:
        self.stars = stars if stars is not None else build_parallax_stars()

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        for star in self.stars:
            sx = (star.x + star.vx * frame.frame_idx) % WIDTH
            sy = (star.y + star.vy * frame.frame_idx) % HEIGHT
            tw_val = twinkle(star.twinkle_freq, frame.t, star.twinkle_offset)
            bright = int(star.brightness * tw_val)
            sr = star.radius
            draw.ellipse(
                [sx - sr, sy - sr, sx + sr, sy + sr],
                fill=(bright, bright, min(255, int(bright * 1.1)), 240),
            )

