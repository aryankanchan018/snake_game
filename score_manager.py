# =============================================================================
# score_manager.py — Persistent score & statistics using JSON
# =============================================================================

import json
import os

SAVE_FILE = os.path.join(os.path.dirname(__file__), "stats.json")

_DEFAULTS = {
    "high_score":    0,
    "games_played":  0,
    "total_food":    0,
    "longest_snake": 0,
}


class ScoreManager:
    """Loads, updates, and persists game statistics."""

    def __init__(self):
        self._data = dict(_DEFAULTS)
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    saved = json.load(f)
                    # Merge to handle any new keys added in future versions
                    self._data.update({k: saved[k] for k in _DEFAULTS if k in saved})
            except (json.JSONDecodeError, IOError):
                pass  # Corrupt file — start fresh

    def save(self):
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(self._data, f, indent=2)
        except IOError:
            pass  # Non-fatal — running without write access

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def high_score(self) -> int:
        return self._data["high_score"]

    @property
    def games_played(self) -> int:
        return self._data["games_played"]

    @property
    def total_food(self) -> int:
        return self._data["total_food"]

    @property
    def longest_snake(self) -> int:
        return self._data["longest_snake"]

    def record_game(self, score: int, food_eaten: int, snake_length: int):
        """Call once at the end of every game session."""
        self._data["games_played"]  += 1
        self._data["total_food"]    += food_eaten
        if score > self._data["high_score"]:
            self._data["high_score"] = score
        if snake_length > self._data["longest_snake"]:
            self._data["longest_snake"] = snake_length
        self.save()
