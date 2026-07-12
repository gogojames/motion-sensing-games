"""Wave generation logic for the fruit-slicing game."""
from __future__ import annotations

import random
from typing import Optional

from fruit_slicing.entities import Fruit, FruitType, WaveConfig


def generate_wave(wave_number: int) -> WaveConfig:
    """Generate wave configuration with increasing difficulty."""
    diff = 1.0 + (wave_number - 1) * 0.15
    return WaveConfig(
        wave_number=wave_number,
        fruit_count=max(3, int(4 + wave_number * diff)),
        bomb_count=min(wave_number // 2, 4),
        golden_chance=0.05,
        min_speed=8.0 * diff,
        max_speed=14.0 * diff,
        spawn_interval=max(0.3, 1.0 / diff),
        trajectory_types=["arc", "straight", "lob"],
    )


_FRUIT_WEIGHTS = [
    (FruitType.WATERMELON, 35),
    (FruitType.ORANGE, 25),
    (FruitType.APPLE, 25),
    (FruitType.BANANA, 15),
]


def _pick_fruit_type(golden_chance: float, golden_spawned: bool) -> FruitType:
    if not golden_spawned and random.random() < golden_chance:
        return FruitType.GOLDEN_WATERMELON
    total = sum(w for _, w in _FRUIT_WEIGHTS)
    r = random.uniform(0, total)
    cumulative = 0
    for ft, weight in _FRUIT_WEIGHTS:
        cumulative += weight
        if r <= cumulative:
            return ft
    return FruitType.WATERMELON


def spawn_fruits(
    wave_config: WaveConfig,
    screen_width: int,
    screen_height: int,
    golden_spawned: bool = False,
) -> list[Fruit]:
    """Spawn a wave of fruits with randomised trajectories."""
    fruits: list[Fruit] = []
    margin = screen_width * 0.15
    spawn_zone_x = (margin, screen_width - margin)
    spawn_y = screen_height + 50

    for i in range(wave_config.fruit_count):
        x = random.uniform(*spawn_zone_x)
        speed = random.uniform(wave_config.min_speed, wave_config.max_speed)
        angle = random.uniform(-0.8, 0.8)
        vx = speed * 0.3 * angle
        vy = -speed
        fruit_type = _pick_fruit_type(wave_config.golden_chance, golden_spawned)
        radius = random.uniform(25, 40)
        fruits.append(
            Fruit(
                id=i,
                type=fruit_type,
                x=x,
                y=spawn_y,
                vx=vx,
                vy=vy,
                radius=radius,
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-3, 3),
            )
        )
    return fruits
