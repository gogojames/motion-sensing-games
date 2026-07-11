"""One-time MediaPipe model download with progress display."""
from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Callable, Optional

MODEL_URL: str = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/latest/"
    "pose_landmarker_lite.task"
)
MODEL_SIZE_MB: float = 5.5


class DownloadError(Exception):
    """Model download failed."""


def get_model_path() -> Path:
    """Return the path where the model file should be stored."""
    return Path("models") / "pose_landmarker_lite.task"


def is_model_downloaded() -> bool:
    """Check if the model file already exists."""
    return get_model_path().is_file()


def ensure_model(
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Path:
    """Ensure the model is downloaded. Returns path to model file.

    Args:
        progress_callback: Called with progress 0.0-1.0 during download.

    Raises:
        DownloadError: If download fails.
    """
    path = get_model_path()
    if path.is_file():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    _download_with_progress(MODEL_URL, path, progress_callback)
    if not path.is_file():
        raise DownloadError("Download completed but model file not found.")
    return path


def _download_with_progress(
    url: str,
    dest: Path,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> None:
    """Download a file with optional progress reporting."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "motion-sensing-games/1.0"}
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 65536
            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total > 0:
                        progress_callback(downloaded / total)
    except (urllib.error.URLError, OSError) as exc:
        if dest.is_file():
            dest.unlink()
        raise DownloadError(
            f"Failed to download model: {exc}. "
            "Check your internet connection and try again."
        ) from exc
