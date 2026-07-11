"""Unit tests for fruit_slicing/spawner.py."""
from __future__ import annotations

import pytest

from fruit_slicing.entities import FruitType
from fruit_slicing.spawner import generate_wave, spawn_fruits


class TestGenerateWave:
    def test_wave_1_defaults(self) -> None:
        wave = generate_wave(1)
        assert wave.wave_number == 1
        assert wave.fruit_count >= 3
        assert wave.bomb_count >= 0
        assert 0.0 < wave.golden_chance <= 0.1

    def test_difficulty_increases(self) -> None:
        w1 = generate_wave(1)
        w5 = generate_wave(5)
        assert w5.fruit_count >= w1.fruit_count
        assert w5.difficulty_multiplier > w1.difficulty_multiplier

    def test_bomb_count_increases(self) -> None:
        w1 = generate_wave(1)
        w10 = generate_wave(10)
        assert w10.bomb_count >= w1.bomb_count

    def test_difficulty_multiplier_formula(self) -> None:
        wave = generate_wave(5)
        expected = 1.0 + (5 - 1) * 0.15
        assert wave.difficulty_multiplier == pytest.approx(expected, abs=0.01)

    def test_spawn_interval_decreases(self) -> None:
        w1 = generate_wave(1)
        w10 = generate_wave(10)
        assert w10.spawn_interval <= w1.spawn_interval


class TestSpawnFruits:
    def test_correct_count(self) -> None:
        wave = generate_wave(1)
        fruits = spawn_fruits(wave, 1280, 720, False)
        assert len(fruits) == wave.fruit_count

    def test_fruits_in_screen_bounds(self) -> None:
        wave = generate_wave(3)
        fruits = spawn_fruits(wave, 1280, 720, False)
        for f in fruits:
            assert 0 <= f.x <= 1280
            assert f.y >= 0

    def test_golden_spawn_chance(self) -> None:
        golden_count = 0
        for _ in range(100):
            wave = generate_wave(5)
            fruits = spawn_fruits(wave, 1280, 720, False)
            golden_count += sum(1 for f in fruits if f.type == FruitType.GOLDEN_WATERMELON)
        assert golden_count > 0

    def test_no_golden_when_already_spawned(self) -> None:
        wave = generate_wave(5)
        fruits = spawn_fruits(wave, 1280, 720, True)
        golden = [f for f in fruits if f.type == FruitType.GOLDEN_WATERMELON]
        assert len(golden) == 0

    def test_fruits_have_valid_types(self) -> None:
        wave = generate_wave(1)
        fruits = spawn_fruits(wave, 1280, 720, False)
        valid_types = {FruitType.WATERMELON, FruitType.ORANGE, FruitType.APPLE, FruitType.BANANA, FruitType.GOLDEN_WATERMELON}
        for f in fruits:
            assert f.type in valid_types

    def test_fruits_have_radius(self) -> None:
        wave = generate_wave(1)
        fruits = spawn_fruits(wave, 1280, 720, False)
        for f in fruits:
            assert f.radius > 0
