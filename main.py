"""Entry point — mode selection, launcher."""
from __future__ import annotations

import argparse
import sys
from typing import Any, Optional


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Motion-Sensing Games")
    parser.add_argument("--camera-id", type=int, default=0, help="Camera device ID")
    parser.add_argument("--fullscreen", action="store_true", help="Start in fullscreen")
    parser.add_argument("--no-sound", action="store_true", help="Disable sound")
    return parser.parse_args()


def main() -> None:
    """Main entry point for the motion-sensing games application."""
    args = parse_args()

    from common.config import load_settings, save_settings, Settings  # noqa: PLC0415
    from common.model_downloader import ensure_model, DownloadError  # noqa: PLC0415
    from common.camera import Camera, CameraError  # noqa: PLC0415
    from common.scores import ScoreManager  # noqa: PLC0415
    from common.menu import MainMenu  # noqa: PLC0415

    settings = load_settings()
    settings.camera_id = args.camera_id
    settings.fullscreen = args.fullscreen
    settings.sound_enabled = not args.no_sound

    try:
        ensure_model()
    except DownloadError as exc:
        print(f"Model download failed: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        camera = Camera(
            camera_id=settings.camera_id,
            width=settings.preferred_resolution[0],
            height=settings.preferred_resolution[1],
        )
        camera.open()
    except CameraError as exc:
        from common.sys_ui import show_camera_permission_error, show_camera_in_use_error  # noqa: PLC0415

        if "permission" in str(exc).lower():
            show_camera_permission_error()
        else:
            show_camera_in_use_error()
        sys.exit(1)

    try:
        _run_game_loop(camera, settings)
    finally:
        camera.release()
        save_settings(settings)


def _run_game_loop(camera: Any, settings: Any) -> None:
    """Run the main game loop: menu → game → menu cycle."""
    import pygame  # noqa: PLC0415

    pygame.init()
    flags = pygame.FULLSCREEN if settings.fullscreen else 0
    screen = pygame.display.set_mode((1280, 720), flags)
    pygame.display.set_caption("Motion-Sensing Games")
    clock = pygame.time.Clock()

    from pose.detector import PoseDetector  # noqa: PLC0415
    from pose.thread import PoseThread  # noqa: PLC0415
    from common.config import get_model_path  # noqa: PLC0415

    detector = PoseDetector(str(get_model_path()))
    pose_thread = PoseThread()
    pose_thread.start(camera, detector)

    try:
        from common.scores import ScoreManager  # noqa: PLC0415
        from common.menu import MainMenu  # noqa: PLC0415

        scores = ScoreManager()
        menu = MainMenu(scores)

        while True:
            frame = camera.read_frame()
            if frame is not None:
                pose_thread.push_frame(frame)

            mode = menu.run(pose_thread, screen)
            if mode == "quit":
                break
            elif mode == "fruit_slicing":
                from fruit_slicing.game import FruitSlicingGame  # noqa: PLC0415

                game: FruitSlicingGame | ConductorGame = FruitSlicingGame()
                game.run(pose_thread, screen, scores)
            elif mode == "conductor":
                from conductor.game import ConductorGame  # noqa: PLC0415

                game = ConductorGame()
                game.run(pose_thread, screen, scores)
    finally:
        pose_thread.stop()
        detector.close()
        pygame.quit()


if __name__ == "__main__":
    main()
