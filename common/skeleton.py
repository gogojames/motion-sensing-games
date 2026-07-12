"""Real-time pose skeleton renderer for pygame surfaces."""
from __future__ import annotations

from typing import Any

import numpy as np

# MediaPipe Pose Landmark connections (35 bone pairs)
POSE_CONNECTIONS: list[tuple[int, int]] = [
    # Face
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    # Torso
    (11, 12), (11, 23), (12, 24), (23, 24),
    # Left arm
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    # Right arm
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    # Left leg
    (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),
    # Right leg
    (24, 26), (26, 28), (28, 30), (30, 32), (28, 32),
]

# Color scheme by body region
COLORS: dict[str, tuple[int, int, int]] = {
    "face": (255, 255, 255),
    "torso": (100, 200, 255),
    "left_arm": (0, 255, 0),
    "right_arm": (255, 0, 0),
    "left_leg": (0, 150, 255),
    "right_leg": (255, 150, 0),
}

# Landmark index ranges for each body region
_FACE_INDICES = set(range(11))
_TORSO_INDICES = {11, 12, 23, 24}
_LEFT_ARM_INDICES = {13, 15, 17, 19, 21}
_RIGHT_ARM_INDICES = {14, 16, 18, 20, 22}
_LEFT_LEG_INDICES = {25, 27, 29, 31}
_RIGHT_LEG_INDICES = {26, 28, 30, 32}

# Map connection to color
_CONNECTION_COLORS: dict[tuple[int, int], tuple[int, int, int]] = {}
for _a, _b in POSE_CONNECTIONS:
    if _a in _FACE_INDICES or _b in _FACE_INDICES:
        _CONNECTION_COLORS[(_a, _b)] = COLORS["face"]
    elif _a in _TORSO_INDICES and _b in _TORSO_INDICES:
        _CONNECTION_COLORS[(_a, _b)] = COLORS["torso"]
    elif _a in _LEFT_ARM_INDICES or _b in _LEFT_ARM_INDICES:
        _CONNECTION_COLORS[(_a, _b)] = COLORS["left_arm"]
    elif _a in _RIGHT_ARM_INDICES or _b in _RIGHT_ARM_INDICES:
        _CONNECTION_COLORS[(_a, _b)] = COLORS["right_arm"]
    elif _a in _LEFT_LEG_INDICES or _b in _LEFT_LEG_INDICES:
        _CONNECTION_COLORS[(_a, _b)] = COLORS["left_leg"]
    elif _a in _RIGHT_LEG_INDICES or _b in _RIGHT_LEG_INDICES:
        _CONNECTION_COLORS[(_a, _b)] = COLORS["right_leg"]
    else:
        _CONNECTION_COLORS[(_a, _b)] = (200, 200, 200)

VISIBILITY_THRESHOLD: float = 0.5


def _get_region_color(idx: int) -> tuple[int, int, int]:
    if idx in _FACE_INDICES:
        return COLORS["face"]
    if idx in _TORSO_INDICES:
        return COLORS["torso"]
    if idx in _LEFT_ARM_INDICES:
        return COLORS["left_arm"]
    if idx in _RIGHT_ARM_INDICES:
        return COLORS["right_arm"]
    if idx in _LEFT_LEG_INDICES:
        return COLORS["left_leg"]
    if idx in _RIGHT_LEG_INDICES:
        return COLORS["right_leg"]
    return (200, 200, 200)


def render_skeleton(
    surface: Any,
    landmarks: np.ndarray,
    width: int,
    height: int,
    visibility_threshold: float = VISIBILITY_THRESHOLD,
    line_width: int = 3,
    joint_radius: int = 4,
) -> None:
    """Draw a MediaPipe pose skeleton onto a pygame surface.

    Args:
        surface: pygame Surface to draw on
        landmarks: shape (33, 3) array with [x_norm, y_norm, visibility]
        width: surface width in pixels
        height: surface height in pixels
        visibility_threshold: minimum visibility to draw a landmark
        line_width: thickness of bone lines
        joint_radius: radius of joint circles
    """
    pixel_coords: dict[int, tuple[int, int]] = {}
    for i in range(min(33, landmarks.shape[0])):
        x_norm, y_norm, vis = landmarks[i, 0], landmarks[i, 1], landmarks[i, 2]
        if vis >= visibility_threshold:
            px = max(0, min(width - 1, int(x_norm * width)))
            py = max(0, min(height - 1, int(y_norm * height)))
            pixel_coords[i] = (px, py)

    for start_idx, end_idx in POSE_CONNECTIONS:
        if start_idx in pixel_coords and end_idx in pixel_coords:
            color = _CONNECTION_COLORS.get((start_idx, end_idx), (200, 200, 200))
            pygame_draw_line(surface, color, pixel_coords[start_idx], pixel_coords[end_idx], line_width)

    for idx, (px, py) in pixel_coords.items():
        color = _get_region_color(idx)
        pygame_draw_circle(surface, (255, 255, 255), (px, py), joint_radius + 1)
        pygame_draw_circle(surface, color, (px, py), joint_radius)


def pygame_draw_line(
    surface: Any,
    color: tuple[int, int, int],
    start_pos: tuple[int, int],
    end_pos: tuple[int, int],
    width: int,
) -> None:
    import pygame
    pygame.draw.line(surface, color, start_pos, end_pos, width)


def pygame_draw_circle(
    surface: Any,
    color: tuple[int, int, int],
    center: tuple[int, int],
    radius: int,
) -> None:
    import pygame
    pygame.draw.circle(surface, color, center, radius)
