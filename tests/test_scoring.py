"""Unit tests for fruit_slicing/scoring.py and conductor/scoring.py."""
from __future__ import annotations

import pytest

from conductor.scoring import ConductorScorer, StarPower
from conductor.targets import StarTargetType
from fruit_slicing.entities import FruitSlicingState, FruitType, GamePhase
from fruit_slicing.scoring import calculate_score, calculate_final_score, update_combo


class TestFruitSlicingScore:
    def test_base_score_watermelon(self) -> None:
        pts = calculate_score(FruitType.WATERMELON, 0)
        assert pts == 10

    def test_base_score_orange(self) -> None:
        pts = calculate_score(FruitType.ORANGE, 0)
        assert pts == 20

    def test_base_score_golden(self) -> None:
        pts = calculate_score(FruitType.GOLDEN_WATERMELON, 0)
        assert pts == 50

    def test_combo_bonus_at_2(self) -> None:
        pts = calculate_score(FruitType.WATERMELON, 2)
        assert pts >= 15

    def test_combo_bonus_at_5(self) -> None:
        pts = calculate_score(FruitType.WATERMELON, 5)
        assert pts >= 20


class TestConductorScoring:
    def test_hit_increases_score(self) -> None:
        scorer = ConductorScorer()
        pts = scorer.on_hit(StarTargetType.LEFT_HAND, 1.0)
        assert pts > 0
        assert scorer.score == pts

    def test_perfect_timing_bonus(self) -> None:
        scorer = ConductorScorer()
        pts_perfect = scorer.on_hit(StarTargetType.LEFT_HAND, 1.0)
        scorer2 = ConductorScorer()
        pts_ok = scorer2.on_hit(StarTargetType.LEFT_HAND, 0.3)
        assert pts_perfect > pts_ok

    def test_combo_increases(self) -> None:
        scorer = ConductorScorer()
        scorer.on_hit(StarTargetType.LEFT_HAND, 0.8)
        scorer.on_hit(StarTargetType.RIGHT_HAND, 0.8)
        assert scorer.combo == 2

    def test_miss_resets_combo(self) -> None:
        scorer = ConductorScorer()
        scorer.on_hit(StarTargetType.LEFT_HAND, 0.8)
        scorer.on_hit(StarTargetType.RIGHT_HAND, 0.8)
        scorer.on_miss()
        assert scorer.combo == 0

    def test_max_combo_tracked(self) -> None:
        scorer = ConductorScorer()
        for _ in range(5):
            scorer.on_hit(StarTargetType.LEFT_HAND, 0.8)
        scorer.on_miss()
        assert scorer.max_combo == 5

    def test_rank_s(self) -> None:
        assert ConductorScorer.calculate_rank(9000) == "S"
        assert ConductorScorer.calculate_rank(15000) == "S"

    def test_rank_a(self) -> None:
        assert ConductorScorer.calculate_rank(7000) == "A"
        assert ConductorScorer.calculate_rank(8999) == "A"

    def test_rank_b(self) -> None:
        assert ConductorScorer.calculate_rank(5000) == "B"
        assert ConductorScorer.calculate_rank(6999) == "B"

    def test_rank_c(self) -> None:
        assert ConductorScorer.calculate_rank(3000) == "C"

    def test_rank_d(self) -> None:
        assert ConductorScorer.calculate_rank(1000) == "D"

    def test_rank_f(self) -> None:
        assert ConductorScorer.calculate_rank(0) == "F"
        assert ConductorScorer.calculate_rank(999) == "F"

    def test_star_power_fill(self) -> None:
        scorer = ConductorScorer()
        initial = scorer.star_power
        scorer.on_hit(StarTargetType.LEFT_HAND, 1.0)
        assert scorer.star_power > initial

    def test_star_power_decay(self) -> None:
        scorer = ConductorScorer()
        scorer.on_hit(StarTargetType.LEFT_HAND, 1.0)
        before = scorer.star_power
        scorer.update_star_power(1.0)
        assert scorer.star_power < before

    def test_supernova_triggers(self) -> None:
        scorer = ConductorScorer()
        for _ in range(20):
            scorer.on_hit(StarTargetType.LEFT_HAND, 1.0)
        assert scorer.supernova_active is True

    def test_final_result_keys(self) -> None:
        scorer = ConductorScorer()
        result = scorer.get_final_result()
        assert "score" in result
        assert "rank" in result
        assert "max_combo" in result
        assert "track_name" in result


class TestFinalScore:
    def test_calculate_final_score(self) -> None:
        state = FruitSlicingState()
        state.phase = GamePhase.PLAYING
        state.score = 100
        state.combo = 5
        state.max_combo = 8
        state.fruits_sliced = 12
        result = calculate_final_score(state)
        assert result["score"] == 100
        assert result["combo"] == 8
        assert result["fruits_sliced"] == 12
