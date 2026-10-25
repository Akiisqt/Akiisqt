"""
osu! Rhythm Profile Box Renderer.
Renders rhythm hit circle with approach ring, burst popup, and 2-row player metrics.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

from PIL import ImageDraw

from scripts.config import (
    COLOR_OSU_BLUE,
    COLOR_OSU_GOLD,
    COLOR_OSU_PINK,
    COLOR_TEXT_CYAN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PURPLE,
    COLOR_TEXT_WHITE,
)
from scripts.fonts import load_system_font
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


def draw_osu_hit_circle(
    glass_draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    radius: int,
    progress: float,
    font_logo: Any,
    font_burst: Any,
) -> None:
    pulse = 1.0 + 0.08 * math.sin(2 * math.pi * progress)
    r = int(radius * pulse)

    glass_draw.ellipse(
        [center_x - r, center_y - r, center_x + r, center_y + r],
        fill=(235, 47, 120, 230),
        outline=(255, 255, 255, 255),
        width=3,
    )
    glass_draw.ellipse(
        [center_x - r + 3, center_y - r + 3, center_x + r - 3, center_y + r - 3],
        outline=(*COLOR_OSU_PINK, 190),
        width=1,
    )

    beat_t = (progress * 2.0) % 1.0
    approach_r = int(r * (2.4 - 1.4 * beat_t))
    approach_alpha = int(220 * beat_t)
    glass_draw.ellipse(
        [center_x - approach_r, center_y - approach_r, center_x + approach_r, center_y + approach_r],
        outline=(*COLOR_OSU_BLUE, approach_alpha),
        width=2,
    )

    logo_text = "osu!"
    tw = glass_draw.textlength(logo_text, font=font_logo)
    glass_draw.text((center_x - int(tw) // 2, center_y - 7), logo_text, font=font_logo, fill=COLOR_TEXT_WHITE)

    if beat_t < 0.35:
        burst_alpha = int(255 * (1.0 - beat_t / 0.35))
        burst_y = center_y - r - 10 - int(12 * (beat_t / 0.35))
        glass_draw.text((center_x - 14, burst_y), "300", font=font_burst, fill=(94, 234, 212, burst_alpha))


def draw_osu_accuracy_gauge(
    glass_draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    r: int,
    accuracy: float,
    progress: float,
    font_num: Any,
    font_lbl: Any,
    label: str = "ACCURACY",
) -> None:
    """Renders a circular rhythm accuracy meter with animated pulse and clean unclipped labels."""
    lw = glass_draw.textlength(label, font=font_lbl)
    glass_draw.text((cx - lw // 2, cy - r - 12), label, font=font_lbl, fill=COLOR_TEXT_MUTED)

    glass_draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 45, 80, 200), width=3)
    angle_sweep = int((accuracy / 100.0) * 360)
    wobble = int(3 * math.sin(2 * math.pi * progress))
    glass_draw.arc(
        [cx - r, cy - r, cx + r, cy + r],
        start=-90,
        end=-90 + angle_sweep + wobble,
        fill=(*COLOR_OSU_GOLD, 240),
        width=3,
    )

    acc_text = f"{accuracy:.1f}%"
    aw = glass_draw.textlength(acc_text, font=font_num)
    glass_draw.text((cx - aw // 2, cy - 7), acc_text, font=font_num, fill=COLOR_OSU_GOLD)


class OsuProfileRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int = 120,
        title: str = "osu",
        osu_info: Optional[Dict[str, Any]] = None,
        labels: Optional[Dict[str, str]] = None,
        font_small: Any = None,
        font_stat_val: Any = None,
        font_stat_sub: Any = None,
        font_bold: Any = None,
        font_burst: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.osu_info = osu_info or {
            "country_rank": 0,
            "play_count": 0,
            "accuracy": 0.0,
            "pp": 0.0,
            "global_rank": 0,
            "level": "0.0",
        }
        self.labels = labels or {
            "country": "country",
            "plays": "plays",
            "accuracy": "accuracy",
            "performance": "performance",
            "global": "global",
            "level": "level",
        }
        self.font_small = font_small or load_system_font(10, bold=False)
        self.font_stat_val = font_stat_val or load_system_font(18, bold=True)
        self.font_stat_sub = font_stat_sub or load_system_font(16, bold=True)
        self.font_bold = font_bold or load_system_font(12, bold=True)
        self.font_burst = font_burst or load_system_font(11, bold=True)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_OSU_PINK
        )

        osu_hit_center_x = self.x + 38
        osu_hit_center_y = self.y + 60
        draw_osu_hit_circle(
            draw,
            osu_hit_center_x,
            osu_hit_center_y,
            18,
            frame.t,
            self.font_bold,
            self.font_burst,
        )

        col_w_osu = 92
        c0_x = self.x + 72
        c1_x = c0_x + col_w_osu
        c2_x = c1_x + col_w_osu

        # Row 1: country | plays | accuracy
        draw.text((c0_x, self.y + 16), self.labels.get("country", "country"), font=self.font_small, fill=COLOR_TEXT_MUTED)
        draw.text((c0_x, self.y + 29), f"#{self.osu_info.get('country_rank', 0):,}", font=self.font_stat_val, fill=COLOR_OSU_PINK)

        draw.text((c1_x, self.y + 16), self.labels.get("plays", "plays"), font=self.font_small, fill=COLOR_TEXT_MUTED)
        draw.text((c1_x, self.y + 29), f"{int(self.osu_info.get('play_count', 0)):,}", font=self.font_stat_sub, fill=COLOR_TEXT_WHITE)

        draw.text((c2_x, self.y + 16), self.labels.get("accuracy", "accuracy"), font=self.font_small, fill=COLOR_TEXT_MUTED)
        draw.text((c2_x, self.y + 29), f"{float(self.osu_info.get('accuracy', 0.0)):.2f}%", font=self.font_stat_val, fill=COLOR_OSU_GOLD)

        # Row 2: performance | global | level
        draw.text((c0_x, self.y + 56), self.labels.get("performance", "performance"), font=self.font_small, fill=COLOR_TEXT_MUTED)
        draw.text((c0_x, self.y + 69), f"{round(float(self.osu_info.get('pp', 0.0))):,}pp", font=self.font_stat_val, fill=COLOR_OSU_BLUE)

        draw.text((c1_x, self.y + 56), self.labels.get("global", "global"), font=self.font_small, fill=COLOR_TEXT_MUTED)
        draw.text((c1_x, self.y + 69), f"#{self.osu_info.get('global_rank', 0):,}", font=self.font_stat_sub, fill=COLOR_TEXT_PURPLE)

        draw.text((c2_x, self.y + 56), self.labels.get("level", "level"), font=self.font_small, fill=COLOR_TEXT_MUTED)
        draw.text((c2_x, self.y + 69), f"Lv.{round(float(self.osu_info.get('level', 0.0)))}", font=self.font_stat_sub, fill=COLOR_TEXT_CYAN)

