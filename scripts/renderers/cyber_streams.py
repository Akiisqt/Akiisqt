"""
Cyber Data Streams Renderer.
Renders floating digital telemetry packets (EVA-01, NERV, GUNDAM, etc.).
"""

from __future__ import annotations

import math
from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import COLOR_OSU_BLUE, HEIGHT, WIDTH
from scripts.fonts import load_system_font
from scripts.models import CyberDataStream, FrameContext, build_cyber_data_streams
from scripts.renderers.base import BaseRenderer


class CyberStreamsRenderer(BaseRenderer):
    def __init__(
        self,
        cyber_streams: Optional[List[CyberDataStream]] = None,
        font_micro: Any = None,
    ) -> None:
        self.cyber_streams = cyber_streams if cyber_streams is not None else build_cyber_data_streams()
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        for stream in self.cyber_streams:
            st_y = (stream.y + stream.vy * frame.frame_idx) % HEIGHT
            st_x = stream.x % WIDTH
            s_alpha = int(stream.alpha * (0.6 + 0.4 * math.sin(2.0 * math.pi * frame.t * 2 + stream.x)))
            draw.text((int(st_x), int(st_y)), stream.text, font=self.font_micro, fill=(*COLOR_OSU_BLUE, s_alpha))

