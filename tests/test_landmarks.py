"""Unit tests for pose/landmarks.py."""
from __future__ import annotations

import math

import numpy as np
import pytest

from pose.landmarks import (
    LEFT_ANKLE,
    LEFT_ELBOW,
    LEFT_HIP,
    LEFT_INDEX,
    LEFT_KNEE,
    LEFT_SHOULDER,
    LEFT_WRIST,
    RIGHT_ANKLE,
    RIGHT_ELBOW,
    RIGHT_HIP,
    RIGHT_INDEX,
    RIGHT_KNEE,
    RIGHT_SHOULDER,
    RIGHT_WRIST,
    GestureType,
    finger_direction,
    is_hand_blade,
    joint_angle,
    normalize_landmarks,
    wrist_velocity,
)

WIDTH = 640
HEIGHT = 480


@pytest.fixture
def standing_pose() -> np.ndarray:
    pose = np.zeros((33, 3), dtype=np.float64)
    pose[LEFT_SHOULDER] = [0.35, 0.30, 0.0]
    pose[RIGHT_SHOULDER] = [0.65, 0.30, 0.0]
    pose[LEFT_ELBOW] = [0.25, 0.50, 0.0]
    pose[RIGHT_ELBOW] = [0.75, 0.50, 0.0]
    pose[LEFT_WRIST] = [0.20, 0.65, 0.0]
    pose[RIGHT_WRIST] = [0.80, 0.65, 0.0]
    pose[LEFT_INDEX] = [0.18, 0.70, 0.0]
    pose[RIGHT_INDEX] = [0.82, 0.70, 0.0]
    pose[LEFT_HIP] = [0.40, 0.55, 0.0]
    pose[RIGHT_HIP] = [0.60, 0.55, 0.0]
    pose[LEFT_KNEE] = [0.40, 0.75, 0.0]
    pose[RIGHT_KNEE] = [0.60, 0.75, 0.0]
    pose[LEFT_ANKLE] = [0.40, 0.95, 0.0]
    pose[RIGHT_ANKLE] = [0.60, 0.95, 0.0]
    pose[:, 2] = 1.0
    return pose


class TestWristVelocity:
    def test_zero_movement(self, standing_pose: np.ndarray) -> None:
        vel = wrist_velocity(standing_pose, standing_pose, 0.033, WIDTH, HEIGHT)
        assert vel == pytest.approx(0.0, abs=1e-6)

    def test_horizontal_movement(self, standing_pose: np.ndarray) -> None:
        moved = standing_pose.copy()
        moved[LEFT_WRIST, 0] += 0.1
        moved[RIGHT_WRIST, 0] += 0.1
        vel = wrist_velocity(standing_pose, moved, 1.0, WIDTH, HEIGHT)
        assert vel > 0.0

    def test_both_wrists_contribute(self, standing_pose: np.ndarray) -> None:
        moved_l = standing_pose.copy()
        moved_l[LEFT_WRIST, 0] += 0.1
        vel_l = wrist_velocity(standing_pose, moved_l, 1.0, WIDTH, HEIGHT)

        moved_both = standing_pose.copy()
        moved_both[LEFT_WRIST, 0] += 0.1
        moved_both[RIGHT_WRIST, 0] += 0.1
        vel_both = wrist_velocity(standing_pose, moved_both, 1.0, WIDTH, HEIGHT)
        assert vel_both >= vel_l


class TestFingerDirection:
    def test_points_from_wrist_to_index(self, standing_pose: np.ndarray) -> None:
        direction = finger_direction(standing_pose, "left", WIDTH, HEIGHT)
        assert direction is not None
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        assert length == pytest.approx(1.0, abs=1e-6)

    def test_right_hand(self, standing_pose: np.ndarray) -> None:
        direction = finger_direction(standing_pose, "right", WIDTH, HEIGHT)
        assert direction is not None


class TestJointAngle:
    def test_right_angle(self) -> None:
        pose = np.zeros((33, 3), dtype=np.float64)
        pose[0] = [0.0, 0.0, 1.0]
        pose[1] = [0.5, 0.0, 1.0]
        pose[2] = [0.5, 0.5, 1.0]
        angle = joint_angle(pose, 0, 1, 2, WIDTH, HEIGHT)
        assert angle == pytest.approx(90.0, abs=5.0)

    def test_straight_line(self) -> None:
        pose = np.zeros((33, 3), dtype=np.float64)
        pose[0] = [0.0, 0.5, 1.0]
        pose[1] = [0.5, 0.5, 1.0]
        pose[2] = [1.0, 0.5, 1.0]
        angle = joint_angle(pose, 0, 1, 2, WIDTH, HEIGHT)
        assert angle == pytest.approx(180.0, abs=5.0)

    def test_acute_angle(self) -> None:
        pose = np.zeros((33, 3), dtype=np.float64)
        pose[0] = [0.0, 0.5, 1.0]
        pose[1] = [0.5, 0.5, 1.0]
        pose[2] = [0.7, 0.2, 1.0]
        angle = joint_angle(pose, 0, 1, 2, WIDTH, HEIGHT)
        assert 0.0 < angle < 180.0


class TestNormalizeLandmarks:
    def test_scales_to_pixel_space(self) -> None:
        lm = np.array([[0.5, 0.5, 1.0], [0.0, 0.0, 1.0]], dtype=np.float64)
        pixel = normalize_landmarks(lm, 640, 480)
        assert pixel[0, 0] == pytest.approx(320.0, abs=0.1)
        assert pixel[0, 1] == pytest.approx(240.0, abs=0.1)
        assert pixel[1, 0] == pytest.approx(0.0, abs=0.1)


class TestHandBlade:
    def test_fast_swipe_detected(self, standing_pose: np.ndarray) -> None:
        moved = standing_pose.copy()
        moved[LEFT_WRIST, 0] += 0.15
        swipe, velocity, hand = is_hand_blade(standing_pose, moved, 0.033, WIDTH, HEIGHT, velocity_threshold=100.0)
        assert swipe is True
        assert velocity > 0

    def test_slow_movement_not_detected(self, standing_pose: np.ndarray) -> None:
        moved = standing_pose.copy()
        moved[LEFT_WRIST, 0] += 0.001
        swipe, velocity, hand = is_hand_blade(standing_pose, moved, 0.033, WIDTH, HEIGHT, velocity_threshold=5000.0)
        assert swipe is False

    def test_no_movement(self, standing_pose: np.ndarray) -> None:
        swipe, velocity, hand = is_hand_blade(standing_pose, standing_pose, 0.033, WIDTH, HEIGHT)
        assert swipe is False


class TestGestureType:
    def test_all_types_exist(self) -> None:
        expected = {
            "HAND_BLADE", "HANDS_UP", "WAVE_SELECT",
            "LEFT_HAND_REACH", "RIGHT_HAND_REACH",
            "DUAL_HAND_SYNC", "SQUAT", "ARMS_EXTEND",
            "HANDS_UP_HOLD", "STANDING_NEUTRAL",
        }
        actual = {gt.name for gt in GestureType}
        assert expected == actual
