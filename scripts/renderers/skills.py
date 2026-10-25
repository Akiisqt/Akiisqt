"""
Skills Power Meters Renderer.
Renders tech stack proficiency meters with harmonic breathing.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional

from PIL import ImageDraw

from scripts.config import (
    COLOR_BORDER_INNER,
    COLOR_OSU_BLUE,
    COLOR_OSU_PINK,
    COLOR_TEXT_WHITE,
)
from scripts.fonts import load_system_font, scroll_text
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


def draw_osu_skill_meters(
    glass_draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    skills: List[str],
    progress: float,
    font: Any,
) -> None:
    """Draws animated rhythm skill meters for the tech stack with balanced padding."""
    col_w = (w - 14) // 2
    row_h = 24

    proficiencies = [95, 90, 88, 85, 92, 86, 90, 84]

    for idx, skill in enumerate(skills[:8]):
        col = idx % 2
        row = idx // 2
        sx = x + col * (col_w + 14)
        sy = y + 16 + row * row_h

        # Skill Name (scrolls smoothly if longer than 90px)
        safe_skill = scroll_text(glass_draw, skill, font, 90, progress)
        glass_draw.text((sx, sy), safe_skill, font=font, fill=COLOR_TEXT_WHITE)

        # Meter Bar
        meter_x = sx + 95
        meter_w = col_w - 98
        pct = proficiencies[idx % len(proficiencies)]
        wave = 0.96 + 0.04 * math.sin(2 * math.pi * progress + idx * 0.6)
        fill_w = int((pct / 100.0) * meter_w * wave)

        glass_draw.rectangle(
            [meter_x, sy + 3, meter_x + meter_w, sy + 11],
            fill=(40, 30, 56, 180),
            outline=(80, 55, 110),
            width=1,
        )
        bar_color = COLOR_OSU_PINK if (col == 0) else COLOR_OSU_BLUE
        glass_draw.rectangle([meter_x, sy + 3, meter_x + fill_w, sy + 11], fill=(*bar_color, 230))


class SkillMetersRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int = 360,
        h: int = 118,
        title: str = "skills",
        skills: Optional[List[str]] = None,
        font_small: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.skills = skills or []
        self.font_small = font_small or load_system_font(10, bold=False)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_BORDER_INNER
        )
        draw_osu_skill_meters(
            draw, self.x + 12, self.y + 4, self.w - 25, self.skills, frame.t, self.font_small
        )

