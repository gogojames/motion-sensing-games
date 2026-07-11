# Implementation Plan: Motion-Sensing Games

**Branch**: `001-motion-sensing-games` | **Date**: 2026-07-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-motion-sensing-games/spec.md`

## Summary

Build two motion-sensing desktop games (fruit-slicing + rhythm conductor) using a
standard webcam and Google MediaPipe Pose Landmarker (lite). All processing runs
locally — frame data never leaves the device. Graphics are procedurally rendered
(pygame), audio is programmatically synthesized. Model (~5.5MB) downloads once on
first run, then fully offline. Python 3.11/3.12, supports macOS and Windows.

## Technical Context

**Language/Version**: Python 3.11 / 3.12

**Primary Dependencies**:
- `mediapipe-tasks` — Pose Landmarker lite (33 keypoints at ~30Hz CPU)
- `opencv-python` — camera frame capture
- `numpy` — angle/vector calculations, gesture classification
- `pygame` — rendering (60fps main loop), audio synthesis, input handling
- System-native: `osascript`/`afplay` (macOS), `MessageBox`/`winsound` (Windows)

**Storage**: Local high-score persistence via JSON file in user config directory
(`~/.motion-sensing-games/highscores.json`)
- Fruit-slicing: top scores per session
- Conductor: best rank, score, max combo per track

**Testing**: pytest (unit tests for gesture logic, collision detection, score
calculation). Manual playtest for real-time camera + rendering pipeline.

**Target Platform**: macOS (Intel + Apple Silicon) + Windows 10/11 — desktop native
via Python runtime. NOT web browser (overriding generic spec assumption).

**Project Type**: Desktop application (Python CLI launcher → pygame window)

**Performance Goals**:
- Pose inference thread: ≥30Hz (one frame every ~33ms on CPU via MediaPipe Lite)
- Render main loop: 60fps (16.6ms per frame for smooth slicing visuals)
- Gesture → game action latency: ≤200ms (perceptual instant)
- Frame data handling: 0 dropped frames — no disk write, no upload, no network

**Constraints**:
- All processing on-device — zero network calls after initial model download
- No image/audio assets in repository — everything procedural
- Camera frames must NOT be saved to disk or transmitted anywhere
- Model download: exactly once (first run), auto-detect platform paths
- Must handle camera already-in-use gracefully (e.g., Zoom running)

**Scale/Scope**: Single-player, local-only. Two game modes sharing one pose pipeline.
Full offline mode after first-run model download.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I — Code Quality
- **Pass**: Python with type hints (via stub files or inline). Static analysis via
  pylint + mypy on all source files. No `# type: ignore` without justification.
  Architecture: strict separation of pose pipeline, game logic, and rendering layers.
  Circular dependency check via import linter.
- **Risk**: Performance-critical hot paths (pose decode, collision) may need
  suppression — justify in Complexity Tracking.

### Principle II — Testing Standards
- **Pass**: pytest for unit-testable modules (gesture classification, collision
  detection, score logic, entity spawning). Cam-dependent integration tested
  manually via playtest guide.
- **Gate**: ≥80% coverage on non-camera modules; ≥90% on scoring + collision paths.

### Principle III — UX Consistency
- **Pass**: Both games share same pose pipeline, calibration flow, and feedback
  patterns. Gestures are consistent across menus and gameplay (wave to select,
  swipe to slice). Color-coding for conductor targets (cyan/orange/purple/gold).
- **Gate**: Onboarding must include camera calibration + 3-2-1 countdown. Error
  states must be human-readable with recovery paths. Silent failures forbidden.

### Principle IV — Performance Requirements
- **Pass**: Frame budget is explicit (16.6ms rendering, 33ms pose). Sensor latency
  bounded by design (pose thread → shared memory → render thread). No GC-heavy
  patterns in hot paths.
- **Gate**: Profile pose pipeline before optimizing. Document latency budget per
  module. Target testing on lowest-spec supported machine (Intel UHD Graphics).

**Verdict**: ✅ PASS — no violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/001-motion-sensing-games/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
motion-sensing-games/
├── main.py                    # Entry point — mode selection, launcher
├── requirements.txt           # Python dependencies
│
├── pose/                      # Pose detection pipeline (shared)
│   ├── __init__.py
│   ├── detector.py            # MediaPipe Pose Landmarker wrapper
│   ├── thread.py              # Background capture + inference thread
│   └── landmarks.py           # Keypoint math utilities (angles, distances)
│
├── fruit_slicing/             # Game 1: Fruit-slicing
│   ├── __init__.py
│   ├── game.py                # Main game loop, state machine
│   ├── entities.py            # Fruit, bomb, particle definitions
│   ├── spawner.py             # Wave generation logic
│   ├── collision.py           # Hand-blade ↔ fruit intersection
│   ├── scoring.py             # Score, combo, multiplier logic
│   ├── renderer.py            # Pygame procedural drawing
│   └── audio.py               # Programmatic sound effect synthesis
│
├── conductor/                 # Game 2: Rhythm conductor
│   ├── __init__.py
│   ├── game.py                # Main game loop, state machine
│   ├── targets.py             # Star note definitions and choreography
│   ├── gesture.py             # Gesture classifier (swipe, hold, squat, arms)
│   ├── music.py               # Procedural music engine (layered tracks)
│   ├── scoring.py             # Combo, star power, rank calculation
│   └── renderer.py            # Starfield + target ring rendering
│
├── common/                    # Shared utilities
│   ├── __init__.py
│   ├── camera.py              # OpenCV camera manager
│   ├── config.py              # Paths, settings, model download
│   ├── menu.py                # Gesture-driven main menu
│   ├── calibration.py         # Body calibration screen
│   ├── sys_ui.py              # Native dialogs (permission, error)
│   └── model_downloader.py    # One-time MediaPipe model download
│
├── tests/                     # pytest test suite
│   ├── test_landmarks.py      # Keypoint math tests
│   ├── test_collision.py      # Collision detection tests
│   ├── test_scoring.py        # Score + combo tests
│   ├── test_spawner.py        # Wave generation tests
│   ├── test_gesture.py        # Gesture classification tests
│   └── test_targets.py        # Conductor target logic tests
│
├── models/                    # Downloaded MediaPipe models (gitignored)
│   └── pose_landmarker_lite.task  # ~5.5MB, downloaded on first run
│
└── data/                      # Local runtime data (gitignored)
    └── highscores.json        # Persisted high scores
```

**Structure Decision**: Single Python package with `pose/` as shared core,
`fruit_slicing/` and `conductor/` as game-specific modules, `common/` for
shared utilities, `tests/` mirroring source layout. No web/mobile split needed.

## Complexity Tracking

> **Not required** — Constitutional Check passed with zero violations.
