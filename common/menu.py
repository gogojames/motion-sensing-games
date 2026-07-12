"""Gesture-driven main menu with game mode selection."""
from __future__ import annotations

from typing import Any, Optional

import numpy as np

from common.scores import ScoreManager
from common.renderer import render_camera_background, render_skeleton_overlay
from common.font import get_font


class MainMenu:
    """Main menu with hand-tracking start: raise both hands to begin."""

    FRUIT_SLICING = "fruit_slicing"
    CONDUCTOR = "conductor"
    QUIT = "quit"

    def __init__(self, scores: ScoreManager) -> None:
        self._scores = scores
        self._selected: int = 0
        self._options: list[str] = [self.FRUIT_SLICING, self.CONDUCTOR, self.QUIT]
        self._tracking: bool = False
        self._hands_up_frames: int = 0
        self._hands_up_required: int = 10

    def run(self, pose_thread: Any, screen: Any = None, camera: Any = None) -> str:
        import pygame  # noqa: PLC0415

        if screen is None:
            return self._terminal_menu()

        clock = pygame.time.Clock()
        running = True
        result: Optional[str] = self.FRUIT_SLICING
        camera_frame: Any = None
        pose: Any = None

        while running:
            if camera is not None:
                frame = camera.read_frame()
                if frame is not None:
                    pose_thread.push_frame(frame)
                    camera_frame = frame

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    result = self.QUIT
                    running = False
                elif event.type == pygame.KEYDOWN:
                    result = self._handle_key(event.key)
                    if result is not None:
                        running = False

            new_pose = pose_thread.get_pose() if pose_thread else None
            if new_pose is not None:
                pose = new_pose
                self._tracking = True
            elif pose is None:
                self._tracking = False

            if pose is not None and hasattr(pose, 'landmarks'):
                lm = pose.landmarks
                wrists_y = [lm[15, 1], lm[16, 1]]
                both_hands_up = all(y < 0.3 for y in wrists_y)
                if both_hands_up:
                    self._hands_up_frames += 1
                else:
                    self._hands_up_frames = 0

                if self._hands_up_frames >= self._hands_up_required:
                    result = self._options[self._selected]
                    running = False

            self._render(screen, camera_frame, pose)
            clock.tick(30)

        return result if result is not None else self.QUIT

    def _terminal_menu(self) -> str:
        print("\n=== Motion-Sensing Games ===")
        print("1. Fruit Slicing")
        print("2. Rhythm Conductor")
        print("3. Quit")
        best_fruit = self._scores.get_best_score(self.FRUIT_SLICING)
        best_conductor = self._scores.get_best_score(self.CONDUCTOR)
        if best_fruit is not None:
            print(f"   Best fruit score: {best_fruit}")
        if best_conductor is not None:
            print(f"   Best conductor score: {best_conductor}")
        while True:
            choice = input("Select (1/2/3): ").strip()
            if choice == "1":
                return self.FRUIT_SLICING
            if choice == "2":
                return self.CONDUCTOR
            if choice == "3":
                return self.QUIT

    def _handle_key(self, key: int) -> Optional[str]:
        import pygame  # noqa: PLC0415

        if key == pygame.K_UP:
            self._selected = (self._selected - 1) % len(self._options)
            self._hands_up_frames = 0
            return None
        if key == pygame.K_DOWN:
            self._selected = (self._selected + 1) % len(self._options)
            self._hands_up_frames = 0
            return None
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            return self._options[self._selected]
        if key == pygame.K_ESCAPE:
            return self.QUIT
        return None

    def _render(self, screen: Any, camera_frame: Any = None, pose: Any = None) -> None:
        import pygame  # noqa: PLC0415

        w, h = screen.get_size()

        render_camera_background(screen, camera_frame, alpha=0.4)
        if pose is not None and hasattr(pose, 'landmarks'):
            render_skeleton_overlay(screen, pose.landmarks, w, h, alpha=0.9)

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((20, 20, 40, 120))
        screen.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 64)
        title = title_font.render("Motion-Sensing Games", True, (255, 255, 255))
        screen.blit(title, (w // 2 - title.get_width() // 2, 60))

        btn_font = pygame.font.Font(None, 40)
        for i, name in enumerate(self._options):
            y = 200 + i * 100
            is_selected = i == self._selected
            color = (100, 200, 255) if is_selected else (80, 80, 120)
            rect = pygame.Rect(w // 2 - 200, y, 400, 70)
            pygame.draw.rect(screen, color, rect, border_radius=12)
            label = name.replace("_", " ").title()
            text = btn_font.render(label, True, (255, 255, 255))
            screen.blit(text, (w // 2 - text.get_width() // 2, y + 18))

        best_fruit = self._scores.get_best_score(self.FRUIT_SLICING)
        best_conductor = self._scores.get_best_score(self.CONDUCTOR)
        score_font = pygame.font.Font(None, 28)
        sy = 540
        if best_fruit is not None:
            t = score_font.render(f"Fruit Best: {best_fruit}", True, (180, 180, 180))
            screen.blit(t, (w // 2 - t.get_width() // 2, sy))
            sy += 30
        if best_conductor is not None:
            t = score_font.render(f"Conductor Best: {best_conductor}", True, (180, 180, 180))
            screen.blit(t, (w // 2 - t.get_width() // 2, sy))

        hint_font = get_font(32)
        if not self._tracking:
            hint = hint_font.render("寻找摄像头中...", True, (255, 200, 100))
            screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 80))
        elif self._hands_up_frames == 0:
            hint = hint_font.render("举起双手开始游戏", True, (100, 255, 100))
            screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 80))
        else:
            progress = min(1.0, self._hands_up_frames / self._hands_up_required)
            bar_w = 200
            bar_h = 12
            bx = w // 2 - bar_w // 2
            by = h - 70
            pygame.draw.rect(screen, (40, 40, 40), (bx, by, bar_w, bar_h), border_radius=6)
            pygame.draw.rect(screen, (100, 255, 100), (bx, by, int(bar_w * progress), bar_h), border_radius=6)

        kb_hint = hint_font.render("↑↓选择  Space确认  Esc退出", True, (120, 120, 160))
        screen.blit(kb_hint, (w // 2 - kb_hint.get_width() // 2, h - 40))

        pygame.display.flip()
