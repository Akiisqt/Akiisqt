"""
Main Profile Card Loader and Animation Pipeline Coordinator.
Orchestrates configuration, data harvesting, typography, component renderers,
and animated GIF generation.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repo root is on sys.path for direct script execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PIL import Image, ImageDraw

from scripts.cache import load_cache, save_cache
from scripts.config import (
    ASCII_CAT,
    BOTTOM_CHARACTERS,
    CACHE_FILE,
    COLOR_EVA_PURPLE,
    COLOR_OSU_BLUE,
    COLOR_OSU_GOLD,
    COLOR_OSU_GREEN,
    COLOR_OSU_PINK,
    COLOR_TEXT_CYAN,
    COLOR_TEXT_PURPLE,
    COLOR_TEXT_WHITE,
    DURATION_SECONDS,
    FPS,
    HEIGHT,
    OUTPUT_FILE,
    PROFILE_FILE,
    TOTAL_FRAMES,
    WIDTH,
    get_token,
)
from scripts.fetchers import (
    fetch_github_stats,
    fetch_osu_stats,
    fetch_steam_stats,
    fetch_youtube_music_stats,
)
from scripts.fonts import glyph_supported, load_system_font, text_renderable
from scripts.models import (
    FrameContext,
    build_cyber_data_streams,
    build_floating_skulls,
    build_osu_sparkles,
    build_osu_triangles,
    build_parallax_stars,
    build_shooting_stars,
)
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


class ProfileCardLoader:
    """Main loader orchestrating data harvesting, component rendering, and GIF compilation."""

    def __init__(
        self,
        profile_path: Optional[Path] = None,
        cache_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
        token: Optional[str] = None,
    ) -> None:
        self.profile_path = profile_path or PROFILE_FILE
        self.cache_path = cache_path or CACHE_FILE
        self.output_path = output_path or OUTPUT_FILE
        self.token = token if token is not None else get_token()

        self.profile_data: Dict[str, Any] = {}
        self.cache: Dict[str, Any] = {}
        self.stats: Dict[str, Any] = {}
        self.osu_info: Dict[str, Any] = {}
        self.steam_info: Dict[str, Any] = {}
        self.ytm_info: Dict[str, Any] = {}
        self.artists_hours: List[Tuple[str, int]] = []

        self.fonts: Dict[str, Any] = {}
        self.star_morph_glyphs: List[str] = []
        self.bottom_chars: List[List[str]] = []

        self.background_renderers: List[BaseRenderer] = []
        self.foreground_renderers: List[BaseRenderer] = []

    def load_config(self) -> Dict[str, Any]:
        """Loads user identity, bio, skills, and configuration from profile.json."""
        if self.profile_path.is_file():
            self.profile_data = json.loads(self.profile_path.read_text(encoding="utf-8"))
            print(f"[✓] Loaded profile data from {self.profile_path.name}")
        else:
            self.profile_data = {
                "profile": {"name": "Akiisqt", "handle": "@Akiisqt", "tagline": "Software Engineer & Builder ✦ Cyber-Emo"},
                "about": ["Building cool tools & systems."],
                "skills": ["Python", "TypeScript", "Linux", "Git", "Luau / Lua", "REST & GraphQL", "Docker", "Architecture"],
                "interests": ["Retro Tech", "Gaming", "Late 90s Rock"],
                "music": {"fallback_artist": "Linkin Park", "fallback_track": "By Myself"},
            }
        return self.profile_data

    def load_cache(self) -> Dict[str, Any]:
        """Loads cached API metrics from cache.json."""
        self.cache = load_cache(self.cache_path)
        print(f"[{'✓' if self.cache else '!'}] Cache: {'loaded' if self.cache else 'empty — first run or cleared'}.")
        return self.cache

    def fetch_all_stats(self) -> None:
        """Fetches live metrics across GitHub, osu!, Steam, and YouTube Music with fallbacks."""
        # 1. GitHub stats & activity data
        print("[*] Fetching live metrics and activity from GitHub API...")
        self.stats = fetch_github_stats(
            self.token,
            default_username=self.profile_data.get("profile", {}).get("name", "Akiisqt"),
            cached_data=self.cache.get("github"),
        )
        print(f"    - Commits: {self.stats['commits']}")
        print(f"    - Contributions: {self.stats['contributions']}")
        print(f"    - Repositories: {self.stats['repositories']}")

        # 2. osu! stats
        print("[*] Fetching live osu! rhythm profile stats...")
        self.osu_info = fetch_osu_stats(
            username=self.profile_data.get("osu", {}).get("username", "Akiisqt"),
            fallback_data=self.profile_data.get("osu", {}),
            cached_data=self.cache.get("osu"),
        )
        print(f"    - Global Rank: #{self.osu_info['global_rank']:,}")
        print(f"    - Performance: {self.osu_info['pp']:,.2f} pp")
        print(f"    - Accuracy: {float(self.osu_info['accuracy']):.2f}%")
        print(f"    - Play Count: {int(self.osu_info['play_count']):,}")

        # 3. Steam profile & gaming stats
        print("[*] Fetching live Steam profile & library stats...")
        self.steam_info = fetch_steam_stats(
            custom_url=self.profile_data.get("steam", {}).get("custom_url", "akiisqt"),
            fallback_data=self.profile_data.get("steam", {}),
            cached_data=self.cache.get("steam"),
        )
        print(f"    - Steam Level: {self.steam_info['level']}")
        print(f"    - Games Owned: {self.steam_info['games_count']}")
        print(f"    - Top Titles: {', '.join(self.steam_info['top_games'][:3])}")

        # 4. YouTube Music stats (Multiple Top Artists with Hours)
        print("[*] Scraping live YouTube Music repeat artists & stream hours...")
        self.ytm_info = fetch_youtube_music_stats(
            handle=self.profile_data.get("profile", {}).get("handle", "@Akiisqt"),
            fallback_data=self.profile_data.get("music", {}),
            cached_data=self.cache.get("youtube_music"),
        )
        self.artists_hours = self.ytm_info.get("artists_hours", [
            ("The Presidents of The USA", 6),
            ("Linkin Park", 5),
            ("Disturbed", 1),
            ("System of A Down", 1),
            ("Red Hot Chili Peppers", 1),
        ])
        print(f"    - Repeat Song: {self.ytm_info['track']} by {self.ytm_info['artist']}")
        print(f"    - Top Artists Tracked: {len(self.artists_hours)}")

        # Persist cache
        save_cache(
            {
                "github": self.stats,
                "osu": self.osu_info,
                "steam": self.steam_info,
                "youtube_music": self.ytm_info,
            },
            self.cache_path,
        )

    def init_fonts(self) -> None:
        """Initializes typography hierarchy and filters renderable glyphs."""
        self.fonts = {
            "huge": load_system_font(24, bold=True),
            "title": load_system_font(14, bold=True),
            "stat_val": load_system_font(18, bold=True),
            "stat_sub": load_system_font(16, bold=True),
            "bold": load_system_font(12, bold=True),
            "body": load_system_font(12, bold=False),
            "small_bold": load_system_font(10, bold=True),
            "small": load_system_font(10, bold=False),
            "micro": load_system_font(9, bold=True),
            "cat": load_system_font(12, bold=True),
            "hit": load_system_font(14, bold=True),
            "burst": load_system_font(11, bold=True),
        }

        star_morph_candidates = ["✦", "✧", "+", "★", "✵"]
        self.star_morph_glyphs = [
            g for g in star_morph_candidates if glyph_supported(self.fonts["small"], g)
        ] or ["+", "*"]

        bottom_chars_raw = self.profile_data.get("bottom_characters", BOTTOM_CHARACTERS)
        self.bottom_chars = [
            c for c in bottom_chars_raw
            if all(text_renderable(self.fonts["small"], line) for line in c)
        ]

    def init_renderers(self) -> None:
        """Instantiates all separate component renderers."""
        card_x = 35
        card_y = 35
        card_w = WIDTH - 70
        card_h = HEIGHT - 70

        # Background particles
        triangles = build_osu_triangles()
        sparkles = build_osu_sparkles()
        parallax_stars = build_parallax_stars()
        shooting_stars = build_shooting_stars()
        cyber_streams = build_cyber_data_streams()
        floating_skulls = build_floating_skulls(self.fonts["bold"])

        self.background_renderers = [
            ParallaxStarsRenderer(parallax_stars),
            ShootingStarsRenderer(shooting_stars),
            TrianglesRenderer(triangles),
            SparklesRenderer(sparkles, self.star_morph_glyphs, self.fonts["small"]),
            CyberStreamsRenderer(cyber_streams, self.fonts["micro"]),
            FloatingSkullsRenderer(floating_skulls, self.fonts["bold"]),
        ]

        cfg_titles = self.profile_data.get("titles", {})
        cfg_labels = self.profile_data.get("labels", {})

        title_cat = cfg_titles.get("cat", "cat").lower()
        title_about = cfg_titles.get("about", "about").lower()
        title_skills = cfg_titles.get("skills", "skills").lower()
        title_interests = cfg_titles.get("interests", "interests").lower()
        title_connect = cfg_titles.get("connect", "connect").lower()
        title_activity = cfg_titles.get("activity", "activity").lower()
        title_osu = cfg_titles.get("osu", "osu").lower()
        title_steam = cfg_titles.get("steam", "steam").lower()
        title_music = cfg_titles.get("music", "music").lower()

        window_title = self.profile_data.get(
            "window_title",
            f"github.com/{self.stats.get('username', 'Akiisqt')}/{self.stats.get('username', 'Akiisqt')}/README.md",
        )
        p_name = self.profile_data.get("profile", {}).get("name", "Akiisqt")
        p_tagline = self.profile_data.get("profile", {}).get("tagline", "")
        about_lines = self.profile_data.get("about", [])
        skills = self.profile_data.get(
            "skills",
            ["Python", "TypeScript", "Linux / Bash", "Git", "Luau / Lua", "REST & GraphQL", "Docker / CI/CD"],
        )
        interests = self.profile_data.get("interests", [])
        cat_ascii_lines = self.profile_data.get("cat_ascii", ASCII_CAT)

        color_map = {
            "purple": COLOR_TEXT_PURPLE,
            "blue": COLOR_OSU_BLUE,
            "pink": COLOR_OSU_PINK,
            "cyan": COLOR_TEXT_CYAN,
            "gold": COLOR_OSU_GOLD,
            "violet": (192, 132, 252),
            "green": COLOR_OSU_GREEN,
            "white": COLOR_TEXT_WHITE,
        }
        connect_items = self.profile_data.get("connect")
        if connect_items:
            connect_badges = [
                (item.get("text", ""), color_map.get(item.get("color", "cyan"), COLOR_TEXT_CYAN))
                for item in connect_items
            ]
        else:
            p_obj = self.profile_data.get("profile", {})
            s_obj = self.profile_data.get("steam", {})
            o_obj = self.profile_data.get("osu", {})
            connect_badges = [
                (f"⌨ github.com/{p_obj.get('name', 'Akiisqt')}", COLOR_TEXT_PURPLE),
                (f"🎮 steam/{s_obj.get('custom_url', 'akiisqt')}", COLOR_OSU_BLUE),
                (f"◎ osu!/{o_obj.get('username', 'Akiisqt')}", COLOR_OSU_PINK),
                (f"✉ {p_obj.get('email', 'aki@devours.rocks')}", COLOR_TEXT_CYAN),
                (f"◈ {p_obj.get('location', 'Cyberspace')}", COLOR_OSU_GOLD),
                ("💬 discord: akiisqt", (192, 132, 252)),
            ]

        # Geometry coordinates
        cx = card_x + 20
        cy = card_y + 48
        col_split_x = cx + 380

        cat_box_x = cx + 265
        cat_box_y = cy - 4
        cat_box_w = 95
        cat_box_h = 58

        about_box_y = cy + 62
        about_box_h = 145

        skills_box_y = about_box_y + about_box_h + 12
        skills_box_h = 118

        interests_box_y = skills_box_y + skills_box_h + 12
        interests_box_h = 115

        connect_box_y = interests_box_y + interests_box_h + 12
        connect_box_h = 116

        rx = col_split_x + 10
        rw = card_w - (col_split_x - card_x) - 30

        stats_box_y = cy
        stats_box_h = 180

        osu_box_y = stats_box_y + stats_box_h + 12
        osu_box_h = 120

        steam_box_y = osu_box_y + osu_box_h + 12
        steam_box_h = 105

        music_box_y = steam_box_y + steam_box_h + 12
        music_box_h = 151

        github_labels = {
            "commits": cfg_labels.get("commits", "commits").lower(),
            "contributions": cfg_labels.get("contributions", cfg_labels.get("contribs", "contributions")).lower(),
            "repos": cfg_labels.get("repos", "repos").lower(),
            "stars": cfg_labels.get("stars", "stars").lower(),
        }

        osu_labels = {
            "country": cfg_labels.get("country", "country").lower(),
            "global": cfg_labels.get("global", "global").lower(),
            "plays": cfg_labels.get("plays", "plays").lower(),
            "accuracy": cfg_labels.get("accuracy", "accuracy").lower(),
            "performance": cfg_labels.get("performance", "performance").lower(),
            "level": cfg_labels.get("level", "level").lower(),
        }

        steam_labels = {
            "steam_level": cfg_labels.get("steam_level", "level").lower(),
            "steam_games": cfg_labels.get("steam_games", "games").lower(),
            "steam_community": cfg_labels.get("steam_community", "community").lower(),
            "steam_top": cfg_labels.get("steam_top", "top").lower(),
            "steam_verified": cfg_labels.get("steam_verified", "Verified"),
        }

        self.foreground_renderers = [
            WindowFrameRenderer(
                card_x, card_y, card_w, card_h, window_title, self.fonts["title"], self.fonts["small"]
            ),
            ProfileHeaderRenderer(
                cx, cy, p_name, p_tagline, self.star_morph_glyphs, self.fonts["huge"], self.fonts["body"]
            ),
            AsciiCatRenderer(
                cat_box_x, cat_box_y, cat_box_w, cat_box_h, title_cat, cat_ascii_lines, self.fonts["cat"], self.fonts["micro"]
            ),
            AboutRenderer(
                cx, about_box_y, 360, about_box_h, title_about, about_lines, self.fonts["body"], self.fonts["micro"]
            ),
            SkillMetersRenderer(
                cx, skills_box_y, 360, skills_box_h, title_skills, skills, self.fonts["small"], self.fonts["micro"]
            ),
            InterestsRenderer(
                cx, interests_box_y, 360, interests_box_h, title_interests, interests, self.star_morph_glyphs, self.fonts["small"], self.fonts["micro"]
            ),
            ConnectRenderer(
                cx, connect_box_y, 360, connect_box_h, title_connect, connect_badges, self.fonts["small"], self.fonts["micro"]
            ),
            GithubActivityRenderer(
                rx, stats_box_y, rw, stats_box_h, title_activity, self.stats, github_labels, self.fonts["small"], self.fonts["stat_val"], self.fonts["micro"]
            ),
            OsuProfileRenderer(
                rx, osu_box_y, rw, osu_box_h, title_osu, self.osu_info, osu_labels, self.fonts["small"], self.fonts["stat_val"], self.fonts["stat_sub"], self.fonts["bold"], self.fonts["burst"], self.fonts["micro"]
            ),
            SteamProfileRenderer(
                rx, steam_box_y, rw, steam_box_h, title_steam, self.steam_info, steam_labels, self.fonts["small"], self.fonts["stat_val"], self.fonts["micro"]
            ),
            MusicRenderer(
                rx, music_box_y, rw, music_box_h, title_music, self.artists_hours, self.fonts["bold"], self.fonts["small"], self.fonts["micro"]
            ),
            BottomCharactersRenderer(
                card_x, card_y, card_w, card_h, self.bottom_chars, self.fonts["small"]
            ),
        ]

    def render_frame(self, frame_idx: int) -> Image.Image:
        """Renders and composites a single animation frame."""
        t = frame_idx / TOTAL_FRAMES
        glow_phase = 2.0 * math.pi * t
        frame = FrameContext(frame_idx, TOTAL_FRAMES, t, glow_phase)

        # Layer 1: Background void
        base_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        base_draw = ImageDraw.Draw(base_img)
        for renderer in self.background_renderers:
            renderer.render(base_draw, frame)

        # Layer 2: Translucent glass window layer
        glass_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        glass_draw = ImageDraw.Draw(glass_layer)
        for renderer in self.foreground_renderers:
            renderer.render(glass_draw, frame)

        return Image.alpha_composite(base_img, glass_layer)

    def render_all_frames(self) -> List[Image.Image]:
        """Renders all animation frames for the GIF loop."""
        print(f"[*] Rendering {TOTAL_FRAMES} frames ({FPS} fps, {DURATION_SECONDS}s loop)...")
        frames: List[Image.Image] = []
        for frame_idx in range(TOTAL_FRAMES):
            frames.append(self.render_frame(frame_idx))
        return frames

    def save_gif(self, frames: List[Image.Image], output_path: Optional[Path] = None) -> Path:
        """Compiles rendered frames into an optimized transparent GIF."""
        target = output_path or self.output_path
        print(f"[*] Saving authentic osu! infographic GIF to {target.name} (with transparent background)...")
        frames[0].save(
            target,
            save_all=True,
            append_images=frames[1:],
            duration=int(1000 / FPS),
            loop=0,
            disposal=2,
            optimize=True,
        )
        file_size_mb = target.stat().st_size / (1024 * 1024)
        print(f"[✓] Successfully generated {target.name} ({file_size_mb:.2f} MB)")
        print("=" * 60)
        return target

    @classmethod
    def run(
        cls,
        profile_path: Optional[Path] = None,
        cache_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Executes the full pipeline: loading, data fetching, rendering, and GIF compilation."""
        print("=" * 60)
        print("AUTHENTIC OSU! UI & CYBER INFOGRAPHIC GENERATOR")
        print("=" * 60)

        loader = cls(profile_path=profile_path, cache_path=cache_path, output_path=output_path)
        if loader.token:
            print("[✓] Found GitHub token.")
        else:
            print("[!] No GitHub token found in env or .env. Using fallback/cached stats.")

        loader.load_config()
        loader.load_cache()
        loader.fetch_all_stats()
        loader.init_fonts()
        loader.init_renderers()
        frames = loader.render_all_frames()
        return loader.save_gif(frames)


def main() -> None:
    ProfileCardLoader.run()


if __name__ == "__main__":
    main()
