"""
Tests for modular renderer classes and ProfileCardLoader.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pytest
from PIL import Image, ImageDraw, ImageFont

from scripts.config import HEIGHT, WIDTH
from scripts.fonts import load_system_font
from scripts.loader import ProfileCardLoader
from scripts.models import FrameContext
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
)


def make_canvas(width: int = WIDTH, height: int = HEIGHT) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def make_frame(frame_idx: int = 0, total_frames: int = 60) -> FrameContext:
    t = frame_idx / total_frames
    glow_phase = 2.0 * math.pi * t
    return FrameContext(frame_idx=frame_idx, total_frames=total_frames, t=t, glow_phase=glow_phase)


class TestBackgroundRenderers:
    def test_parallax_stars_renderer(self):
        renderer = ParallaxStarsRenderer()
        assert len(renderer.stars) == 75
        assert isinstance(renderer, BaseRenderer)

        _, draw = make_canvas()
        for frame_idx in [0, 15, 30, 45]:
            renderer.render(draw, make_frame(frame_idx))

    def test_shooting_stars_renderer(self):
        renderer = ShootingStarsRenderer()
        assert len(renderer.stars) == 3
        assert isinstance(renderer, BaseRenderer)

        _, draw = make_canvas()
        for frame_idx in [0, 20, 40]:
            renderer.render(draw, make_frame(frame_idx))

    def test_triangles_renderer(self):
        renderer = TrianglesRenderer()
        assert len(renderer.triangles) == 38
        assert isinstance(renderer, BaseRenderer)

        _, draw = make_canvas()
        for frame_idx in [0, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_sparkles_renderer(self):
        renderer = SparklesRenderer(star_morph_glyphs=["✦", "✧", "+"])
        assert len(renderer.sparkles) == 45
        assert isinstance(renderer, BaseRenderer)

        _, draw = make_canvas()
        for frame_idx in [0, 15, 30, 45]:
            renderer.render(draw, make_frame(frame_idx))

    def test_sparkles_renderer_empty_glyphs_safe(self):
        renderer = SparklesRenderer(star_morph_glyphs=[])
        _, draw = make_canvas()
        renderer.render(draw, make_frame(0))  # Must not crash with division by zero

    def test_cyber_streams_renderer(self):
        renderer = CyberStreamsRenderer()
        assert len(renderer.cyber_streams) == 24
        assert isinstance(renderer, BaseRenderer)

        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_floating_skulls_renderer(self):
        renderer = FloatingSkullsRenderer()
        assert isinstance(renderer, BaseRenderer)

        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))


class TestForegroundRenderers:
    def test_window_frame_renderer(self):
        renderer = WindowFrameRenderer(
            x=35, y=35, w=790, h=690, title="github.com/Akiisqt/Akiisqt/README.md"
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_profile_header_renderer(self):
        renderer = ProfileHeaderRenderer(
            cx=55,
            cy=83,
            p_name="Akiisqt",
            p_tagline="Software Engineer & Builder ✦ Cyber-Emo",
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_ascii_cat_renderer(self):
        renderer = AsciiCatRenderer(
            x=320,
            y=79,
            w=95,
            h=58,
            title="cat",
            ascii_lines=[r" /\ _ /\ ", r"( =^.^= )", r" (\")(\")"],
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_about_renderer(self):
        renderer = AboutRenderer(
            x=55,
            y=145,
            w=360,
            h=145,
            title="about",
            about_lines=["First bullet point.", "Second bullet point with longer text."],
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        renderer.render(draw, make_frame(0))

    def test_skill_meters_renderer(self):
        renderer = SkillMetersRenderer(
            x=55,
            y=302,
            w=360,
            h=118,
            title="skills",
            skills=["Python", "TypeScript", "Linux", "Git", "Docker"],
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_interests_renderer(self):
        renderer = InterestsRenderer(
            x=55,
            y=432,
            w=360,
            h=115,
            title="interests",
            interests=["Retro Tech", "Gaming", "Late 90s Rock"],
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_interests_renderer_empty_safe(self):
        renderer = InterestsRenderer(
            x=55,
            y=432,
            w=360,
            h=115,
            title="interests",
            interests=[],
        )
        _, draw = make_canvas()
        renderer.render(draw, make_frame(0))

    def test_connect_renderer(self):
        renderer = ConnectRenderer(
            x=55,
            y=559,
            w=360,
            h=116,
            title="connect",
            badges=[("⌨ github.com/Akiisqt", (168, 85, 247)), ("🎮 steam/akiisqt", (0, 195, 255))],
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_github_activity_renderer(self):
        stats = {
            "commits": 254,
            "contributions": 182,
            "repositories": 22,
            "stars": 15,
            "monthly_contributions": [("Nov", 10), ("Dec", 20), ("Jan", 30)],
        }
        renderer = GithubActivityRenderer(
            x=445,
            y=83,
            w=380,
            h=180,
            title="activity",
            stats=stats,
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_osu_profile_renderer(self):
        osu_info = {
            "country_rank": 130493,
            "play_count": 4673,
            "accuracy": 82.71,
            "pp": 1300.62,
            "global_rank": 753550,
            "level": 56.78,
        }
        renderer = OsuProfileRenderer(
            x=445,
            y=275,
            w=380,
            h=120,
            title="osu",
            osu_info=osu_info,
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_steam_profile_renderer(self):
        steam_info = {
            "level": 66,
            "games_count": 174,
            "top_games": ["Overwatch®", "Factorio", "Papers, Please"],
        }
        renderer = SteamProfileRenderer(
            x=445,
            y=407,
            w=380,
            h=105,
            title="steam",
            steam_info=steam_info,
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_music_renderer(self):
        artists_hours = [("Linkin Park", 5), ("Disturbed", 2)]
        renderer = MusicRenderer(
            x=445,
            y=524,
            w=380,
            h=151,
            title="music",
            artists_hours=artists_hours,
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))

    def test_bottom_characters_renderer(self):
        renderer = BottomCharactersRenderer(
            card_x=35,
            card_y=35,
            card_w=790,
            card_h=690,
            bottom_chars=[[r"(\_/)", r"(o.o)"], [r"/\_/\ ", r"( =^.^=)"]],
        )
        assert isinstance(renderer, BaseRenderer)
        _, draw = make_canvas()
        for frame_idx in [0, 15, 30]:
            renderer.render(draw, make_frame(frame_idx))


class TestProfileCardLoader:
    def test_loader_init(self, tmp_path):
        loader = ProfileCardLoader(
            profile_path=tmp_path / "profile.json",
            cache_path=tmp_path / "cache.json",
            output_path=tmp_path / "out.gif",
            token="test-token",
        )
        assert loader.token == "test-token"
        assert loader.profile_path == tmp_path / "profile.json"

    def test_loader_fallback_config(self, tmp_path):
        loader = ProfileCardLoader(profile_path=tmp_path / "missing.json")
        config = loader.load_config()
        assert config["profile"]["name"] == "Akiisqt"

    def test_loader_render_single_frame(self):
        loader = ProfileCardLoader()
        loader.load_config()
        loader.load_cache()
        # Seed dummy stats to bypass network
        loader.stats = {
            "username": "Akiisqt",
            "commits": 254,
            "contributions": 182,
            "repositories": 22,
            "stars": 15,
            "monthly_contributions": [("Nov", 10), ("Dec", 20)],
        }
        loader.osu_info = {
            "country_rank": 1000,
            "play_count": 500,
            "accuracy": 95.0,
            "pp": 2000.0,
            "global_rank": 5000,
            "level": 50.0,
        }
        loader.steam_info = {
            "level": 50,
            "games_count": 100,
            "top_games": ["Game A", "Game B"],
        }
        loader.artists_hours = [("Artist 1", 10)]
        loader.init_fonts()
        loader.init_renderers()

        assert len(loader.background_renderers) == 6
        assert len(loader.foreground_renderers) == 12

        frame_img = loader.render_frame(0)
        assert isinstance(frame_img, Image.Image)
        assert frame_img.size == (WIDTH, HEIGHT)
        assert frame_img.mode == "RGBA"

    def test_loader_save_gif(self, tmp_path):
        loader = ProfileCardLoader(output_path=tmp_path / "test.gif")
        img1 = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        img2 = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 10, 255))
        out_file = loader.save_gif([img1, img2])
        assert out_file.is_file()
        assert out_file.stat().st_size > 0

