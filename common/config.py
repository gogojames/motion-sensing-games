"""Platform detection, paths, and settings management."""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

IS_MACOS: bool = sys.platform == "darwin"
IS_WINDOWS: bool = sys.platform == "win32"


def get_data_dir() -> Path:
    """Return platform-appropriate user data directory, creating it if needed.

    macOS: ~/Library/Application Support/motion-sensing-games/
    Windows: %APPDATA%/motion-sensing-games/
    Linux/other: ~/.config/motion-sensing-games/
    """
    if IS_MACOS:
        base = Path.home() / "Library" / "Application Support"
    elif IS_WINDOWS:
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    else:
        base = Path.home() / ".config"
    data_dir = base / "motion-sensing-games"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_model_path() -> Path:
    """Return path to MediaPipe model file (relative to project root)."""
    return Path("models") / "pose_landmarker_lite.task"


@dataclass
class Settings:
    """Application settings matching config.json schema."""

    schema_version: int = 1
    camera_id: int = 0
    preferred_resolution: tuple[int, int] = (640, 480)
    fullscreen: bool = False
    sound_enabled: bool = True
    motion_sensitivity: float = 0.5
    model_path: str = "models/pose_landmarker_lite.task"


def load_settings() -> Settings:
    """Load settings from config.json in data dir, or return defaults."""
    config_path = get_data_dir() / "config.json"
    if not config_path.is_file():
        return Settings()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        resolution = tuple(data.get("preferred_resolution", [640, 480]))
        return Settings(
            schema_version=data.get("schema_version", 1),
            camera_id=data.get("camera_id", 0),
            preferred_resolution=(resolution[0], resolution[1]),
            fullscreen=data.get("fullscreen", False),
            sound_enabled=data.get("sound_enabled", True),
            motion_sensitivity=data.get("motion_sensitivity", 0.5),
            model_path=data.get("model_path", "models/pose_landmarker_lite.task"),
        )
    except (json.JSONDecodeError, KeyError, OSError):
        return Settings()


def save_settings(settings: Settings) -> None:
    """Save settings to config.json in data dir."""
    config_path = get_data_dir() / "config.json"
    data = asdict(settings)
    data["preferred_resolution"] = list(settings.preferred_resolution)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
