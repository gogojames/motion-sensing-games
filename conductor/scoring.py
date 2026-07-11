"""Scoring engine for the conductor game."""
from __future__ import annotations

from dataclasses import dataclass

from conductor.targets import StarTargetType


@dataclass
class StarPower:
    """Star power meter — fills on hits, decays over time."""
    current: float = 0.0
    decay_rate: float = 0.05
    fill_rate: float = 0.08
    supernova_threshold: float = 1.0
    supernova_duration: float = 8.0


class ConductorScorer:
    """Tracks score, combo, and star power for the conductor game."""

    def __init__(self) -> None:
        self._score: int = 0
        self._combo: int = 0
        self._max_combo: int = 0
        self._star_power = StarPower()
        self._supernova_active: bool = False
        self._supernova_timer: float = 0.0
        self._total_hits: int = 0
        self._total_misses: int = 0

    @property
    def score(self) -> int:
        return self._score

    @property
    def combo(self) -> int:
        return self._combo

    @property
    def max_combo(self) -> int:
        return self._max_combo

    @property
    def star_power(self) -> float:
        return self._star_power.current

    @property
    def supernova_active(self) -> bool:
        return self._supernova_active

    def on_hit(self, target_type: StarTargetType, timing_accuracy: float) -> int:
        """Process a successful hit. timing_accuracy: 1.0=perfect, 0.0=worst. Returns points earned."""
        self._combo += 1
        self._max_combo = max(self._max_combo, self._combo)
        self._total_hits += 1

        base = target_type.base_points
        timing_bonus = int(timing_accuracy * 15)
        combo_bonus = min(self._combo * 2, 30)
        points = base + timing_bonus + combo_bonus

        self._score += points
        self._star_power.current = min(
            self._star_power.supernova_threshold,
            self._star_power.current + self._star_power.fill_rate,
        )

        if self._star_power.current >= self._star_power.supernova_threshold:
            self.trigger_supernova()

        return points

    def on_miss(self) -> None:
        """Process a missed note."""
        self._combo = 0
        self._total_misses += 1

    def trigger_supernova(self) -> None:
        """Activate supernova mode."""
        self._supernova_active = True
        self._supernova_timer = self._star_power.supernova_duration
        self._star_power.current = 0.0

    def update_star_power(self, dt: float) -> None:
        """Decay star power and advance supernova timer."""
        if self._supernova_active:
            self._supernova_timer -= dt
            if self._supernova_timer <= 0:
                self._supernova_active = False
                self._supernova_timer = 0.0
        else:
            self._star_power.current = max(
                0.0,
                self._star_power.current - self._star_power.decay_rate * dt,
            )

    @staticmethod
    def calculate_rank(score: int) -> str:
        """Map score to rank letter per data-model.md."""
        if score >= 9000:
            return "S"
        if score >= 7000:
            return "A"
        if score >= 5000:
            return "B"
        if score >= 3000:
            return "C"
        if score >= 1000:
            return "D"
        return "F"

    def get_final_result(self) -> dict[str, object]:
        """Return final score summary for display and persistence."""
        return {
            "score": self._score,
            "rank": self.calculate_rank(self._score),
            "max_combo": self._max_combo,
            "track_name": "Star Voyage",
            "total_hits": self._total_hits,
            "total_misses": self._total_misses,
        }
