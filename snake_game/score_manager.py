# =============================================================================
# snake_game/score_manager.py — Persistent score & statistics (JSON)
# =============================================================================

import json
import os
import sys

# Detect WebAssembly / Pygbag environment
_IS_WEB = sys.platform in ("emscripten", "wasi")

_DEFAULTS = {
    "high_score":    0,
    "games_played":  0,
    "total_food":    0,
    "longest_snake": 0,
}


class ScoreManager:
    """
    Loads, updates, and persists game statistics.
    - Desktop: saves to data/stats.json
    - Browser (Pygbag/WASM): keeps stats in memory only (no file I/O)
    """

    def __init__(self):
        self._data = dict(_DEFAULTS)
        if not _IS_WEB:
            from snake_game.constants import DATA_DIR
            self._save_file = os.path.join(DATA_DIR, "stats.json")
            os.makedirs(DATA_DIR, exist_ok=True)
            self._load()
        else:
            self._save_file = None

    def _load(self):
        if self._save_file and os.path.exists(self._save_file):
            try:
                with open(self._save_file, "r") as f:
                    saved = json.load(f)
                self._data.update({k: saved[k] for k in _DEFAULTS if k in saved})
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        if not self._save_file:
            return   # Web — in-memory only
        try:
            with open(self._save_file, "w") as f:
                json.dump(self._data, f, indent=2)
        except IOError:
            pass

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
        self._data["games_played"] += 1
        self._data["total_food"]   += food_eaten
        if score > self._data["high_score"]:
            self._data["high_score"] = score
        if snake_length > self._data["longest_snake"]:
            self._data["longest_snake"] = snake_length
        self.save()
