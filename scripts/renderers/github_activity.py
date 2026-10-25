"""
GitHub Metrics & Activity Sparkline Renderer.
Renders summary metric columns and 12-month contribution histogram with trend curve.
"""

from __future__ import annotations

import datetime
import math
from typing import Any, Dict, List, Optional, Tuple

from PIL import ImageDraw

from scripts.config import (
    COLOR_BORDER_INNER,
    COLOR_OSU_BLUE,
    COLOR_OSU_GOLD,
    COLOR_OSU_PINK,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PURPLE,
)
from scripts.fonts import load_system_font
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


def draw_github_activity_sparkline(
    glass_draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    data: List[Tuple[Any, int]],
    progress: float,
    font: Any,
) -> None:
    """Draws an animated GitHub contribution momentum histogram & wave across 12 monthly divisions."""
    glass_draw.rectangle([x, y, x + w, y + h], fill=(20, 15, 30, 150), outline=(70, 50, 95, 180), width=1)
    
    if not data:
        return

    raw_max = max(c for _, c in data)
    max_val = max(1, raw_max)
    half_val = round(max_val / 2) if max_val > 1 else 0

    max_str = f"{max_val:,}"
    half_str = f"{half_val:,}"

    # Calculate y-axis label width on the left
    max_w = glass_draw.textlength(max_str, font=font)
    half_w = glass_draw.textlength(half_str, font=font)
    y_axis_w = max(18, int(max(max_w, half_w)) + 6)

    chart_x = x + y_axis_w
    chart_w = w - y_axis_w - 6

    bars = len(data)
    bar_w = (chart_w - 12) // bars
    start_x = chart_x + (chart_w - (bars * bar_w - 4)) // 2

    base_y = y + h - 16
    plot_h = h - 22
    y_max_line = base_y - plot_h
    y_half_line = base_y - plot_h // 2

    # Subtle horizontal reference grid lines
    glass_draw.line([(chart_x + 2, y_max_line), (x + w - 8, y_max_line)], fill=(70, 50, 95, 80), width=1)
    glass_draw.line([(chart_x + 2, y_half_line), (x + w - 8, y_half_line)], fill=(70, 50, 95, 80), width=1)

    # Render left-side y-axis labels (right-aligned against chart plot area)
    glass_draw.text((chart_x - int(max_w) - 3, y_max_line - 5), max_str, font=font, fill=COLOR_TEXT_MUTED)
    glass_draw.text((chart_x - int(half_str_w := half_w) - 3, y_half_line - 5), half_str, font=font, fill=COLOR_TEXT_MUTED)

    points = []
    for i, (m_raw, val) in enumerate(data):
        bx = start_x + i * bar_w
        if val > 0:
            b_pulse = 1.0 + 0.05 * math.sin(2 * math.pi * progress + i * 0.5)
            bar_h = max(2, int((val / max_val) * plot_h * b_pulse))
            by = base_y - bar_h
            glass_draw.rectangle([bx, by, bx + bar_w - 4, base_y], fill=(0, 202, 255, 190))
        else:
            by = base_y
            glass_draw.rectangle([bx, base_y - 1, bx + bar_w - 4, base_y], fill=(45, 55, 80, 140))

        lbl_str = str(m_raw)
        if "-" in lbl_str:
            try:
                m_num = int(lbl_str.split("-")[1])
                lbl_str = datetime.date(2000, m_num, 1).strftime("%b")
            except Exception:
                lbl_str = lbl_str[-2:]
        elif lbl_str.isdigit() and 1 <= int(lbl_str) <= 12:
            lbl_str = datetime.date(2000, int(lbl_str), 1).strftime("%b")
        elif len(lbl_str) > 3 and not lbl_str.isalpha():
            lbl_str = lbl_str[-2:]

        lbl_w = glass_draw.textlength(lbl_str, font=font)
        bar_center = bx + (bar_w - 4) / 2
        glass_draw.text((int(bar_center - lbl_w / 2), y + h - 13), lbl_str, font=font, fill=COLOR_TEXT_MUTED)
        points.append((int(bar_center), by))

    if len(points) >= 2:
        for idx in range(len(points) - 1):
            glass_draw.line([points[idx], points[idx + 1]], fill=(*COLOR_OSU_PINK, 240), width=2)
            px, py = points[idx]
            glass_draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255, 255))
        px, py = points[-1]
        glass_draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255, 255))


class GithubActivityRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int = 180,
        title: str = "activity",
        stats: Optional[Dict[str, Any]] = None,
        labels: Optional[Dict[str, str]] = None,
        font_small: Any = None,
        font_stat_val: Any = None,
        font_micro: Any = None,
    ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.stats = stats or {
            "commits": 0,
            "contributions": 0,
            "repositories": 0,
            "stars": 0,
            "monthly_contributions": [],
        }
        self.labels = labels or {
            "commits": "commits",
            "contributions": "contributions",
            "repos": "repos",
            "stars": "stars",
        }
        self.font_small = font_small or load_system_font(10, bold=False)
        self.font_stat_val = font_stat_val or load_system_font(18, bold=True)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_BORDER_INNER
        )

        stat_entries = [
            (self.labels.get("commits", "commits"), f"{self.stats.get('commits', 0):,}", COLOR_OSU_BLUE),
            (self.labels.get("contributions", "contributions"), f"{self.stats.get('contributions', 0):,}", COLOR_OSU_PINK),
            (self.labels.get("repos", "repos"), f"{self.stats.get('repositories', 0):,}", COLOR_TEXT_PURPLE),
            (self.labels.get("stars", "stars"), f"{self.stats.get('stars', 0):,}", COLOR_OSU_GOLD),
        ]
        num_stats = len(stat_entries)
        col_span = self.w / num_stats
        for idx, (label, val, val_color) in enumerate(stat_entries):
            col_center = self.x + (idx + 0.5) * col_span
            lbl_w = draw.textlength(label, font=self.font_small)
            val_w = draw.textlength(val, font=self.font_stat_val)
            draw.text((int(col_center - lbl_w / 2), self.y + 16), label, font=self.font_small, fill=COLOR_TEXT_MUTED)
            draw.text((int(col_center - val_w / 2), self.y + 29), val, font=self.font_stat_val, fill=val_color)

        spark_y = self.y + 58
        spark_h = self.h - 70
        draw_github_activity_sparkline(
            draw,
            self.x + 14,
            spark_y,
            self.w - 28,
            spark_h,
            self.stats.get("monthly_contributions", []),
            frame.t,
            self.font_micro,
        )

