"""
Floating Triangles Renderer.
Renders upward-drifting / oscillating geometric osu! triangles.
"""

from __future__ import annotations

import math
from typing import List, Optional

from PIL import ImageDraw

from scripts.config import HEIGHT, WIDTH
from scripts.models import FrameContext, OsuTriangle, build_osu_triangles
from scripts.renderers.base import BaseRenderer


class TrianglesRenderer(BaseRenderer):
    def __init__(self, triangles: Optional[List[OsuTriangle]] = None) -> None:
        self.triangles = triangles if triangles is not None else build_osu_triangles()

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        for tri in self.triangles:
            cur_y = (tri.y - tri.amp * math.sin(2.0 * math.pi * tri.freq * frame.t + tri.phase)) % HEIGHT
            cur_x = (tri.x + (tri.amp * 0.4) * math.cos(2.0 * math.pi * tri.freq * frame.t + tri.phase)) % WIDTH
            r = tri.size
            p1 = (cur_x, cur_y - r)
            p2 = (cur_x + int(r * 0.866), cur_y + int(r * 0.5))
            p3 = (cur_x - int(r * 0.866), cur_y + int(r * 0.5))
            draw.polygon([p1, p2, p3], fill=(*tri.color, tri.opacity))

