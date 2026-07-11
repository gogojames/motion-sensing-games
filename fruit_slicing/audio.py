"""Procedural sound effects for the fruit-slicing game."""
from __future__ import annotations

from typing import Optional

import numpy as np

_enabled: bool = True
_initialized: bool = False


def init_audio() -> None:
    """Initialise the pygame mixer for procedural audio synthesis."""
    global _initialized  # noqa: PLW0603
    if _initialized:
        return
    try:
        import pygame  # noqa: PLC0415

        pygame.mixer.pre_init(44100, -16, 2, 1024)
        _initialized = True
    except Exception:
        _initialized = False


def set_enabled(enabled: bool) -> None:
    """Enable or disable sound effects."""
    global _enabled  # noqa: PLW0603
    _enabled = enabled


def _make_sound(samples: np.ndarray) -> Optional[object]:
    """Create a pygame Sound from numpy samples."""
    if not _enabled or not _initialized:
        return None
    try:
        import pygame  # noqa: PLC0415

        stereo = np.column_stack((samples, samples)).astype(np.int16)
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


def play_slice_sound() -> None:
    """Play a short white-noise sweep (~100ms) for fruit slicing."""
    if not _enabled:
        return
    sr = 44100
    n = int(sr * 0.1)
    t = np.linspace(0, 0.1, n)
    freq = 2000 + 3000 * t / 0.1
    samples = (np.sin(2 * np.pi * freq * t) * 8000 * (1 - t / 0.1)).astype(np.int16)
    snd = _make_sound(samples)
    if snd is not None:
        snd.play()


def play_bomb_sound() -> None:
    """Play a low-frequency rumble (~300ms) for bomb explosion."""
    if not _enabled:
        return
    sr = 44100
    n = int(sr * 0.3)
    t = np.linspace(0, 0.3, n)
    noise = np.random.uniform(-4000, 4000, n)
    rumble = np.sin(2 * np.pi * 60 * t) * 6000
    env = np.exp(-3 * t)
    samples = ((rumble + noise) * env).clip(-32768, 32767).astype(np.int16)
    snd = _make_sound(samples)
    if snd is not None:
        snd.play()


def play_combo_chime(combo_level: int) -> None:
    """Play an ascending sine tone for combo milestones."""
    if not _enabled:
        return
    sr = 44100
    base_hz = 440 + combo_level * 80
    n = int(sr * 0.15)
    t = np.linspace(0, 0.15, n)
    samples = (np.sin(2 * np.pi * base_hz * t) * 6000 * (1 - t / 0.15)).astype(
        np.int16
    )
    snd = _make_sound(samples)
    if snd is not None:
        snd.play()


def play_golden_sound() -> None:
    """Play a sparkle arpeggio for golden watermelon."""
    if not _enabled:
        return
    sr = 44100
    notes = [880, 1100, 1320, 1760]
    all_samples = np.zeros(0, dtype=np.int16)
    for hz in notes:
        n = int(sr * 0.1)
        t = np.linspace(0, 0.1, n)
        wave = (np.sin(2 * np.pi * hz * t) * 5000 * (1 - t / 0.1)).astype(np.int16)
        all_samples = np.concatenate([all_samples, wave])
    snd = _make_sound(all_samples)
    if snd is not None:
        snd.play()


def play_miss_sound() -> None:
    """Play a descending tone for missed fruit."""
    if not _enabled:
        return
    sr = 44100
    n = int(sr * 0.2)
    t = np.linspace(0, 0.2, n)
    freq = 600 - 300 * t / 0.2
    samples = (np.sin(2 * np.pi * freq * t) * 4000 * (1 - t / 0.2)).astype(np.int16)
    snd = _make_sound(samples)
    if snd is not None:
        snd.play()


def play_menu_click() -> None:
    """Play a quick pop sound for menu selection."""
    if not _enabled:
        return
    sr = 44100
    n = int(sr * 0.05)
    t = np.linspace(0, 0.05, n)
    samples = (np.sin(2 * np.pi * 1000 * t) * 5000 * (1 - t / 0.05)).astype(np.int16)
    snd = _make_sound(samples)
    if snd is not None:
        snd.play()
