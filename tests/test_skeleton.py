"""Tests for the skeleton renderer module."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from common.skeleton import (
    POSE_CONNECTIONS,
    VISIBILITY_THRESHOLD,
    _get_region_color,
    _CONNECTION_COLORS,
    render_skeleton,
)


class TestPoseConnections:
    def test_has_35_connections(self):
        assert len(POSE_CONNECTIONS) == 35

    def test_connections_are_valid_indices(self):
        for start, end in POSE_CONNECTIONS:
            assert 0 <= start <= 32
            assert 0 <= end <= 32


class TestVisibilityThreshold:
    def test_threshold_value(self):
        assert VISIBILITY_THRESHOLD == 0.5


class TestGetRegionColor:
    def test_face_indices(self):
        for idx in range(11):
            assert _get_region_color(idx) == (255, 255, 255)

    def test_torso_indices(self):
        for idx in [11, 12, 23, 24]:
            assert _get_region_color(idx) == (100, 200, 255)

    def test_left_arm_indices(self):
        for idx in [13, 15, 17, 19, 21]:
            assert _get_region_color(idx) == (0, 255, 0)

    def test_right_arm_indices(self):
        for idx in [14, 16, 18, 20, 22]:
            assert _get_region_color(idx) == (255, 0, 0)

    def test_left_leg_indices(self):
        for idx in [25, 27, 29, 31]:
            assert _get_region_color(idx) == (0, 150, 255)

    def test_right_leg_indices(self):
        for idx in [26, 28, 30, 32]:
            assert _get_region_color(idx) == (255, 150, 0)


class TestConnectionColors:
    def test_all_connections_have_colors(self):
        for conn in POSE_CONNECTIONS:
            assert conn in _CONNECTION_COLORS


class TestRenderSkeleton:
    @patch("common.skeleton.pygame_draw_line")
    @patch("common.skeleton.pygame_draw_circle")
    def test_render_skeleton_calls_draw_line(self, mock_circle, mock_line):
        surface = MagicMock()
        landmarks = np.random.rand(33, 3).astype(np.float32)
        landmarks[:, 2] = 0.8

        render_skeleton(surface, landmarks, 1280, 720)

        assert mock_line.call_count > 0

    @patch("common.skeleton.pygame_draw_line")
    @patch("common.skeleton.pygame_draw_circle")
    def test_render_skeleton_calls_draw_circle(self, mock_circle, mock_line):
        surface = MagicMock()
        landmarks = np.random.rand(33, 3).astype(np.float32)
        landmarks[:, 2] = 0.8

        render_skeleton(surface, landmarks, 1280, 720)

        assert mock_circle.call_count > 0

    @patch("common.skeleton.pygame_draw_line")
    @patch("common.skeleton.pygame_draw_circle")
    def test_render_skeleton_skips_low_visibility(self, mock_circle, mock_line):
        surface = MagicMock()
        landmarks = np.random.rand(33, 3).astype(np.float32)
        landmarks[:, 2] = 0.1

        render_skeleton(surface, landmarks, 1280, 720)

        assert mock_line.call_count == 0
        assert mock_circle.call_count == 0

    @patch("common.skeleton.pygame_draw_line")
    @patch("common.skeleton.pygame_draw_circle")
    def test_render_skeleton_clamps_coordinates(self, mock_circle, mock_line):
        surface = MagicMock()
        landmarks = np.zeros((33, 3), dtype=np.float32)
        landmarks[:, 0] = 1.5
        landmarks[:, 1] = 1.5
        landmarks[:, 2] = 0.9

        render_skeleton(surface, landmarks, 100, 100)

        for call in mock_circle.call_args_list:
            center = call[0][2]
            assert center[0] <= 99
            assert center[1] <= 99

    def test_render_skeleton_empty_landmarks(self):
        surface = MagicMock()
        landmarks = np.zeros((33, 3), dtype=np.float32)

        render_skeleton(surface, landmarks, 1280, 720)

        assert surface.blit.call_count == 0
