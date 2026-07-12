"""Shared rendering utilities for camera background and overlays."""
from __future__ import annotations

from typing import Any


def render_camera_background(screen: Any, camera_frame: Any, alpha: float = 1.0) -> None:
    """Render mirrored webcam feed as background.

    Args:
        screen: pygame surface to render on
        camera_frame: BGR numpy array from camera, or None
        alpha: transparency (0.0 = fully transparent, 1.0 = fully opaque)
    """
    import cv2  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    import pygame  # noqa: PLC0415

    if camera_frame is None or not hasattr(camera_frame, 'size') or camera_frame.size == 0:
        return

    rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    rgb = np.fliplr(rgb)
    surf = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
    surf = pygame.transform.scale(surf, screen.get_size())

    if alpha < 1.0:
        surf.set_alpha(int(alpha * 255))

    screen.blit(surf, (0, 0))


def render_skeleton_overlay(
    screen: Any,
    landmarks: Any,
    width: int,
    height: int,
    alpha: float = 0.8,
    visibility_threshold: float = 0.5,
) -> None:
    """Render pose skeleton with configurable alpha.

    Args:
        screen: pygame surface to render on
        landmarks: pose landmarks array (33, 3)
        width: screen width
        height: screen height
        alpha: transparency for skeleton lines
        visibility_threshold: minimum visibility to draw a landmark
    """
    import pygame  # noqa: PLC0415

    if landmarks is None or len(landmarks) < 33:
        return

    # Create a transparent surface for the skeleton
    skeleton_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # Draw skeleton connections with alpha
    connections = [
        (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Arms
        (11, 23), (12, 24), (23, 24),  # Torso
        (23, 25), (25, 27), (24, 26), (26, 28),  # Upper legs
        (27, 29), (29, 31), (28, 30), (30, 32),  # Lower legs
    ]

    color = (0, 255, 255, int(alpha * 255))  # Cyan with alpha

    pixel_coords: dict[int, tuple[int, int]] = {}
    for idx in range(min(33, len(landmarks))):
        vis = landmarks[idx, 2]
        if vis >= visibility_threshold:
            px = max(0, min(width - 1, int((1.0 - landmarks[idx, 0]) * width)))
            py = max(0, min(height - 1, int(landmarks[idx, 1] * height)))
            pixel_coords[idx] = (px, py)

    for i, j in connections:
        if i in pixel_coords and j in pixel_coords:
            pygame.draw.line(skeleton_surf, color, pixel_coords[i], pixel_coords[j], 2)

    for _idx, (x, y) in pixel_coords.items():
        pygame.draw.circle(skeleton_surf, (255, 255, 255, int(alpha * 255)), (x, y), 4)

    screen.blit(skeleton_surf, (0, 0))


def render_debug_status(
    screen: Any,
    pose_thread: Any,
    camera_frame: Any,
    frame: Any,
) -> None:
    """Render debug status indicator showing pose detection state."""
    import pygame  # noqa: PLC0415

    w, h = screen.get_size()
    font = pygame.font.Font(None, 24)
    y_offset = h - 100

    cam_ok = camera_frame is not None and hasattr(camera_frame, 'size') and camera_frame.size > 0
    cam_color = (0, 255, 0) if cam_ok else (255, 0, 0)
    cam_text = font.render(f"Camera: {'OK' if cam_ok else 'FAIL'}", True, cam_color)
    screen.blit(cam_text, (20, y_offset))
    y_offset += 25

    tracking = pose_thread.is_tracking if pose_thread else False
    track_color = (0, 255, 0) if tracking else (255, 165, 0)
    track_text = font.render(f"Tracking: {'Yes' if tracking else 'No'}", True, track_color)
    screen.blit(track_text, (20, y_offset))
    y_offset += 25

    if frame is not None and hasattr(frame, 'landmarks'):
        lm_count = len(frame.landmarks) if frame.landmarks is not None else 0
        visible_count = sum(1 for lm in frame.landmarks if lm[2] > 0.5) if lm_count > 0 else 0
        lm_text = font.render(f"Landmarks: {visible_count}/{lm_count} visible", True, (200, 200, 200))
    else:
        lm_text = font.render("Landmarks: None", True, (255, 100, 100))
    screen.blit(lm_text, (20, y_offset))
