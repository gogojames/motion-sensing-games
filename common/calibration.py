"""Body calibration screen - captures baseline pose measurements."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

# Landmark indices
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_HIP = 23
RIGHT_HIP = 24


@dataclass
class CalibrationData:
    """Baseline measurements captured during calibration."""

    shoulder_width: float
    standing_hip_y: float
    arm_span: float
    torso_angle: float
    confidence: float

    @property
    def is_valid(self) -> bool:
        """Check if calibration confidence is acceptable (>0.7)."""
        return self.confidence > 0.7


class CalibrationScreen:
    """2-second calibration flow that captures baseline pose measurements."""

    CALIBRATION_DURATION: float = 2.0

    def __init__(self) -> None:
        self._samples: list[Any] = []

    def run(self, pose_thread: Any, screen: Any = None) -> CalibrationData:
        """Run calibration for 2 seconds and return baseline measurements."""
        self._samples.clear()
        self._collect_samples(pose_thread, self.CALIBRATION_DURATION)
        w, h = 640, 480
        if hasattr(pose_thread, "frame_dimensions"):
            w, h = pose_thread.frame_dimensions
        return self._compute_calibration(w, h)

    def _collect_samples(self, pose_thread: Any, duration: float) -> None:
        """Collect pose samples for the given duration."""
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            pose = pose_thread.get_pose()
            if pose is not None:
                self._samples.append(pose)
            time.sleep(1.0 / 30.0)

    def _compute_calibration(self, width: int, height: int) -> CalibrationData:
        """Compute baseline measurements from collected samples."""
        if not self._samples:
            return CalibrationData(
                shoulder_width=0,
                standing_hip_y=0.5,
                arm_span=0,
                torso_angle=0,
                confidence=0.0,
            )
        shoulders: list[float] = []
        hip_ys: list[float] = []
        arm_spans: list[float] = []
        torso_angles: list[float] = []
        vis_scores: list[float] = []

        for pf in self._samples:
            lm = pf.landmarks
            ls = lm[LEFT_SHOULDER, :2] * np.array([width, height])
            rs = lm[RIGHT_SHOULDER, :2] * np.array([width, height])
            shoulders.append(float(np.linalg.norm(rs - ls)))

            hip_y = (lm[LEFT_HIP, 1] + lm[RIGHT_HIP, 1]) / 2.0
            hip_ys.append(float(hip_y))

            lw = lm[LEFT_WRIST, :2] * np.array([width, height])
            rw = lm[RIGHT_WRIST, :2] * np.array([width, height])
            arm_spans.append(float(np.linalg.norm(rw - lw)))

            mid_shoulder = (ls + rs) / 2.0
            mid_hip_y = hip_y * height
            dx = mid_shoulder[0] - width / 2.0
            dy = mid_shoulder[1] - mid_hip_y
            torso_angles.append(
                float(np.degrees(np.arctan2(abs(dx), abs(dy) + 1e-8)))
            )

            key_indices = [
                LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP,
                LEFT_WRIST, RIGHT_WRIST,
            ]
            vis_scores.append(float(np.mean([lm[i, 2] for i in key_indices])))

        confidence = float(np.mean(vis_scores))
        return CalibrationData(
            shoulder_width=float(np.mean(shoulders)),
            standing_hip_y=float(np.mean(hip_ys)),
            arm_span=float(np.max(arm_spans)) if arm_spans else 0.0,
            torso_angle=float(np.mean(torso_angles)),
            confidence=confidence,
        )

    def _render_countdown(self, screen: Any, elapsed: float) -> None:
        """Render countdown overlay. No-op if no pygame screen provided."""
        # Rendering integrated in game loop
