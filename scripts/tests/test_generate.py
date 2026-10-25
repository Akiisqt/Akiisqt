"""
Tests for generate.py — covering the public seams agreed in the TDD plan.

Seams under test:
  - glyph_supported(font, char)
  - text_renderable(font, text)
  - clip_text(draw, text, font, max_width)
  - fit_text(draw, text, font, max_width)   — existing behaviour preserved
  - scroll_text(draw, text, font, max_width, anim_t)
  - twinkle(freq, anim_t, offset)
  - load_cache() / save_cache(data)         — round-trip via cache.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

# Make the scripts package importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import generate as gen


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_draw(width: int = 600, height: int = 100):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    return ImageDraw.Draw(img)


def default_font():
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Seam: glyph_supported
# ---------------------------------------------------------------------------

class TestGlyphSupported:
    def test_ascii_letter_is_supported(self):
        assert gen.glyph_supported(default_font(), "A") is True

    def test_digit_is_supported(self):
        assert gen.glyph_supported(default_font(), "9") is True

    def test_returns_bool(self):
        result = gen.glyph_supported(default_font(), " ")
        assert isinstance(result, bool)

    def test_emoji_returns_bool_without_crash(self):
        result = gen.glyph_supported(default_font(), "💀")
        assert isinstance(result, bool)

    def test_broken_font_returns_false(self):
        class BadFont:
            def getmask(self, char):
                raise RuntimeError("broken")

        assert gen.glyph_supported(BadFont(), "A") is False


# ---------------------------------------------------------------------------
# Seam: text_renderable
# ---------------------------------------------------------------------------

class TestTextRenderable:
    def test_plain_ascii_is_renderable(self):
        assert gen.text_renderable(default_font(), "hello world") is True

    def test_empty_string_is_renderable(self):
        assert gen.text_renderable(default_font(), "") is True

    def test_whitespace_only_is_renderable(self):
        # all() over empty iterable is True
        assert gen.text_renderable(default_font(), "   ") is True


# ---------------------------------------------------------------------------
# Seam: clip_text
# ---------------------------------------------------------------------------

class TestClipText:
    def test_short_text_returned_unchanged(self):
        draw = make_draw()
        font = default_font()
        assert gen.clip_text(draw, "Hi", font, 10_000) == "Hi"

    def test_clipped_result_fits_max_width(self):
        draw = make_draw()
        font = default_font()
        long_text = "A" * 300
        result = gen.clip_text(draw, long_text, font, 50)
        assert draw.textlength(result, font=font) <= 50

    def test_clipped_result_is_shorter_than_original(self):
        draw = make_draw()
        font = default_font()
        long_text = "A" * 300
        result = gen.clip_text(draw, long_text, font, 50)
        assert len(result) < len(long_text)

    def test_zero_max_width_returns_empty(self):
        draw = make_draw()
        font = default_font()
        assert gen.clip_text(draw, "ABC", font, 0) == ""

    def test_no_ellipsis_appended(self):
        draw = make_draw()
        font = default_font()
        result = gen.clip_text(draw, "Hello World Long Text Here", font, 40)
        assert "..." not in result


# ---------------------------------------------------------------------------
# Seam: fit_text  (existing behaviour must be preserved)
# ---------------------------------------------------------------------------

class TestFitText:
    def test_short_text_returned_unchanged(self):
        draw = make_draw()
        font = default_font()
        assert gen.fit_text(draw, "Hi", font, 10_000) == "Hi"

    def test_truncated_text_ends_with_ellipsis(self):
        draw = make_draw()
        font = default_font()
        result = gen.fit_text(draw, "A" * 300, font, 50)
        assert result.endswith("...")

    def test_truncated_result_fits_max_width(self):
        draw = make_draw()
        font = default_font()
        result = gen.fit_text(draw, "A" * 300, font, 50)
        assert draw.textlength(result, font=font) <= 50

    def test_returns_ellipsis_when_no_room(self):
        draw = make_draw()
        font = default_font()
        assert gen.fit_text(draw, "XYZ", font, 0) == "..."


# ---------------------------------------------------------------------------
# Seam: scroll_text
# ---------------------------------------------------------------------------

class TestScrollText:
    def test_fitting_text_unchanged_at_any_t(self):
        draw = make_draw()
        font = default_font()
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            assert gen.scroll_text(draw, "Hi", font, 10_000, t) == "Hi"

    def test_overflowing_result_fits_max_width(self):
        draw = make_draw()
        font = default_font()
        long_text = "A" * 300
        for t in [0.0, 0.25, 0.5, 0.75]:
            result = gen.scroll_text(draw, long_text, font, 50, t)
            assert draw.textlength(result, font=font) <= 50, f"Overflow at t={t}"

    def test_different_positions_for_different_t(self):
        draw = make_draw(800, 100)
        font = default_font()
        long_text = "The quick brown fox jumps over the lazy dog and keeps going on and on"
        results = {t: gen.scroll_text(draw, long_text, font, 80, t) for t in [0.0, 0.3, 0.6, 0.9]}
        assert len(set(results.values())) > 1, "Scrolling text should differ across t values"

    def test_no_ellipsis_in_scrolled_result(self):
        draw = make_draw()
        font = default_font()
        result = gen.scroll_text(draw, "Long text that overflows the container box", font, 50, 0.5)
        assert "..." not in result

    def test_empty_string_returned_unchanged(self):
        draw = make_draw()
        font = default_font()
        assert gen.scroll_text(draw, "", font, 100, 0.5) == ""


# ---------------------------------------------------------------------------
# Seam: twinkle
# ---------------------------------------------------------------------------

class TestTwinkle:
    def test_output_always_in_zero_to_one(self):
        import random
        rng = random.Random(42)
        for _ in range(2000):
            freq = rng.uniform(0.5, 4.0)
            t = rng.uniform(0.0, 1.0)
            offset = rng.uniform(0, 2 * math.pi)
            val = gen.twinkle(freq, t, offset)
            assert 0.0 <= val <= 1.0, f"Out of range: {val} at freq={freq}, t={t}"

    def test_integer_freq_loops_perfectly(self):
        for freq in [1.0, 2.0, 3.0]:
            v0 = gen.twinkle(freq, 0.0, 0.0)
            v1 = gen.twinkle(freq, 1.0, 0.0)
            assert abs(v0 - v1) < 1e-9, f"Not seamless at freq={freq}"

    def test_zero_freq_is_constant(self):
        # sin(0) = 0 always, so result = 0.5
        for t in [0.0, 0.3, 0.7, 1.0]:
            assert gen.twinkle(0.0, t, 0.0) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Seam: load_cache / save_cache
# ---------------------------------------------------------------------------

class TestCache:
    def test_round_trip(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "cache.json"
        monkeypatch.setattr(gen, "CACHE_FILE", cache_file)

        data = {"osu": {"global_rank": 123456, "pp": 1500.0}, "github": {"commits": 300}}
        gen.save_cache(data)
        loaded = gen.load_cache()

        assert loaded["osu"]["global_rank"] == 123456
        assert loaded["github"]["commits"] == 300

    def test_load_returns_empty_when_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(gen, "CACHE_FILE", tmp_path / "nonexistent.json")
        assert gen.load_cache() == {}

    def test_load_returns_empty_on_invalid_json(self, tmp_path, monkeypatch):
        bad = tmp_path / "bad.json"
        bad.write_text("not valid json {{", encoding="utf-8")
        monkeypatch.setattr(gen, "CACHE_FILE", bad)
        assert gen.load_cache() == {}

    def test_save_does_not_raise_on_write_error(self, tmp_path, monkeypatch, capsys):
        # Point at a directory (not a file) to provoke an OSError
        monkeypatch.setattr(gen, "CACHE_FILE", tmp_path)
        gen.save_cache({"test": 1})  # must not raise
        assert "Warning" in capsys.readouterr().err

    def test_nested_data_preserved(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "cache.json"
        monkeypatch.setattr(gen, "CACHE_FILE", cache_file)

        data = {
            "youtube_music": {
                "artists_hours": [["Linkin Park", 5], ["Disturbed", 1]],
                "track": "Numb",
                "artist": "Linkin Park",
            }
        }
        gen.save_cache(data)
        loaded = gen.load_cache()
        assert loaded["youtube_music"]["track"] == "Numb"
        assert loaded["youtube_music"]["artists_hours"][0][0] == "Linkin Park"


# ---------------------------------------------------------------------------
# Seam: get_past_12_months
# ---------------------------------------------------------------------------

class TestGetPast12Months:
    def test_returns_exactly_12_months(self):
        months = gen.get_past_12_months()
        assert len(months) == 12

    def test_october_reference_date_starts_in_november_previous_year(self):
        import datetime
        dt = datetime.datetime(2026, 10, 24, tzinfo=datetime.timezone.utc)
        months = gen.get_past_12_months(dt)
        assert len(months) == 12
        assert months[0] == (2025, 11)   # Last year's November
        assert months[-1] == (2026, 10)  # Current year's October

    def test_september_reference_date_starts_in_october_previous_year(self):
        import datetime
        dt = datetime.datetime(2026, 9, 15, tzinfo=datetime.timezone.utc)
        months = gen.get_past_12_months(dt)
        assert len(months) == 12
        assert months[0] == (2025, 10)
        assert months[-1] == (2026, 9)

    def test_january_reference_date_crosses_year_boundary(self):
        import datetime
        dt = datetime.datetime(2027, 1, 10, tzinfo=datetime.timezone.utc)
        months = gen.get_past_12_months(dt)
        assert len(months) == 12
        assert months[0] == (2026, 2)
        assert months[-1] == (2027, 1)

    def test_all_months_consecutive(self):
        import datetime
        dt = datetime.datetime(2026, 6, 1, tzinfo=datetime.timezone.utc)
        months = gen.get_past_12_months(dt)
        for i in range(len(months) - 1):
            y1, m1 = months[i]
            y2, m2 = months[i + 1]
            if m1 == 12:
                assert y2 == y1 + 1 and m2 == 1
            else:
                assert y2 == y1 and m2 == m1 + 1


# ---------------------------------------------------------------------------
# Seam: draw_github_activity_sparkline (12 divisions)
# ---------------------------------------------------------------------------

class TestDrawGithubActivitySparkline:
    def test_renders_12_divisions_without_error(self):
        draw = make_draw(370, 100)
        font = default_font()
        data = [
            ("Nov", 14), ("Dec", 10), ("Jan", 12), ("Feb", 16),
            ("Mar", 22), ("Apr", 15), ("May", 18), ("Jun", 24),
            ("Jul", 20), ("Aug", 26), ("Sep", 32), ("Oct", 28),
        ]
        # Should execute cleanly without raising
        gen.draw_github_activity_sparkline(draw, 10, 10, 350, 80, data, 0.5, font)

    def test_empty_data_handled_cleanly(self):
        draw = make_draw(370, 100)
        font = default_font()
        gen.draw_github_activity_sparkline(draw, 10, 10, 350, 80, [], 0.0, font)

    def test_handles_various_month_label_formats(self):
        draw = make_draw(370, 100)
        font = default_font()
        data = [("2025-11", 5), ("2025-12", 8), ("01", 12), ("Feb", 15)]
        gen.draw_github_activity_sparkline(draw, 10, 10, 350, 80, data, 0.25, font)

    def test_renders_with_zero_heavy_data_and_y_values(self):
        draw = make_draw(370, 100)
        font = default_font()
        data = [
            ("Nov", 11), ("Dec", 0), ("Jan", 0), ("Feb", 0),
            ("Mar", 0), ("Apr", 2), ("May", 0), ("Jun", 0),
            ("Jul", 0), ("Aug", 7), ("Sep", 113), ("Oct", 49),
        ]
        # Should cleanly render y-values (113, 57), guide lines, and columns
        gen.draw_github_activity_sparkline(draw, 10, 10, 350, 80, data, 0.5, font)


# ---------------------------------------------------------------------------
# Seam: fetch_github_stats (monthly_contributions fallback)
# ---------------------------------------------------------------------------

class TestFetchGithubStats:
    def test_uses_cached_monthly_contributions(self):
        cached = {
            "monthly_contributions": [["Nov", 10], ["Dec", 20]],
            "commits": 100,
            "contributions": 300,
        }
        stats = gen.fetch_github_stats(token="", default_username="Akiisqt", cached_data=cached)
        assert stats["monthly_contributions"] == [("Nov", 10), ("Dec", 20)]
        assert stats["contributions"] == 300

    def test_floor_generates_12_months_when_no_cache(self):
        stats = gen.fetch_github_stats(token="", default_username="Akiisqt", cached_data={})
        assert len(stats["monthly_contributions"]) == 12
        assert stats["contributions"] > 0


# ---------------------------------------------------------------------------
# Seam: draw_osu_skill_meters (scrolls long skills)
# ---------------------------------------------------------------------------

class TestDrawOsuSkillMeters:
    def test_short_and_long_skills_render_cleanly(self):
        draw = make_draw(360, 120)
        font = default_font()
        skills = [
            "Python",
            "Extremely Long Skill Name That Definitely Overflows Ninety Pixels",
            "TypeScript",
            "PostgreSQL & Distributed Systems Architecture",
        ]
        # Should render across progress timesteps without error
        for t in [0.0, 0.25, 0.5, 0.75]:
            gen.draw_osu_skill_meters(draw, 10, 10, 335, skills, t, font)


