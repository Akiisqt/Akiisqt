"""
Animation models and particle generators.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, List, Tuple

from scripts.config import (
    COLOR_OSU_BLUE,
    COLOR_OSU_PINK,
    HEIGHT,
    SPARKLE_COUNT,
    TOTAL_FRAMES,
    TRIANGLE_COUNT,
    WIDTH,
)
from scripts.fonts import glyph_supported


@dataclass
class FrameContext:
    frame_idx: int
    total_frames: int
    t: float
    glow_phase: float


@dataclass
class OsuTriangle:
    x: float
    y: float
    size: float
    opacity: int
    color: Tuple[int, int, int]
    amp: float
    freq: int
    phase: float


@dataclass
class OsuSparkle:
    x: float
    y: float
    vy: float
    char: str
    freq: int
    offset: float


@dataclass
class CyberDataStream:
    x: float
    y: float
    vy: float
    text: str
    alpha: int


@dataclass
class FloatingSkeletonSkull:
    x: float
    y: float
    vy: float
    glyph: str
    alpha: int
    freq: int
    offset: float


@dataclass
class ParallaxStar:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    brightness: int
    twinkle_freq: int
    twinkle_offset: float


@dataclass
class ShootingStar:
    start_x: float
    start_y: float
    dx: float
    dy: float
    length: float
    speed: float
    color: Tuple[int, int, int]


def build_floating_skulls(font: Any) -> List[FloatingSkeletonSkull]:
    """Builds ethereal cyber-skeleton skulls drifting in the void.
    Only includes glyphs supported by the given font; returns [] if none are supported."""
    skull_glyphs_all = ["☠", "💀", "🦴"]
    skull_glyphs = [g for g in skull_glyphs_all if glyph_supported(font, g)]
    if not skull_glyphs:
        return []
    random.seed(666)
    skulls = []
    for _ in range(16):
        x = random.uniform(8, WIDTH - 8)
        y = random.uniform(0, HEIGHT)
        vy = (random.choice([-1, -2]) * HEIGHT) / TOTAL_FRAMES
        glyph = random.choice(skull_glyphs)
        alpha = random.randint(110, 195)
        freq = random.choice([1, 2])
        offset = random.uniform(0, 2 * math.pi)
        skulls.append(FloatingSkeletonSkull(x, y, vy, glyph, alpha, freq, offset))
    return skulls


def build_cyber_data_streams() -> List[CyberDataStream]:
    """Builds Gundam Anaheim Electronics & Neon Genesis Evangelion NERV telemetry packets."""
    random.seed(909)
    streams = []
    tokens = [
        "EVA-01", "NERV.SYS", "SYNC:99.8%", "MAGI:OK", "0xDEAD",
        "GUNDAM.RX", "ANAHEIM", "NT-D:ON", "E.F.S.F.", "AT_FIELD",
        "0x7F", "BEAM_SABER", "MINOVSKY", "DEAD_CORP", "CALCIUM", "UNIT-02"
    ]
    for _ in range(24):
        x = random.uniform(8, WIDTH - 8)
        y = random.uniform(0, HEIGHT)
        vy = (random.choice([-1, -2]) * HEIGHT) / TOTAL_FRAMES
        text = random.choice(tokens)
        alpha = random.randint(100, 175)
        streams.append(CyberDataStream(x=x, y=y, vy=vy, text=text, alpha=alpha))
    return streams


def build_parallax_stars() -> List[ParallaxStar]:
    """Builds multi-layer depth parallax stars with deterministic integer wrapping."""
    random.seed(999)
    stars = []
    # 3 depth layers: 0=distant (slow, dim), 1=mid, 2=foreground (fast, bright)
    for _ in range(75):
        layer = random.choices([0, 1, 2], weights=[0.5, 0.35, 0.15])[0]
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)
        
        if layer == 0:
            h_cross = random.choice([-1, 0, 1])
            radius = 1.0
            brightness = random.randint(110, 170)
        elif layer == 1:
            h_cross = random.choice([-2, -1, 1, 2])
            radius = 1.5
            brightness = random.randint(170, 220)
        else:
            h_cross = random.choice([-3, -2, 2, 3])
            radius = 2.2
            brightness = random.randint(220, 255)

        vx = (h_cross * WIDTH) / TOTAL_FRAMES
        vy = (random.choice([-1, 0]) * HEIGHT) / TOTAL_FRAMES
        twinkle_freq = random.choice([1, 2, 3])
        twinkle_offset = random.uniform(0, 2 * math.pi)

        stars.append(ParallaxStar(x, y, vx, vy, radius, brightness, twinkle_freq, twinkle_offset))
    return stars


def build_shooting_stars() -> List[ShootingStar]:
    """Builds diagonal looping shooting star streaks."""
    return [
        ShootingStar(
            start_x=WIDTH * 0.95,
            start_y=-30,
            dx=-1.4,
            dy=1.0,
            length=110,
            speed=1.0,
            color=COLOR_OSU_PINK,
        ),
        ShootingStar(
            start_x=WIDTH * 0.55,
            start_y=-40,
            dx=-1.3,
            dy=1.0,
            length=120,
            speed=1.0,
            color=COLOR_OSU_BLUE,
        ),
        ShootingStar(
            start_x=WIDTH * 1.15,
            start_y=HEIGHT * 0.25,
            dx=-1.5,
            dy=1.0,
            length=95,
            speed=2.0,
            color=(192, 132, 252),
        ),
    ]


def build_osu_triangles() -> List[OsuTriangle]:
    random.seed(727)
    triangles: List[OsuTriangle] = []
    colors = [
        (255, 102, 170),
        (192, 132, 252),
        (0, 202, 255),
        (255, 255, 255),
    ]

    for _ in range(TRIANGLE_COUNT):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)
        size = random.uniform(18, 54)
        opacity = random.randint(18, 55)
        color = random.choice(colors)
        amp = random.uniform(8.0, 22.0)
        freq = random.choice([1, 2])
        phase = random.uniform(0, 2 * math.pi)

        triangles.append(OsuTriangle(x=x, y=y, size=size, opacity=opacity, color=color, amp=amp, freq=freq, phase=phase))

    return triangles


def build_osu_sparkles() -> List[OsuSparkle]:
    random.seed(1337)
    sparkles: List[OsuSparkle] = []
    glyphs = ["✦", "✧", "+", "★"]

    for _ in range(SPARKLE_COUNT):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)
        crossings = random.choice([-1, 0, -2])
        vy = (crossings * HEIGHT) / TOTAL_FRAMES
        char = random.choice(glyphs)
        freq = random.choice([1, 2, 3])
        offset = random.uniform(0, 2 * math.pi)

        sparkles.append(OsuSparkle(x=x, y=y, vy=vy, char=char, freq=freq, offset=offset))

    return sparkles

