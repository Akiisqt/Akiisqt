"""
Cache management for last-retrieved API value persistence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from scripts.config import CACHE_FILE


def load_cache(cache_file: Optional[Path] = None) -> Dict[str, Any]:
    """Loads the most recently fetched API values from cache.json.
    Returns {} on any error (missing file, bad JSON, permission denied)."""
    target = cache_file or CACHE_FILE
    try:
        if target.is_file():
            return json.loads(target.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Warning] Could not read cache: {e}", file=sys.stderr)
    return {}


def save_cache(data: Dict[str, Any], cache_file: Optional[Path] = None) -> None:
    """Persists fetched API values to cache.json for use on future fetch failures."""
    target = cache_file or CACHE_FILE
    try:
        target.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    except Exception as e:
        print(f"[Warning] Could not write cache: {e}", file=sys.stderr)

