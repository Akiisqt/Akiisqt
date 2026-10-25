"""
Steam Gaming Profile Box Renderer.
Renders player telemetry (level, library count, verified badge) and scrolling top games ticker.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from PIL import ImageDraw

from scripts.config import (
    COLOR_OSU_BLUE,
    COLOR_OSU_GOLD,
    COLOR_OSU_GREEN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PURPLE,
    COLOR_TEXT_WHITE,
)
from scripts.fonts import load_system_font, scroll_text
from scripts.models import FrameContext
from scripts.renderers.base import BaseRenderer, draw_osu_glass_box


class SteamProfileRenderer(BaseRenderer):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int = 105,
        title: str = "steam",
        steam_info: Optional[Dict[str, Any]] = None,
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
        self.steam_info = steam_info or {
            "level": 0,
            "games_count": 0,
            "top_games": [],
        }
        self.labels = labels or {
            "steam_level": "level",
            "steam_games": "games",
            "steam_community": "community",
            "steam_top": "top",
            "steam_verified": "Verified",
        }
        self.font_small = font_small or load_system_font(10, bold=False)
        self.font_stat_val = font_stat_val or load_system_font(18, bold=True)
        self.font_micro = font_micro or load_system_font(9, bold=True)

    def render(self, draw: ImageDraw.ImageDraw, frame: FrameContext) -> None:
        draw_osu_glass_box(
            draw, self.x, self.y, self.w, self.h, self.title, self.font_micro, COLOR_OSU_BLUE
        )

        steam_col_w = (self.w - 28) // 3

        # Level
        draw.text(
            (self.x + 14, self.y + 16),
            self.labels.get("steam_level", "level"),
            font=self.font_small,
            fill=COLOR_TEXT_MUTED,
        )
        draw.text(
            (self.x + 14, self.y + 29),
            f"Lv. {self.steam_info.get('level', 0)}",
            font=self.font_stat_val,
            fill=COLOR_OSU_BLUE,
        )

        # Games Count
        draw.text(
            (self.x + 14 + steam_col_w, self.y + 16),
            self.labels.get("steam_games", "games"),
            font=self.font_small,
            fill=COLOR_TEXT_MUTED,
        )
        draw.text(
            (self.x + 14 + steam_col_w, self.y + 29),
            f"{self.steam_info.get('games_count', 0)}+",
            font=self.font_stat_val,
            fill=COLOR_OSU_GOLD,
        )

        # Community Status
        draw.text(
            (self.x + 14 + steam_col_w * 2, self.y + 16),
            self.labels.get("steam_community", "community"),
            font=self.font_small,
            fill=COLOR_TEXT_MUTED,
        )
        draw.text(
            (self.x + 14 + steam_col_w * 2, self.y + 29),
            self.labels.get("steam_verified", "Verified"),
            font=self.font_stat_val,
            fill=COLOR_OSU_GREEN,
        )

        # Recent / Featured Steam Games ticker row
        games_row_y = self.y + 62
        top_lbl = self.labels.get("steam_top", "top")
        draw.text((self.x + 14, games_row_y), f"{top_lbl} »", font=self.font_micro, fill=COLOR_TEXT_PURPLE)

        top_games = self.steam_info.get("top_games", [])
        top_games_str = "  ✦  ".join(top_games[:3])
        safe_games_str = scroll_text(draw, top_games_str, self.font_small, self.w - 95, frame.t)
        draw.text((self.x + 80, games_row_y), safe_games_str, font=self.font_small, fill=COLOR_TEXT_WHITE)

