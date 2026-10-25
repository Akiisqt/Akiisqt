"""
YouTube Music Top Artists Bar Chart Renderer.
Renders horizontal bar chart with rank badges, animated audio waves, and listening hours.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple

from PIL import ImageDraw

from scripts.config import (
    COLOR_BORDER_INNER,
    COLOR_OSU_BLUE,
    COLOR_OSU_GOLD,
    COLOR_OSU_PINK,
    COLOR_TEXT_WHITE,
)
from scripts.fonts import load_system_font, scroll_text
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


def draw_ytm_artists_barchart(
    glass_draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    artists_hours: List[Tuple[str, int]],
    progress: float,
    font_bold: Any,
    font_small: Any,
    anim_t: float = 0.0,
) -> None:
    """Draws a vertical multi-artist listening hours bar graph with right-aligned bars & hours."""
    if not artists_hours:
        return

    max_hrs = max(hrs for _, hrs in artists_hours) or 1
    count = min(5, len(artists_hours))
    row_h = (h - 22) // count

    right_margin = 14
    hrs_label_w = 26
    bar_track_w = 78
    bar_end_x = x + w - right_margin - hrs_label_w - 6
    bar_x = bar_end_x - bar_track_w
    name_max_w = bar_x - (x + 36) - 10

    for i, (name, hrs) in enumerate(artists_hours[:count]):
        ry = y + 14 + i * row_h

        rank_badge = f"#{i+1}"
        glass_draw.text((x + 14, ry), rank_badge, font=font_bold, fill=COLOR_OSU_PINK)

        safe_name = scroll_text(glass_draw, name, font_bold, name_max_w, anim_t)
        glass_draw.text((x + 36, ry), safe_name, font=font_bold, fill=COLOR_TEXT_WHITE)

        wave = 0.95 + 0.05 * math.sin(2 * math.pi * progress + i * 0.8)
        bar_fill_w = max(10, int((hrs / max_hrs) * bar_track_w * wave))

        glass_draw.rectangle([bar_x, ry + 2, bar_end_x, ry + 12], fill=(40, 28, 58, 200), outline=(70, 50, 90), width=1)

        bar_color = COLOR_OSU_PINK if (i == 0) else (COLOR_OSU_BLUE if i == 1 else COLOR_BORDER_INNER)
        glass_draw.rectangle([bar_x, ry + 2, bar_x + bar_fill_w, ry + 12], fill=(*bar_color, 235))

        hrs_text = f"{hrs}h"
        glass_draw.text((bar_end_x + 8, ry + 1), hrs_text, font=font_small, fill=COLOR_OSU_GOLD)


class MusicRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int = 151,
        title: str = "music",
        artists_hours: Optional[List[Tuple[str, int]]] = None,
        font_bold: Any = None,
        font_small: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.artists_hours = artists_hours or []
        self.font_bold = font_bold or load_system_font(12, bold=True)
        self.font_small = font_small or load_system_font(10, bold=False)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_OSU_BLUE
        )
        draw_ytm_artists_barchart(
            draw,
            self.x,
            self.y + 2,
            self.w,
            self.h - 6,
            self.artists_hours,
            frame.t,
            self.font_bold,
            self.font_small,
            anim_t=frame.t,
        )

