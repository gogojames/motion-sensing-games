"""Native system UI dialogs and notification sounds."""
from __future__ import annotations

import subprocess
import sys

IS_MACOS: bool = sys.platform == "darwin"
IS_WINDOWS: bool = sys.platform == "win32"


def _escape_osascript(text: str) -> str:
    """Escape text for use in osascript commands."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def show_error(title: str, message: str) -> None:
    """Show a native error dialog."""
    if IS_MACOS:
        escaped_title = _escape_osascript(title)
        escaped_msg = _escape_osascript(message)
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display dialog "{escaped_msg}" with title "{escaped_title}" '
                f'buttons {{"OK"}} default button "OK" with icon stop',
            ],
            check=False,
        )
    elif IS_WINDOWS:
        import ctypes  # noqa: PLC0415 — only on Windows

        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)  # type: ignore[attr-defined]
    else:
        print(f"[ERROR] {title}: {message}", file=sys.stderr)


def show_camera_permission_error() -> None:
    """Show camera permission error with recovery instructions."""
    if IS_MACOS:
        msg = (
            "Camera access denied.\n\n"
            "To enable:\n"
            "1. Open System Settings > Privacy & Security > Camera\n"
            "2. Find Terminal (or your Python IDE)\n"
            "3. Toggle camera access ON\n\n"
            "Then restart the application."
        )
    else:
        msg = (
            "Camera access denied.\n\n"
            "To enable:\n"
            "1. Open Settings > Privacy > Camera\n"
            "2. Find your terminal/IDE application\n"
            "3. Toggle camera access ON\n\n"
            "Then restart the application."
        )
    show_error("Camera Permission Required", msg)


def show_camera_in_use_error() -> None:
    """Show error when camera is in use by another application."""
    msg = (
        "Camera is in use by another application.\n\n"
        "Please close any applications using the camera "
        "(Zoom, Teams, FaceTime, etc.) and try again."
    )
    show_error("Camera Unavailable", msg)


def play_notification_sound() -> None:
    """Play a system notification sound."""
    if IS_MACOS:
        subprocess.run(
            ["afplay", "/System/Library/Sounds/Glass.aiff"],
            check=False,
        )
    elif IS_WINDOWS:
        try:
            import winsound  # noqa: PLC0415 — only on Windows

            winsound.MessageBeep()
        except ImportError:
            pass
