"""Unit tests for fruit_slicing/collision.py."""
from __future__ import annotations

import pytest

from fruit_slicing.collision import (
    _point_to_segment_distance as point_to_segment_distance,
    check_fruit_missed,
    check_swipe_bomb,
    check_swipe_fruit,
)
from fruit_slicing.entities import Bomb, Fruit, FruitType, HandBlade


def _make_fruit(x: float = 400.0, y: float = 300.0, radius: float = 30.0) -> Fruit:
    return Fruit(
        id=1,
        type=FruitType.WATERMELON,
        x=x, y=y,
        vx=0.0, vy=-2.0,
        radius=radius,
        rotation=0.0,
        rotation_speed=5.0,
        sliced=False,
        missed=False,
        trail=[],
    )


def _make_blade(
    start: tuple[float, float] = (100.0, 300.0),
    end: tuple[float, float] = (500.0, 300.0),
) -> HandBlade:
    return HandBlade(
        hand="right",
        start_pos=start,
        end_pos=end,
        velocity=800.0,
        lifetime=10,
        arc=[start, end],
    )


def _make_bomb(x: float = 400.0, y: float = 300.0) -> Bomb:
    return Bomb(
        x=x, y=y,
        vx=0.0, vy=-2.0,
        radius=35.0,
        rotation=0.0,
        rotation_speed=3.0,
        exploded=False,
    )


class TestPointToSegmentDistance:
    def test_point_on_segment(self) -> None:
        d = point_to_segment_distance(0.5, 0.0, 0.0, 0.0, 1.0, 0.0)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_point_above_segment(self) -> None:
        d = point_to_segment_distance(0.5, 1.0, 0.0, 0.0, 1.0, 0.0)
        assert d == pytest.approx(1.0, abs=1e-6)

    def test_point_beyond_endpoint(self) -> None:
        d = point_to_segment_distance(2.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        assert d == pytest.approx(1.0, abs=1e-6)

    def test_point_before_start(self) -> None:
        d = point_to_segment_distance(-1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        assert d == pytest.approx(1.0, abs=1e-6)


class TestCheckSwipeFruit:
    def test_swipe_through_fruit(self) -> None:
        fruit = _make_fruit(300.0, 300.0, 30.0)
        blade = _make_blade((100.0, 300.0), (500.0, 300.0))
        assert check_swipe_fruit(blade, fruit) is True

    def test_swipe_misses_fruit(self) -> None:
        fruit = _make_fruit(300.0, 100.0, 30.0)
        blade = _make_blade((100.0, 300.0), (500.0, 300.0))
        assert check_swipe_fruit(blade, fruit) is False

    def test_already_sliced_fruit(self) -> None:
        fruit = _make_fruit(300.0, 300.0, 30.0)
        fruit.sliced = True
        blade = _make_blade((100.0, 300.0), (500.0, 300.0))
        assert check_swipe_fruit(blade, fruit) is False

    def test_swipe_at_fruit_edge(self) -> None:
        fruit = _make_fruit(300.0, 300.0, 30.0)
        blade = _make_blade((100.0, 330.0), (500.0, 330.0))
        assert check_swipe_fruit(blade, fruit) is True


class TestCheckSwipeBomb:
    def test_swipe_through_bomb(self) -> None:
        bomb = _make_bomb(300.0, 300.0)
        blade = _make_blade((100.0, 300.0), (500.0, 300.0))
        assert check_swipe_bomb(blade, bomb) is True

    def test_swipe_misses_bomb(self) -> None:
        bomb = _make_bomb(300.0, 100.0)
        blade = _make_blade((100.0, 300.0), (500.0, 300.0))
        assert check_swipe_bomb(blade, bomb) is False

    def test_already_exploded(self) -> None:
        bomb = _make_bomb(300.0, 300.0)
        bomb.exploded = True
        blade = _make_blade((100.0, 300.0), (500.0, 300.0))
        assert check_swipe_bomb(blade, bomb) is False


class TestCheckFruitMissed:
    def test_fruit_below_screen(self) -> None:
        fruit = _make_fruit(400.0, 800.0)
        assert check_fruit_missed(fruit, 720) is True

    def test_fruit_on_screen(self) -> None:
        fruit = _make_fruit(400.0, 300.0)
        assert check_fruit_missed(fruit, 720) is False

    def test_fruit_just_above_bottom(self) -> None:
        fruit = _make_fruit(400.0, 719.0, radius=30.0)
        assert check_fruit_missed(fruit, 720) is False

    def test_fruit_with_large_radius(self) -> None:
        fruit = _make_fruit(400.0, 695.0, radius=30.0)
        assert check_fruit_missed(fruit, 720) is False
