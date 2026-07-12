"""Fruit-slicing game entities and data models."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class GamePhase(Enum):
    """Game state machine phases."""

    MENU = "menu"
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class FruitType(Enum):
    """Fruit types with point values and display colours."""

    WATERMELON = ("watermelon", 10, (34, 139, 34))
    ORANGE = ("orange", 20, (255, 165, 0))
    APPLE = ("apple", 15, (255, 0, 0))
    BANANA = ("banana", 15, (255, 255, 0))
    GOLDEN_WATERMELON = ("golden", 50, (255, 215, 0))

    def __init__(self, display_name: str, points: int, color: tuple[int, int, int]) -> None:
        self.display_name = display_name
        self.points = points
        self.color = color


@dataclass
class Fruit:
    """A spawned fruit target in the fruit-slicing game."""

    id: int
    type: FruitType
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    rotation: float = 0.0
    rotation_speed: float = 0.0
    sliced: bool = False
    missed: bool = False
    trail: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class Bomb:
    """A bomb object — hitting it ends the game."""

    x: float
    y: float
    vx: float
    vy: float
    radius: float
    rotation: float = 0.0
    rotation_speed: float = 0.0
    exploded: bool = False


@dataclass
class HandBlade:
    """Registered when wrist movement exceeds velocity threshold."""

    hand: str
    start_pos: tuple[float, float]
    end_pos: tuple[float, float]
    velocity: float
    lifetime: int = 10
    arc: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class WaveConfig:
    """Defines spawn pattern for a wave of fruits."""

    wave_number: int
    fruit_count: int
    bomb_count: int
    golden_chance: float
    min_speed: float
    max_speed: float
    spawn_interval: float
    trajectory_types: list[str] = field(default_factory=lambda: ["arc", "straight"])

    @property
    def difficulty_multiplier(self) -> float:
        return 1.0 + (self.wave_number - 1) * 0.15


@dataclass
class FruitSlicingState:
    """Complete game state for the fruit-slicing game."""

    phase: GamePhase = GamePhase.MENU
    lives: int = 3
    score: int = 0
    combo: int = 0
    max_combo: int = 0
    fruits_sliced: int = 0
    fruits_missed: int = 0
    wave: int = 1
    golden_fruit_spawned: bool = False
