"""
Shooting Stars Renderer.
Renders diagonal shooting star streaks with fading trails.
"""

from __future__ import annotations

from typing import List, Optional

from PIL import ImageDraw

from scripts.config import HEIGHT, WIDTH
from scripts.models import FrameContext, ShootingStar, build_shooting_stars
from scripts.renderers.base import BaseRenderer


class ShootingStarsRenderer(BaseRenderer):
    def __init__(self, stars: Optional[List[ShootingStar]] = None) -> None:
        self.stars = stars if stars is not None else build_shooting_stars()

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        for ss in self.stars:
            cycle_t = (frame.t * ss.speed) % 1.0
            head_x = ss.start_x + (ss.dx * WIDTH) * cycle_t
            head_y = ss.start_y + (ss.dy * HEIGHT) * cycle_t
            steps = 14
            for seg in range(steps):
                alpha = 1.0 - (seg / steps)
                seg_x = head_x - (ss.dx * ss.length * (seg / steps))
                seg_y = head_y - (ss.dy * ss.length * (seg / steps))
                if 0 <= seg_x <= WIDTH and 0 <= seg_y <= HEIGHT:
                    r = int(ss.color[0] * alpha)
                    g = int(ss.color[1] * alpha)
                    b = int(ss.color[2] * alpha)
                    w = 2 if seg < 4 else 1
                    draw.line(
                        [(seg_x, seg_y), (seg_x + 1, seg_y + 1)],
                        fill=(r, g, b, int(255 * alpha)),
                        width=w,
                    )

