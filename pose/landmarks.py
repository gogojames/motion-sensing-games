"""Keypoint math utilities, gesture types, and gesture event definitions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np

# ── MediaPipe Pose Landmark indices (33 keypoints) ──────────────────────────
NOSE = 0
LEFT_EYE_INNER = 1
LEFT_EYE = 2
LEFT_EYE_OUTER = 3
RIGHT_EYE_INNER = 4
RIGHT_EYE = 5
RIGHT_EYE_OUTER = 6
LEFT_EAR = 7
RIGHT_EAR = 8
MOUTH_LEFT = 9
MOUTH_RIGHT = 10
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_PINKY = 17
RIGHT_PINKY = 18
LEFT_INDEX = 19
RIGHT_INDEX = 20
LEFT_THUMB = 21
RIGHT_THUMB = 22
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32


class GestureType(Enum):
    """All gesture types for both games."""

    # Fruit-slicing gestures
    HAND_BLADE = "hand_blade"
    HANDS_UP = "hands_up"
    WAVE_SELECT = "wave_select"

    # Conductor gestures
    LEFT_HAND_REACH = "left_reach"
    RIGHT_HAND_REACH = "right_reach"
    DUAL_HAND_SYNC = "dual_sync"
    SQUAT = "squat"
    ARMS_EXTEND = "arms_extend"

    # Calibration
    HANDS_UP_HOLD = "hands_up_hold"
    STANDING_NEUTRAL = "standing"


@dataclass
class GestureEvent:
    """An atomic action recognised by the gesture pipeline."""

    type: GestureType
    hand: Optional[str]
    position: tuple[float, float]
    velocity: float
    confidence: float
    timestamp: int


def normalize_landmarks(
    landmarks: np.ndarray, width: int, height: int
) -> np.ndarray:
    """Convert normalised [0, 1] landmarks to pixel coordinates."""
    out = landmarks.copy()
    out[:, 0] = landmarks[:, 0] * width
    out[:, 1] = landmarks[:, 1] * height
    return out


def _euclidean_2d(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance between two 2-D points."""
    return float(np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))


def wrist_velocity(
    landmarks_a: np.ndarray,
    landmarks_b: np.ndarray,
    dt_seconds: float,
    width: int,
    height: int,
) -> float:
    """Calculate hand velocity between two frames in pixels / sec.

    Uses wrist landmarks (15, 16). Picks the wrist with higher visibility
    in the current frame.
    """
    if dt_seconds <= 0:
        return 0.0
    pix_a = normalize_landmarks(landmarks_a, width, height)
    pix_b = normalize_landmarks(landmarks_b, width, height)
    vis_l = pix_b[LEFT_WRIST, 2]
    vis_r = pix_b[RIGHT_WRIST, 2]
    idx = LEFT_WRIST if vis_l >= vis_r else RIGHT_WRIST
    dist = _euclidean_2d(pix_a[idx], pix_b[idx])
    return dist / dt_seconds


def finger_direction(
    landmarks: np.ndarray,
    hand: str,
    width: int,
    height: int,
) -> Optional[tuple[float, float]]:
    """Direction vector from wrist to index finger tip, normalised."""
    if hand == "left":
        w_idx, f_idx = LEFT_WRIST, LEFT_INDEX
    elif hand == "right":
        w_idx, f_idx = RIGHT_WRIST, RIGHT_INDEX
    else:
        return None
    pix = normalize_landmarks(landmarks, width, height)
    if pix[w_idx, 2] < 0.5 or pix[f_idx, 2] < 0.5:
        return None
    dx = pix[f_idx, 0] - pix[w_idx, 0]
    dy = pix[f_idx, 1] - pix[w_idx, 1]
    length = np.sqrt(dx * dx + dy * dy)
    if length < 1e-6:
        return (0.0, 0.0)
    return (float(dx / length), float(dy / length))


def joint_angle(
    landmarks: np.ndarray,
    joint_a: int,
    joint_b: int,
    joint_c: int,
    width: int,
    height: int,
) -> float:
    """Angle at joint_b between segments A->B and B->C, in degrees."""
    pix = normalize_landmarks(landmarks, width, height)
    ba = pix[joint_a, :2] - pix[joint_b, :2]
    bc = pix[joint_c, :2] - pix[joint_b, :2]
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cos_angle = float(np.clip(cos_angle, -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_angle)))


def is_hand_blade(
    landmarks_a: np.ndarray,
    landmarks_b: np.ndarray,
    dt_seconds: float,
    width: int,
    height: int,
    velocity_threshold: float = 500.0,
) -> tuple[bool, float, str]:
    """Determine if a hand swipe occurred between two frames.

    Returns:
        (is_swipe, velocity, hand) where hand is "left", "right", or "both"
    """
    if dt_seconds <= 0:
        return False, 0.0, ""
    pix_a = normalize_landmarks(landmarks_a, width, height)
    pix_b = normalize_landmarks(landmarks_b, width, height)
    vel_l = _euclidean_2d(pix_a[LEFT_WRIST], pix_b[LEFT_WRIST]) / dt_seconds
    vel_r = _euclidean_2d(pix_a[RIGHT_WRIST], pix_b[RIGHT_WRIST]) / dt_seconds
    left_swipe = vel_l >= velocity_threshold
    right_swipe = vel_r >= velocity_threshold
    if left_swipe and right_swipe:
        return True, max(vel_l, vel_r), "both"
    if left_swipe:
        return True, vel_l, "left"
    if right_swipe:
        return True, vel_r, "right"
    return False, max(vel_l, vel_r), ""
