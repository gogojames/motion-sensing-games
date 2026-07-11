"""High score persistence - read/write data/highscores.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

DEFAULT_SCORES: dict[str, Any] = {
    "schema_version": 1,
    "fruit_slicing": {"top_scores": [], "max_entries": 10},
    "conductor": {"top_scores": [], "max_entries": 10},
}


class ScoreManager:
    """Manages high score persistence for both game modes."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            from common.config import get_data_dir  # noqa: PLC0415

            data_dir = get_data_dir()
        self._data_dir = data_dir

    def _get_file_path(self) -> Path:
        """Return path to highscores.json."""
        return self._data_dir / "highscores.json"

    def load(self) -> dict[str, Any]:
        """Load highscores from disk. Returns default if file missing/malformed."""
        path = self._get_file_path()
        if not path.is_file():
            return json.loads(json.dumps(DEFAULT_SCORES))
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key in ("fruit_slicing", "conductor"):
                if key not in data:
                    data[key] = DEFAULT_SCORES[key]
            return data
        except (json.JSONDecodeError, OSError):
            return json.loads(json.dumps(DEFAULT_SCORES))

    def save(self, scores: dict[str, Any]) -> None:
        """Save highscores to disk."""
        path = self._get_file_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)

    def update_highscore(self, game_mode: str, score_entry: dict[str, Any]) -> bool:
        """Update high scores for a game mode.

        Returns True if this was a new high score (entered the top 10).
        """
        scores = self.load()
        mode_data = scores.setdefault(
            game_mode, {"top_scores": [], "max_entries": 10}
        )
        top = mode_data.setdefault("top_scores", [])
        max_entries = mode_data.get("max_entries", 10)
        top.append(score_entry)
        top.sort(key=lambda e: e.get("score", 0), reverse=True)
        mode_data["top_scores"] = top[:max_entries]
        is_new_high = top[0] is score_entry if top else False
        self.save(scores)
        return is_new_high

    def get_best_score(self, game_mode: str) -> Optional[int]:
        """Return the best score for a game mode, or None if no scores."""
        scores = self.load()
        top = scores.get(game_mode, {}).get("top_scores", [])
        if not top:
            return None
        return max(e.get("score", 0) for e in top)

    def get_top_scores(self, game_mode: str, limit: int = 10) -> list[dict[str, Any]]:
        """Return top N scores for a game mode."""
        scores = self.load()
        return scores.get(game_mode, {}).get("top_scores", [])[:limit]
