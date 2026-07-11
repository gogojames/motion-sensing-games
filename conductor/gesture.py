"""Full-body gesture classifier for the conductor game."""
from __future__ import annotations

from typing import Optional

import numpy as np

from common.calibration import CalibrationData
from pose.landmarks import GestureEvent, GestureType, joint_angle


class ConductorGestureClassifier:
    """Classifies conductor-specific gestures from pose landmarks."""

    def __init__(self, calibration: CalibrationData) -> None:
        self._calibration = calibration
        self._arms_extend_start: float | None = None
        self._arms_extend_hold: float = 0.5

    def classify(
        self,
        pose: np.ndarray,
        current_time: float,
        dt: float,
        width: int = 1280,
        height: int = 720,
    ) -> Optional[GestureEvent]:
        """Classify gesture from 33×3 landmarks array. Returns None if no gesture."""
        wrist_l = pose[15]
        wrist_r = pose[16]
        hip_l = pose[23]
        hip_r = pose[24]
        shoulder_l = pose[11]
        shoulder_r = pose[12]
        elbow_l = pose[13]
        elbow_r = pose[14]

        hip_y_avg = (hip_l[1] + hip_r[1]) / 2.0
        squat_threshold = self._calibration.standing_hip_y + 0.12

        if hip_y_avg > squat_threshold:
            speed = abs(hip_y_avg - self._calibration.standing_hip_y) / max(dt, 0.001)
            return GestureEvent(
                type=GestureType.SQUAT,
                hand=None,
                position=(0.5, hip_y_avg),
                velocity=speed,
                confidence=min(1.0, speed / 0.3),
                timestamp=int(current_time * 1000),
            )

        arm_span = self._calibration.arm_span
        if arm_span > 0:
            wrist_distance = abs(wrist_l[0] - wrist_r[0])
            left_angle = joint_angle(pose, 11, 13, 15, width, height)
            right_angle = joint_angle(pose, 12, 14, 16, width, height)
            arms_out = (left_angle > 120.0) and (right_angle > 120.0) and (wrist_distance > arm_span * 0.75)

            if arms_out:
                if self._arms_extend_start is None:
                    self._arms_extend_start = current_time
                elif (current_time - self._arms_extend_start) >= self._arms_extend_hold:
                    return GestureEvent(
                        type=GestureType.ARMS_EXTEND,
                        hand="both",
                        position=((wrist_l[0] + wrist_r[0]) / 2, (wrist_l[1] + wrist_r[1]) / 2),
                        velocity=wrist_distance / max(dt, 0.001),
                        confidence=0.9,
                        timestamp=int(current_time * 1000),
                    )
            else:
                self._arms_extend_start = None

        hand_sync_threshold = 0.15
        wrist_proximity = abs(wrist_l[0] - wrist_r[0])
        wrist_y_diff = abs(wrist_l[1] - wrist_r[1])
        both_hands_up = (wrist_l[1] < 0.4) and (wrist_r[1] < 0.4)

        if wrist_proximity < hand_sync_threshold and wrist_y_diff < 0.08 and both_hands_up:
            mid_x = (wrist_l[0] + wrist_r[0]) / 2
            mid_y = (wrist_l[1] + wrist_r[1]) / 2
            speed = np.sqrt(
                (wrist_l[0] - wrist_r[0]) ** 2 + (wrist_l[1] - wrist_r[1]) ** 2
            ) / max(dt, 0.001)
            return GestureEvent(
                type=GestureType.DUAL_HAND_SYNC,
                hand="both",
                position=(mid_x, mid_y),
                velocity=speed,
                confidence=0.85,
                timestamp=int(current_time * 1000),
            )

        if wrist_l[1] < 0.35:
            return GestureEvent(
                type=GestureType.LEFT_HAND_REACH,
                hand="left",
                position=(wrist_l[0], wrist_l[1]),
                velocity=0.0,
                confidence=0.8,
                timestamp=int(current_time * 1000),
            )

        if wrist_r[1] < 0.35:
            return GestureEvent(
                type=GestureType.RIGHT_HAND_REACH,
                hand="right",
                position=(wrist_r[0], wrist_r[1]),
                velocity=0.0,
                confidence=0.8,
                timestamp=int(current_time * 1000),
            )

        return None
