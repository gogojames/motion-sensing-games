"""Scoring, combo, and multiplier logic for the fruit-slicing game."""
from __future__ import annotations

from fruit_slicing.entities import FruitSlicingState, FruitType


def calculate_score(fruit_type: FruitType, combo: int) -> int:
    """Calculate points for slicing a fruit at the given combo level."""
    base = fruit_type.points
    if combo >= 5:
        return base + 10
    if combo >= 2:
        return base + 5
    return base


def update_combo(state: FruitSlicingState, sliced: bool) -> None:
    """Update combo counter. Increment on slice, reset on miss."""
    if sliced:
        state.combo += 1
        state.max_combo = max(state.max_combo, state.combo)
    else:
        state.combo = 0


def on_fruit_sliced(state: FruitSlicingState, fruit_type: FruitType) -> int:
    """Process a fruit slice event. Returns points earned."""
    points = calculate_score(fruit_type, state.combo)
    update_combo(state, sliced=True)
    state.score += points
    state.fruits_sliced += 1
    return points


def on_fruit_missed(state: FruitSlicingState) -> None:
    """Process a fruit miss. Decrements lives."""
    update_combo(state, sliced=False)
    state.fruits_missed += 1
    state.lives -= 1


def on_bomb_hit(state: FruitSlicingState) -> None:
    """Process a bomb hit. Decrements lives and resets combo."""
    update_combo(state, sliced=False)
    state.lives -= 1


def calculate_final_score(state: FruitSlicingState) -> dict:
    """Return final score data for high-score record."""
    return {
        "score": state.score,
        "combo": state.max_combo,
        "fruits_sliced": state.fruits_sliced,
    }
