"""
Configuration & Constants for Profile Card Generator.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

# ============================================================
# CANVAS DIMENSIONS & TIMING
# ============================================================

WIDTH = 860
HEIGHT = 760

FPS = 15
DURATION_SECONDS = 4
TOTAL_FRAMES = int(FPS * DURATION_SECONDS)  # 60 frames

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "github_stats.gif"
CACHE_FILE = ROOT_DIR / "cache.json"
PROFILE_FILE = ROOT_DIR / "profile.json"

# ============================================================
# COLOR PALETTE
# Gundam E.F.S.F. & Neon Genesis Evangelion Tactical Mecha Theme (No Orange)
# ============================================================

COLOR_BG_TOP: Tuple[int, int, int] = (18, 22, 34)                  # Deep tactical armor navy
COLOR_BG_BOTTOM: Tuple[int, int, int] = (10, 12, 18)               # Void gunmetal
COLOR_GLASS_WINDOW: Tuple[int, int, int, int] = (14, 18, 28, 245)  # Mecha cockpit glass container
COLOR_GLASS_BOX: Tuple[int, int, int, int] = (20, 25, 38, 225)     # Tactical card container
COLOR_GLASS_TITLE: Tuple[int, int, int, int] = (26, 32, 48, 250)   # Header bar armor plate

# Mecha & Evangelion Core Colors (Cyan, Acid Green, Deep Sync Violet, Crimson, V-Fin Gold)
COLOR_EVA_GREEN: Tuple[int, int, int] = (57, 255, 110)             # Neon Genesis EVA-01 Acid Green (#39ff6e)
COLOR_EVA_PURPLE: Tuple[int, int, int] = (168, 85, 247)            # EVA-01 Deep Sync Violet (#a855f7)
COLOR_NERV_RED: Tuple[int, int, int] = (239, 68, 68)               # Tactical Emergency Red (#ef4444)
COLOR_GUNDAM_BLUE: Tuple[int, int, int] = (0, 195, 255)            # Gundam Anaheim Cyan / Cobalt (#00c3ff)
COLOR_GUNDAM_GOLD: Tuple[int, int, int] = (250, 204, 21)           # Gundam V-Fin Tactical Yellow (#facc15)

# Aliases for UI elements
COLOR_OSU_PINK = COLOR_EVA_PURPLE            # Primary sync accent
COLOR_OSU_DARK_PINK = COLOR_NERV_RED         # Alert crimson
COLOR_OSU_BLUE = COLOR_GUNDAM_BLUE           # Tactical blue / beam cyan
COLOR_OSU_GOLD = COLOR_GUNDAM_GOLD           # Caution gold
COLOR_OSU_GREEN = COLOR_EVA_GREEN            # EVA sync green

COLOR_BORDER_OUTER = COLOR_GUNDAM_BLUE       # Mecha HUD outer glow
COLOR_BORDER_INNER = COLOR_EVA_PURPLE        # EVA tactical border
COLOR_BORDER_CYAN = COLOR_GUNDAM_BLUE        # Tactical cyan
COLOR_CYBER_ACCENT = (59, 130, 246)          # Federation blue

COLOR_TEXT_WHITE: Tuple[int, int, int] = (245, 248, 255)
COLOR_TEXT_MUTED: Tuple[int, int, int] = (156, 163, 175)
COLOR_TEXT_PINK = COLOR_EVA_GREEN            # Acid green pill text
COLOR_TEXT_PURPLE = COLOR_EVA_PURPLE
COLOR_TEXT_CYAN = COLOR_GUNDAM_BLUE
COLOR_PILL_BG: Tuple[int, int, int, int] = (24, 32, 48, 220)
COLOR_PILL_BORDER: Tuple[int, int, int] = (59, 130, 246)

# ============================================================
# ASCII ART & PARTICLES
# ============================================================

ASCII_CAT = [
    r" /\ _ /\ ",
    r"( =^.^= )",
    r" (\")(\")"
]

# Mini ASCII Characters sitting/standing on the bottom window ledge (including Cyber Skeleton!)
BOTTOM_CHARACTERS = [
    [r"(\_/)", r"(o.o)"],        # Bunny
    [r"/\_/\ ", r"( =^.^=)"],    # Kitty
    [r"  X  ", r" -|:|- "],       # Cyber Skeleton companion (ASCII-safe)
    [r"c(..o)", r"( > <)"],      # Mini bear
]

TRIANGLE_COUNT = 38
SPARKLE_COUNT = 45


# ============================================================
# TOKEN SETUP
# ============================================================

def get_token() -> str:
    token = os.getenv("TOKEN", "").strip()
    if token:
        return "github_" + token

    env_path = ROOT_DIR / ".env"
    if env_path.is_file():
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    if key.strip() == "TOKEN":
                        return "github_" + val.strip().strip('"').strip("'")
        except OSError:
            pass
    return ""

