"""
Data harvesting and API fetching with resilient 3-tier fallback cascade:
Live API -> cache.json -> Hardcoded Floors
"""

from __future__ import annotations

import calendar
import datetime
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple


def get_past_12_months(reference_date: Optional[datetime.datetime] = None) -> List[Tuple[int, int]]:
    """Returns a list of 12 (year, month) tuples representing the rolling 12 months ending in reference_date."""
    if reference_date is None:
        reference_date = datetime.datetime.now(datetime.timezone.utc)
    months = []
    for i in range(11, -1, -1):
        m_idx = reference_date.month - 1 - i
        y = reference_date.year + (m_idx // 12)
        m = (m_idx % 12) + 1
        months.append((y, m))
    return months


def request_github(url: str, token: str, method: str = "GET", data: Optional[dict] = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "cyber-emo-profile-stats",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(data).encode("utf-8") if data is not None else None
    if body:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, headers=headers, method=method, data=body)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except Exception as e:
        print(f"[Warning] GitHub request failed for {url}: {e}", file=sys.stderr)
        return None


def fetch_github_stats(token: str, default_username: str = "Akiisqt", cached_data: Optional[dict] = None) -> Dict[str, Any]:
    _ca = cached_data or {}
    user_info = request_github("https://api.github.com/user", token) if token else None
    username = user_info.get("login", default_username) if user_info else default_username
    followers = user_info.get("followers", 0) if user_info else (_ca.get("followers") or 0)

    repos_data = request_github(f"https://api.github.com/users/{username}/repos?per_page=100&type=owner", token) or []
    repo_count = len(repos_data)
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data if isinstance(repo, dict))

    search_commits_url = "https://api.github.com/search/commits?q=" + urllib.parse.quote(f"author:{username}")
    commits_data = request_github(search_commits_url, token)
    total_commits = commits_data.get("total_count", 0) if commits_data else (_ca.get("commits") or 254)

    search_prs_url = "https://api.github.com/search/issues?q=" + urllib.parse.quote(f"author:{username} type:pr")
    prs_data = request_github(search_prs_url, token)
    total_prs = prs_data.get("total_count", 0) if prs_data else (_ca.get("pull_requests") or 7)

    search_issues_url = "https://api.github.com/search/issues?q=" + urllib.parse.quote(f"author:{username} type:issue")
    issues_data = request_github(search_issues_url, token)
    total_issues = issues_data.get("total_count", 0) if issues_data else (_ca.get("issues") or 9)

    monthly_contributions = []
    total_contributions = 0
    past_months = get_past_12_months()

    if token:
        y_start, m_start = past_months[0]
        y_end, m_end = past_months[-1]
        last_day = calendar.monthrange(y_end, m_end)[1]
        from_date = f"{y_start}-{m_start:02d}-01T00:00:00Z"
        to_date = f"{y_end}-{m_end:02d}-{last_day:02d}T23:59:59Z"

        gql_query = {
            "query": f"""
            query {{
              viewer {{
                contributionsCollection(from: "{from_date}", to: "{to_date}") {{
                  totalCommitContributions
                  totalIssueContributions
                  totalPullRequestContributions
                  totalPullRequestReviewContributions
                  restrictedContributionsCount
                  contributionCalendar {{
                    totalContributions
                    weeks {{
                      contributionDays {{
                        date
                        contributionCount
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
        }
        res = request_github("https://api.github.com/graphql", token, method="POST", data=gql_query)
        if res and "data" in res and res["data"] and "viewer" in res["data"]:
            col = res["data"]["viewer"].get("contributionsCollection") or {}
            cal = col.get("contributionCalendar") or {}
            month_counts = {f"{y}-{m:02d}": 0 for y, m in past_months}
            for week in cal.get("weeks", []):
                for day in week.get("contributionDays", []):
                    d_prefix = day.get("date", "")[:7]
                    if d_prefix in month_counts:
                        month_counts[d_prefix] += day.get("contributionCount", 0)

            monthly_contributions = [
                (datetime.date(y, m, 1).strftime("%b"), month_counts[f"{y}-{m:02d}"])
                for y, m in past_months
            ]
            cal_total = cal.get("totalContributions", 0)
            total_contributions = cal_total if cal_total > 0 else sum(c for _, c in monthly_contributions)

    if not monthly_contributions:
        cached_mc = _ca.get("monthly_contributions")
        if cached_mc:
            monthly_contributions = [tuple(x) for x in cached_mc]
            total_contributions = _ca.get("contributions") or sum(c for _, c in monthly_contributions)
        else:
            month_abbrs = [datetime.date(y, m, 1).strftime("%b") for y, m in past_months]
            floor_counts = [11, 0, 0, 0, 0, 2, 0, 0, 0, 7, 113, 49]
            monthly_contributions = list(zip(month_abbrs, floor_counts))
            total_contributions = _ca.get("contributions") or sum(floor_counts)

    return {
        "username": username,
        "followers": followers,
        "repositories": repo_count if repo_count > 0 else (_ca.get("repositories") or 22),
        "stars": total_stars if total_stars > 0 else (_ca.get("stars") or 0),
        "commits": total_commits if total_commits > 0 else (_ca.get("commits") or 254),
        "contributions": total_contributions,
        "monthly_contributions": monthly_contributions,
        "pull_requests": total_prs if total_prs > 0 else (_ca.get("pull_requests") or 7),
        "issues": total_issues if total_issues > 0 else (_ca.get("issues") or 9),
    }


def fetch_osu_stats(
    username: str = "Akiisqt",
    fallback_data: Optional[dict] = None,
    cached_data: Optional[dict] = None,
) -> Dict[str, Any]:
    _ca = cached_data or {}
    fallback = {
        "global_rank": _ca.get("global_rank") or 753550,
        "country_rank": _ca.get("country_rank") or 130493,
        "pp": _ca.get("pp") or 1300.62,
        "accuracy": _ca.get("accuracy") or 82.71,
        "play_count": _ca.get("play_count") or 4673,
        "level": _ca.get("level") or "56.78",
    }

    url = f"https://osu.ppy.sh/users/{username}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            page = resp.read().decode("utf-8")
            m = re.search(r'data-initial-data="([^"]+)"', page)
            if m:
                data_str = html.unescape(m.group(1))
                data = json.loads(data_str)
                user = data.get("user", {})
                st = user.get("statistics", {})
                lvl = st.get("level", {})
                return {
                    "global_rank": st.get("global_rank", fallback["global_rank"]),
                    "country_rank": st.get("country_rank", fallback["country_rank"]),
                    "pp": st.get("pp", fallback["pp"]),
                    "accuracy": st.get("hit_accuracy", fallback["accuracy"]),
                    "play_count": st.get("play_count", fallback["play_count"]),
                    "level": f"{lvl.get('current', 56)}.{lvl.get('progress', 78)}",
                }
    except Exception as e:
        print(f"[Warning] osu! stats fetch failed: {e}. Using cached data.", file=sys.stderr)

    return fallback


def fetch_steam_stats(
    custom_url: str = "akiisqt",
    fallback_data: Optional[dict] = None,
    cached_data: Optional[dict] = None,
) -> Dict[str, Any]:
    _ca = cached_data or {}
    fallback = {
        "level": _ca.get("level") or 66,
        "games_count": _ca.get("games_count") or 174,
        "top_games": _ca.get("top_games") or ["Overwatch®", "Factorio", "Papers, Please", "Counter-Strike 2"],
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    extracted_games: List[Tuple[str, float]] = []
    level = fallback["level"]
    games_count = fallback["games_count"]

    # Strategy 1: Steam Profile XML API (reliable, never rate-limited or blocked)
    try:
        xml_url = f"https://steamcommunity.com/id/{custom_url}/?xml=1"
        req_xml = urllib.request.Request(xml_url, headers=headers)
        with urllib.request.urlopen(req_xml, timeout=6) as resp:
            tree = ET.fromstring(resp.read())
            for g in tree.findall(".//mostPlayedGame"):
                name = g.findtext("gameName")
                hours_str = g.findtext("hoursOnRecord")
                if name:
                    hours = float(hours_str.replace(",", "")) if hours_str else 0.0
                    extracted_games.append((name.strip(), hours))
    except Exception as e:
        print(f"[Warning] Steam XML fetch failed: {e}", file=sys.stderr)

    # Strategy 2: Steam Community HTML Scraper (complementary source for level, total games, recent titles)
    try:
        html_url = f"https://steamcommunity.com/id/{custom_url}/"
        req_html = urllib.request.Request(html_url, headers=headers)
        with urllib.request.urlopen(req_html, timeout=6) as resp:
            page = resp.read().decode("utf-8")
            lvl_match = re.search(r'friendPlayerLevelNum\">(\d+)<', page)
            if lvl_match:
                level = int(lvl_match.group(1))

            games_match = re.search(r'(\d+)\s+games\s+in\s+library', page, re.IGNORECASE) or re.search(r'games\">[^\d]*(\d+)[^\d]*<', page)
            if games_match:
                games_count = int(games_match.group(1))

            for m in re.finditer(r'<div class="game_info_details">\s*([\d\.]+)\s*hrs on record.*?<div class="game_name"><a[^>]*>([^<]+)</a>', page, re.DOTALL):
                try:
                    hrs = float(m.group(1))
                    gname = m.group(2).strip()
                    if not any(g[0].lower() == gname.lower() for g in extracted_games):
                        extracted_games.append((gname, hrs))
                except (ValueError, IndexError):
                    continue
    except Exception as e:
        print(f"[Warning] Steam HTML scrape failed: {e}", file=sys.stderr)

    if extracted_games:
        games_sorted = sorted(extracted_games, key=lambda x: x[1], reverse=True)
        top_games = [g[0] for g in games_sorted[:3]]
    else:
        top_games = fallback["top_games"]

    return {
        "level": level,
        "games_count": games_count,
        "top_games": top_games,
    }


def fetch_youtube_music_stats(
    handle: str = "@Akiisqt",
    fallback_data: Optional[dict] = None,
    cached_data: Optional[dict] = None,
) -> Dict[str, Any]:
    _ca = cached_data or {}
    cached_artists_raw = _ca.get("artists_hours")
    if cached_artists_raw:
        artists_fallback = [(item[0], int(item[1])) for item in cached_artists_raw]
    else:
        artists_fallback = [
            ("The Presidents of The USA", 6),
            ("Linkin Park", 5),
            ("Disturbed", 1),
            ("System of A Down", 1),
            ("Red Hot Chili Peppers", 1),
        ]

    fallback = {
        "artist": _ca.get("artist") or "Linkin Park",
        "track": _ca.get("track") or "One Step Closer",
        "artists_hours": artists_fallback,
    }

    url = f"https://music.youtube.com/{handle}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html_text = resp.read().decode("utf-8")
            matches = re.findall(r"data:\s*'([^']+)'", html_text)
            if len(matches) > 1:
                raw_json = bytes(matches[1].replace(r"\/", "/"), "utf-8").decode("unicode_escape")
                parsed = json.loads(raw_json)
                tabs = parsed.get("contents", {}).get("singleColumnBrowseResultsRenderer", {}).get("tabs", [])
                if tabs:
                    sections = tabs[0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", [])
                    repeat_artists_hours = []
                    repeat_songs = []

                    for sec in sections:
                        shelf = sec.get("musicShelfRenderer") or sec.get("musicCarouselShelfRenderer")
                        if not shelf:
                            continue
                        header = shelf.get("header", {}).get("musicCarouselShelfBasicHeaderRenderer", {}).get("title", {}).get("runs", [{}])[0].get("text", "")
                        
                        if "musicShelfRenderer" in sec:
                            items = shelf.get("contents", [])
                            for it in items[:4]:
                                flex = it.get("musicResponsiveListItemRenderer", {}).get("flexColumns", [])
                                if len(flex) >= 2:
                                    s_title = flex[0]["musicResponsiveListItemFlexColumnRenderer"]["text"]["runs"][0]["text"]
                                    s_artist = flex[1]["musicResponsiveListItemFlexColumnRenderer"]["text"]["runs"][0]["text"]
                                    repeat_songs.append((s_title, s_artist))

                        if "Artists" in header:
                            for it in shelf.get("contents", [])[:5]:
                                r = it.get("musicTwoRowItemRenderer", {})
                                a_title = r.get("title", {}).get("runs", [{}])[0].get("text", "")
                                sub_runs = [x.get("text", "") for x in r.get("subtitle", {}).get("runs", [])]
                                sub_text = " ".join(sub_runs)
                                hr_match = re.search(r"(\d+)\s*hour", sub_text)
                                hours = int(hr_match.group(1)) if hr_match else 1
                                if a_title:
                                    repeat_artists_hours.append((a_title, hours))

                    if repeat_artists_hours or repeat_songs:
                        top_song = repeat_songs[0] if repeat_songs else (fallback["track"], fallback["artist"])
                        artists_final = repeat_artists_hours if repeat_artists_hours else fallback["artists_hours"]
                        return {
                            "track": top_song[0],
                            "artist": top_song[1] or fallback["artist"],
                            "artists_hours": artists_final,
                        }
    except Exception as e:
        print(f"[Warning] Live YouTube Music scrape error: {e}. Using fallback data.", file=sys.stderr)

    return fallback

