"""OpenCV camera capture manager with error handling."""
from __future__ import annotations

from typing import Optional

import cv2
import numpy as np


class CameraError(Exception):
    """Base camera error."""


class CameraInUseError(CameraError):
    """Camera is in use by another application."""


class CameraNotFoundError(CameraError):
    """No camera found on the system."""


class CameraPermissionError(CameraError):
    """Camera permission denied."""


class Camera:
    """Manages OpenCV camera capture with error handling."""

    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480) -> None:
        self._camera_id = camera_id
        self._width = width
        self._height = height
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        """Open camera. Raises CameraError subclasses on failure."""
        self._cap = cv2.VideoCapture(self._camera_id)
        if not self._cap.isOpened():
            self._cap = None
            raise CameraNotFoundError(
                f"Cannot open camera {self._camera_id}. "
                "No camera may be available, or permission may be denied."
            )
        # Set buffer size to 1 to prevent frame accumulation
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

    def read_frame(self) -> np.ndarray:
        """Read a single frame. Returns BGR numpy array."""
        if self._cap is None or not self._cap.isOpened():
            raise CameraError("Camera is not open. Call open() first.")
        ret, frame = self._cap.read()
        if not ret or frame is None:
            raise CameraError("Failed to read frame from camera.")
        return frame

    def release(self) -> None:
        """Release camera resources."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self) -> Camera:
        self.open()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> bool:
        self.release()
        return False

    @property
    def is_opened(self) -> bool:
        """Check if camera is currently open."""
        return self._cap is not None and self._cap.isOpened()
