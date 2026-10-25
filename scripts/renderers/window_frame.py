"""
Window Frame Renderer.
Renders outer window frame, desktop titlebar, corner brackets, and controls.
"""

from __future__ import annotations

import math
from typing import Any

from PIL import ImageDraw

from scripts.config import (
    COLOR_BORDER_INNER,
    COLOR_EVA_PURPLE,
    COLOR_GLASS_TITLE,
    COLOR_GLASS_WINDOW,
    COLOR_GUNDAM_BLUE,
    COLOR_NERV_RED,
    COLOR_OSU_BLUE,
    COLOR_OSU_PINK,
    COLOR_TEXT_WHITE,
)
from scripts.fonts import fit_text, load_system_font
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer


def draw_osu_window_frame(
    glass_draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    font_title: Any,
    font_small: Any,
    glow_phase: float,
) -> None:
    glow_intensity = int(180 + 75 * math.sin(glow_phase))
    glow_color = (
        int(COLOR_OSU_PINK[0] * (glow_intensity / 255)),
        int(COLOR_OSU_PINK[1] * (glow_intensity / 255)),
        int(COLOR_OSU_PINK[2] * (glow_intensity / 255)),
        240,
    )

    glass_draw.rectangle([x - 3, y - 3, x + w + 3, y + h + 3], outline=glow_color, width=1)
    glass_draw.rectangle([x - 1, y - 1, x + w + 1, y + h + 1], outline=(*COLOR_BORDER_INNER, 240), width=2)
    glass_draw.rectangle([x, y, x + w, y + h], fill=COLOR_GLASS_WINDOW)

    # Cyberpunk HUD Outer Corner Brackets
    bk_len = 16
    glass_draw.line([(x - 8, y), (x + bk_len, y)], fill=(*COLOR_OSU_BLUE, 255), width=2)
    glass_draw.line([(x, y - 8), (x, y + bk_len)], fill=(*COLOR_OSU_BLUE, 255), width=2)
    glass_draw.line([(x + w - bk_len, y), (x + w + 8, y)], fill=(*COLOR_OSU_BLUE, 255), width=2)
    glass_draw.line([(x + w, y - 8), (x + w, y + bk_len)], fill=(*COLOR_OSU_BLUE, 255), width=2)
    glass_draw.line([(x - 8, y + h), (x + bk_len, y + h)], fill=(*COLOR_OSU_BLUE, 255), width=2)
    glass_draw.line([(x, y + h - bk_len), (x, y + h + 8)], fill=(*COLOR_OSU_BLUE, 255), width=2)
    glass_draw.line([(x + w - bk_len, y + h), (x + w + 8, y + h)], fill=(*COLOR_OSU_BLUE, 255), width=2)
    glass_draw.line([(x + w, y + h - bk_len), (x + w, y + h + 8)], fill=(*COLOR_OSU_BLUE, 255), width=2)

    title_bar_height = 36
    glass_draw.rectangle([x, y, x + w, y + title_bar_height], fill=COLOR_GLASS_TITLE)
    glass_draw.line([x, y + title_bar_height, x + w, y + title_bar_height], fill=(*COLOR_BORDER_INNER, 220), width=1)

    # Right side: Evangelion NERV & Gundam System Telemetry
    btn_y = y + 10
    btn_x = x + w - 75
    glass_draw.text((btn_x, btn_y), "[_]", font=font_small, fill=COLOR_EVA_PURPLE)
    glass_draw.text((btn_x + 24, btn_y), "[□]", font=font_small, fill=COLOR_GUNDAM_BLUE)
    glass_draw.text((btn_x + 48, btn_y), "[✕]", font=font_small, fill=COLOR_NERV_RED)

    # Clean GitHub Window Title
    safe_title = fit_text(glass_draw, title, font_title, w - 100)
    glass_draw.text((x + 14, y + 9), safe_title, font=font_title, fill=COLOR_TEXT_WHITE)


class WindowFrameRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str,
        font_title: Any = None,
        font_small: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.font_title = font_title or load_system_font(14, bold=True)
        self.font_small = font_small or load_system_font(10, bold=False)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_window_frame(
            draw,
            self.x,
            self.y,
            self.w,
            self.h,
            self.title,
            self.font_title,
            self.font_small,
            frame.glow_phase,
        )

