"""Gesture-driven main menu with game mode selection."""
from __future__ import annotations

from typing import Any, Optional

import numpy as np

from common.scores import ScoreManager


class MainMenu:
    """Main menu that lets the player choose a game mode via gesture or keyboard.

    Renders two large buttons with game mode names, displays high scores,
    and accepts WAVE_SELECT gesture or keyboard input.
    """

    FRUIT_SLICING = "fruit_slicing"
    CONDUCTOR = "conductor"
    QUIT = "quit"

    def __init__(self, scores: ScoreManager) -> None:
        self._scores = scores
        self._selected: int = 0
        self._options: list[str] = [self.FRUIT_SLICING, self.CONDUCTOR, self.QUIT]

    def run(self, pose_thread: Any, screen: Any = None) -> str:
        """Run the main menu loop.

        Args:
            pose_thread: PoseThread for gesture detection
            screen: pygame screen (optional — falls back to terminal)

        Returns:
            Selected game mode string ("fruit_slicing", "conductor", or "quit")
        """
        import pygame  # noqa: PLC0415 — lazy import

        if screen is None:
            return self._terminal_menu()

        clock = pygame.time.Clock()
        running = True
        result: Optional[str] = self.FRUIT_SLICING

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    result = self.QUIT
                    running = False
                elif event.type == pygame.KEYDOWN:
                    result = self._handle_key(event.key)
                    if result is not None:
                        running = False

            pose = pose_thread.get_pose() if pose_thread else None
            if pose is not None:
                gesture = self._detect_menu_gesture(pose)
                if gesture == "select":
                    result = self._options[self._selected]
                    running = False
                elif gesture == "next":
                    self._selected = (self._selected + 1) % len(self._options)

            self._render(screen)
            clock.tick(30)

        return result if result is not None else self.QUIT

    def _terminal_menu(self) -> str:
        """Fallback terminal-based menu when no pygame screen."""
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
        """Handle keyboard input. Returns mode string or None to continue."""
        import pygame  # noqa: PLC0415

        if key == pygame.K_UP:
            self._selected = (self._selected - 1) % len(self._options)
            return None
        if key == pygame.K_DOWN:
            self._selected = (self._selected + 1) % len(self._options)
            return None
        if key in (pygame.K_SPACE, pygame.K_RETURN):
            return self._options[self._selected]
        if key == pygame.K_ESCAPE:
            return self.QUIT
        return None

    def _detect_menu_gesture(self, pose: Any) -> Optional[str]:
        """Detect menu gestures from pose data.

        Returns "select" for wave, "next" for hand raise, None otherwise.
        """
        if not hasattr(pose, "landmarks"):
            return None
        lm = pose.landmarks
        wrists_y = [lm[15, 1], lm[16, 1]]
        hands_up = all(y < 0.3 for y in wrists_y)
        if hands_up:
            return "next"
        return None

    def _render(self, screen: Any) -> None:
        """Render the main menu."""
        import pygame  # noqa: PLC0415

        w, h = screen.get_size()
        screen.fill((20, 20, 40))

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

        hint = score_font.render(
            "Arrow keys to navigate, Space to select, Esc to quit",
            True,
            (120, 120, 160),
        )
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 50))

        pygame.display.flip()
