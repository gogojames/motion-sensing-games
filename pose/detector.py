"""MediaPipe Pose Landmarker wrapper for synchronous detection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import cv2
import numpy as np

try:
    from mediapipe.tasks.python import BaseOptions
    from mediapipe.tasks.python import vision as mp_vision

    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False


@dataclass
class PoseFrame:
    """Output of a single MediaPipe Pose Landmarker inference cycle.

    Attributes:
        landmarks: shape (33, 3) with [x_norm, y_norm, visibility]
        world_landmarks: shape (33, 3) with [x_m, y_m, z_m] in meters
        timestamp_ms: capture timestamp for velocity computation
    """

    landmarks: np.ndarray
    world_landmarks: np.ndarray
    timestamp_ms: int


class PoseDetector:
    """Synchronous Pose Landmarker using RunningMode.VIDEO.

    Uses detect_for_video() for deterministic output per input frame.
    This avoids the frame-dropping behaviour of LIVE_STREAM mode.
    """

    def __init__(
        self,
        model_path: str,
        num_poses: int = 1,
        min_detection_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        if not HAS_MEDIAPIPE:
            raise ImportError(
                "mediapipe-tasks is required. "
                "Install with: pip install mediapipe-tasks>=0.10.0"
            )
        options = mp_vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_poses=num_poses,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=min_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._detector = mp_vision.PoseLandmarker.create_from_options(options)

    def detect(self, frame: np.ndarray, timestamp_ms: int) -> Optional[PoseFrame]:
        """Detect pose in a single frame.

        Args:
            frame: BGR numpy array from camera (H, W, 3)
            timestamp_ms: Frame timestamp in milliseconds

        Returns:
            PoseFrame if pose detected, None otherwise
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp_vision.Image(image_format=mp_vision.ImageFormat.SRGB, data=rgb)
        result = self._detector.detect_for_video(mp_image, timestamp_ms)
        if not result.pose_landmarks:
            return None
        lm = result.pose_landmarks[0]
        landmarks = np.array(
            [[p.x, p.y, p.visibility] for p in lm], dtype=np.float64
        )
        wl = result.pose_world_landmarks[0]
        world_landmarks = np.array(
            [[p.x, p.y, p.z] for p in wl], dtype=np.float64
        )
        return PoseFrame(
            landmarks=landmarks,
            world_landmarks=world_landmarks,
            timestamp_ms=timestamp_ms,
        )

    def warmup(
        self,
        frame_generator: Callable[[], Optional[tuple[np.ndarray, int]]],
        num_frames: int = 10,
    ) -> None:
        """Warm up the detector with dummy frames to avoid cold-start latency."""
        for _ in range(num_frames):
            pair = frame_generator()
            if pair is None:
                break
            frame, ts = pair
            self.detect(frame, ts)

    def close(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, "_detector") and self._detector is not None:
            self._detector.close()
