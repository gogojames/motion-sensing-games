"""Background pose detection thread running at 30 Hz."""
from __future__ import annotations

import queue
import threading
import time
from typing import Any, Optional


class PoseThread:
    """Daemon thread that captures camera frames and runs pose detection.

    Architecture:
        Camera read + MediaPipe inference run at 30 Hz in a daemon thread.
        Pose results are pushed to ``Queue(maxsize=2)`` (latest-frame-wins).
        The main thread calls ``get_pose()`` at 60 fps to consume the latest.
    """

    TARGET_HZ: float = 30.0

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._pose_queue: queue.Queue[Any] = queue.Queue(maxsize=2)
        self._frame_queue: queue.Queue[Any] = queue.Queue(maxsize=1)
        self._lock = threading.Lock()
        self._latest_pose: Any = None
        self._is_tracking: bool = False
        self._frame_width: int = 640
        self._frame_height: int = 480
        self._camera: Any = None
        self._detector: Any = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, camera: Any, detector: Any) -> None:
        """Start the background pose detection thread."""
        self._camera = camera
        self._detector = detector
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="pose-thread"
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the background thread and wait for it to finish."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def push_frame(self, frame: Any) -> None:
        """Push a camera frame for processing (latest-frame-wins)."""
        if not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except queue.Empty:
                pass
        try:
            self._frame_queue.put_nowait(frame)
        except queue.Full:
            pass

    def get_pose(self) -> Any:
        """Get the most recent PoseFrame, or ``None`` if nothing new."""
        try:
            return self._pose_queue.get_nowait()
        except queue.Empty:
            return None

    @property
    def is_tracking(self) -> bool:
        """Whether pose is currently being detected."""
        with self._lock:
            return self._is_tracking

    @property
    def frame_dimensions(self) -> tuple[int, int]:
        """Return (width, height) of the camera frame."""
        with self._lock:
            return self._frame_width, self._frame_height

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        """Main loop for the background thread at 30 Hz."""
        interval = 1.0 / self.TARGET_HZ
        while self._running:
            t0 = time.monotonic()
            frame = self._read_frame()
            if frame is not None:
                self._process_frame(frame)
            elapsed = time.monotonic() - t0
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _read_frame(self) -> Any:
        """Read a frame from the frame queue (non-blocking)."""
        try:
            return self._frame_queue.get_nowait()
        except queue.Empty:
            return None

    def _process_frame(self, frame: Any) -> None:
        """Run pose detection and push result to pose queue."""
        ts_ms = int(time.monotonic() * 1000)
        result = self._detector.detect(frame, ts_ms)
        with self._lock:
            self._is_tracking = result is not None
            if result is not None:
                self._latest_pose = result
                self._frame_width = frame.shape[1]
                self._frame_height = frame.shape[0]
        if result is not None:
            if not self._pose_queue.empty():
                try:
                    self._pose_queue.get_nowait()
                except queue.Empty:
                    pass
            try:
                self._pose_queue.put_nowait(result)
            except queue.Full:
                pass
