#!/usr/bin/env python3
"""
Cyber-Emo & Authentic osu! Rhythm Aesthetic Dynamic Profile & Stats GIF Generator.
Entrypoint module delegating to the ProfileCardLoader and component renderers.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure repo root is on sys.path for direct script execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Configuration and constants re-exported for backwards compatibility
from scripts.config import (
    ASCII_CAT,
    BOTTOM_CHARACTERS,
    CACHE_FILE,
    COLOR_BG_BOTTOM,
    COLOR_BG_TOP,
    COLOR_BORDER_CYAN,
    COLOR_BORDER_INNER,
    COLOR_BORDER_OUTER,
    COLOR_CYBER_ACCENT,
    COLOR_EVA_GREEN,
    COLOR_EVA_PURPLE,
    COLOR_GLASS_BOX,
    COLOR_GLASS_TITLE,
    COLOR_GLASS_WINDOW,
    COLOR_GUNDAM_BLUE,
    COLOR_GUNDAM_GOLD,
    COLOR_NERV_RED,
    COLOR_OSU_BLUE,
    COLOR_OSU_DARK_PINK,
    COLOR_OSU_GOLD,
    COLOR_OSU_GREEN,
    COLOR_OSU_PINK,
    COLOR_PILL_BG,
    COLOR_PILL_BORDER,
    COLOR_TEXT_CYAN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PINK,
    COLOR_TEXT_PURPLE,
    COLOR_TEXT_WHITE,
    DURATION_SECONDS,
    FPS,
    HEIGHT,
    OUTPUT_FILE,
    SPARKLE_COUNT,
    TOTAL_FRAMES,
    TRIANGLE_COUNT,
    WIDTH,
    get_token,
)

# Cache utilities
from scripts.cache import load_cache as _load_cache, save_cache as _save_cache

def load_cache(cache_file: Optional[Path] = None) -> Dict[str, Any]:
    target = cache_file or getattr(sys.modules[__name__], "CACHE_FILE", CACHE_FILE)
    return _load_cache(target)

def save_cache(data: Dict[str, Any], cache_file: Optional[Path] = None) -> None:
    target = cache_file or getattr(sys.modules[__name__], "CACHE_FILE", CACHE_FILE)
    return _save_cache(data, target)

# Typography and text helpers
from scripts.fonts import (
    clip_text,
    fit_text,
    glyph_supported,
    load_system_font,
    scroll_text,
    text_renderable,
    twinkle,
    wrap_text,
)

# Animation models and particle builders
from scripts.models import (
    CyberDataStream,
    FloatingSkeletonSkull,
    FrameContext,
    OsuSparkle,
    OsuTriangle,
    ParallaxStar,
    ShootingStar,
    build_cyber_data_streams,
    build_floating_skulls,
    build_osu_sparkles,
    build_osu_triangles,
    build_parallax_stars,
    build_shooting_stars,
)

# Data harvesting
from scripts.fetchers import (
    fetch_github_stats,
    fetch_osu_stats,
    fetch_steam_stats,
    fetch_youtube_music_stats,
    get_past_12_months,
    request_github,
)

# Renderers and visual primitives
from scripts.renderers import (
    AboutRenderer,
    AsciiCatRenderer,
    BaseRenderer,
    BottomCharactersRenderer,
    ConnectRenderer,
    CyberStreamsRenderer,
    FloatingSkullsRenderer,
    GithubActivityRenderer,
    InterestsRenderer,
    MusicRenderer,
    OsuProfileRenderer,
    ParallaxStarsRenderer,
    ProfileHeaderRenderer,
    ShootingStarsRenderer,
    SkillMetersRenderer,
    SparklesRenderer,
    SteamProfileRenderer,
    TrianglesRenderer,
    WindowFrameRenderer,
    draw_github_activity_sparkline,
    draw_osu_accuracy_gauge,
    draw_osu_angled_tab,
    draw_osu_glass_box,
    draw_osu_hit_circle,
    draw_osu_skill_meters,
    draw_osu_window_frame,
    draw_ytm_artists_barchart,
)

# Main Loader
from scripts.loader import ProfileCardLoader


def generate_gif() -> None:
    """Main generation entrypoint invoking the ProfileCardLoader."""
    ProfileCardLoader.run()


def main() -> None:
    generate_gif()


if __name__ == "__main__":
    main()
