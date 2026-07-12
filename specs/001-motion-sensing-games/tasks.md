# Tasks: Motion-Sensing Games

**Input**: Design documents from `/specs/001-motion-sensing-games/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅, constitution.md ✅

**Tests**: Unit tests included in Phase 5 per constitution requirement (≥80% coverage, ≥90% critical paths). Not blocking for implementation phases.

**Organization**: Tasks grouped by user story. US1 (fruit-slicing) is MVP — stop and validate after Phase 3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- All file paths relative to project root (`motion-sensing-games/`)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project skeleton, dependencies, and configuration infrastructure

- [x] T001 Create full project directory structure per plan.md: `pose/`, `fruit_slicing/`, `conductor/`, `common/`, `tests/`, `models/` (gitignored), `data/` (gitignored); create all `__init__.py` files; create `.gitignore` (models/, data/, __pycache__, .venv, *.pyc); create `requirements.txt` with mediapipe-tasks>=0.10.0, opencv-python>=4.8.0, numpy>=1.24.0, pygame>=2.5.0
- [x] T002 [P] Implement `common/config.py` — platform detection (macOS/Windows), user data directory resolution (`~/Library/Application Support/motion-sensing-games/` or `%APPDATA%/motion-sensing-games/`), model path constant, default settings loading from `config.json`, settings dataclass per contracts/data-files.md schema
- [x] T003 [P] Implement `common/sys_ui.py` — native error/permission dialog functions: `show_error(title, message)` using `osascript -e 'display dialog'` on macOS and `ctypes.windll.user32.MessageBoxW` on Windows; `show_camera_permission_error()` with instructions; `show_camera_in_use_error()` for camera-in-use case; `play_notification_sound()` using `afplay` on macOS and `winsound.MessageBeep` on Windows

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core pose pipeline, camera, calibration — MUST complete before ANY game can be implemented

**⚠️ CRITICAL**: No user story work begins until this phase is complete

- [x] T004 Implement `common/model_downloader.py` — one-time download of `pose_landmarker_lite.task` (~5.5MB) from `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task`; check if model exists at `models/pose_landmarker_lite.task`; if missing, show pygame progress bar during download via `urllib.request`; on failure, call `sys_ui.show_error()` with retry/quit options; save to models dir
- [x] T005 Implement `common/camera.py` — OpenCV camera manager class: `open_camera(camera_id=0, width=640, height=480)` returns capture object; set `CAP_PROP_BUFFERSIZE = 1` to prevent frame accumulation; `read_frame()` returns BGR numpy array; `release_camera()` cleanup; error handling for camera-in-use (`cv2.error`), permission denied, and no-camera-found; platform-specific fallback for default camera ID
- [x] T006 Implement `pose/detector.py` — MediaPipe Pose Landmarker wrapper class: define `PoseFrame` dataclass (landmarks ndarray 33×3, world_landmarks ndarray 33×3, timestamp_ms int); create `PoseDetector` class with `__init__(model_path)` that initializes `vision.PoseLandmarker` with `RunningMode.VIDEO`, `num_poses=1`, confidence thresholds 0.5; `detect(frame, timestamp_ms)` method calls `detect_for_video()` synchronously; returns `PoseFrame` or None; warmup method that runs 5-10 dummy frames to avoid cold-start latency
- [x] T007 Implement `pose/landmarks.py` — keypoint math utilities: `wrist_velocity(pose_a, pose_b)` → pixels/sec using indices 15/16; `finger_direction(pose, hand)` → direction vector from wrist (15/16) to index finger tip (19/20); `joint_angle(pose, joint_a, joint_b, joint_c)` → angle in degrees; `normalize_landmarks(landmarks, width, height)` → pixel-space coordinates; `is_hand_blade(pose_a, pose_b, threshold)` → bool + velocity; define `GestureType` enum (HAND_BLADE, HANDS_UP, WAVE_SELECT, LEFT_HAND_REACH, RIGHT_HAND_REACH, DUAL_HAND_SYNC, SQUAT, ARMS_EXTEND, HANDS_UP_HOLD, STANDING_NEUTRAL); define `GestureEvent` dataclass per data-model.md
- [x] T008 Implement `pose/thread.py` — background pose detection thread class: `PoseThread` with `start(camera, detector)` that spawns daemon thread running at 30Hz; reads camera frames, runs detector, pushes `PoseFrame` to `queue.Queue(maxsize=1)` (latest-frame-wins); exposes `get_pose() → PoseFrame | None` for main thread; `get_gesture() → GestureEvent | None` (consumes gesture queue); `stop()` to join thread; shared state dict with Lock for `is_tracking`, `frame_width`, `frame_height`
- [x] T009 Implement `common/calibration.py` — 2-second body calibration flow: `CalibrationData` dataclass (shoulder_width, standing_hip_y, arm_span, torso_angle, confidence) per data-model.md; `CalibrationScreen` class that captures 2 seconds of neutral standing pose data; computes baseline measurements from wrist, shoulder, hip landmarks; confidence score based on landmark visibility; renders countdown overlay (2, 1, done) with pose skeleton; returns `CalibrationData` or raises if confidence < 0.7
- [x] T010 Implement `common/scores.py` — high score persistence: `load_highscores() → dict` reads `data/highscores.json` per contracts/data-files.md schema (schema_version, fruit_slicing.top_scores, conductor.top_scores); `save_highscores(data)` writes JSON; `update_highscore(game_mode, score_entry) → bool` returns True if new high score; `get_best_score(game_mode) → int | None`; handle missing file gracefully (create default); cap at max_entries=10 per mode
- [x] T011 Implement `common/menu.py` — gesture-driven main menu: `MainMenu` class with `run(pose_thread)` → returns selected game mode ("fruit_slicing" | "conductor" | "quit"); renders two large buttons with game mode icons (procedural); accepts WAVE_SELECT gesture (horizontal hand wave) or keyboard (Space to confirm, arrow keys to navigate); displays current high scores per mode; camera feed as background; "Press Space or wave to start" instruction text
- [x] T012 Implement `main.py` — entry point: parse CLI args (--camera-id, --fullscreen, --no-sound); call `model_downloader.ensure_model()`; open camera via `camera.open_camera()`; initialize pygame (1280×720 window, 60fps); run main menu loop; on game selection → run calibration → launch selected game module; on game end → back to menu; keyboard fallback: Space=start, P=pause, F=fullscreen, R=restart, Esc=quit; graceful shutdown (release camera, pygame quit)

**Checkpoint**: Pose pipeline working, menu launches, camera opens, calibration runs — ready for game implementation

---

## Phase 3: User Story 1 — Fruit-Slicing Game (P1) 🎯 MVP

**Goal**: Player stands in front of webcam and slices flying fruits with hand swipes. Bombs end game, miss 3 fruits ends game, score tracking with combos.

**Independent Test**: Launch game → calibration → countdown → swipe hand → fruit splits with effect + sound → score increments → miss 3 or hit bomb → game over screen with score

### Implementation for User Story 1

- [x] T013 [US1] Implement `fruit_slicing/entities.py` — all fruit-slicing dataclasses per data-model.md: `Fruit` (id, type, x, y, vx, vy, radius, rotation, rotation_speed, sliced, missed, trail list), `FruitType` enum (WATERMELON 10pts green, ORANGE 20pts orange, APPLE 15pts red, BANANA 15pts yellow, GOLDEN_WATERMELON 50pts gold), `Bomb` (x, y, vx, vy, radius, rotation, exploded), `HandBlade` (hand, start_pos, end_pos, velocity, lifetime, arc), `WaveConfig` (wave_number, fruit_count, bomb_count, golden_chance, speeds, spawn_interval, trajectory_types, difficulty_multiplier property), `FruitSlicingState` (phase, lives=3, score, combo, max_combo, fruits_sliced, fruits_missed, wave, golden_fruit_spawned)
- [x] T014 [P] [US1] Implement `fruit_slicing/spawner.py` — wave generation: `WaveSpawner` class with `generate_wave(wave_number) → WaveConfig`; difficulty scaling via `difficulty_multiplier = 1.0 + (wave - 1) * 0.15`; `spawn_fruits(wave_config, screen_width, screen_height) → list[Fruit]` with randomized trajectories (arc, straight, lob, fan); bomb probability increases with wave; golden watermelon 5% chance per wave; spawn interval decreases with difficulty; fruits launch from screen bottom within comfortable gesture zone (not at extreme edges)
- [x] T015 [P] [US1] Implement `fruit_slicing/collision.py` — intersection detection: `check_swipe_fruit(blade: HandBlade, fruit: Fruit) → bool` using point-in-circle test along swipe arc; `check_swipe_bomb(blade: HandBlade, bomb: Bomb) → bool`; `check_fruit_missed(fruit: Fruit, screen_height) → bool` (fallen below bottom); blade arc is line segment from start_pos to end_pos with thickness; collision radius per fruit type; requires fruit.sliced == False and visibility check
- [x] T016 [P] [US1] Implement `fruit_slicing/scoring.py` — scoring engine: `calculate_score(fruit_type, combo) → int`; base points from FruitType; combo bonus: +5 per consecutive slice (combo 2+), +10 per slice (combo 5+); `update_combo(state, event)` — increment on slice, reset on miss/bomb; golden watermelon always +50; `calculate_final_score(state) → dict` with score, combo, fruits_sliced for high score record
- [x] T017 [P] [US1] Implement `fruit_slicing/audio.py` — procedural sound effects via pygame.sndarray + numpy: `init_audio()` with `pygame.mixer.pre_init(44100, -16, 2, 1024)`; `play_slice_sound()` — short white noise bandpass sweep ~100ms; `play_bomb_sound()` — low freq rumble + noise burst ~300ms; `play_combo_chime(combo_level)` — ascending sine tone sequence; `play_golden_sound()` — sparkle arpeggio; `play_miss_sound()` — descending tone; `play_menu_click()` — quick pop; all synthesized with numpy, no audio files; `set_enabled(bool)` for mute toggle
- [x] T018 [P] [US1] Implement `fruit_slicing/renderer.py` — procedural drawing: `FruitRenderer` class with `render_fruit(screen, fruit)` — colored circle with rotation indicator (line), type-specific color from FruitType; `render_bomb(screen, bomb)` — dark spiky circle; `render_hand_blade(screen, blade)` — bright trail along arc path with fade; `render_particles(screen, particles)` — explosion/slice particle effects; `render_hud(screen, state)` — score, lives (hearts), combo counter, wave number; `render_background(screen, camera_frame)` — mirrored webcam feed as background via pygame.surfarray; `render_countdown(screen, count)` — large centered number; `render_game_over(screen, state)` — final score + "Press R to restart"
- [x] T019 [US1] Implement `fruit_slicing/game.py` — main game loop: `FruitSlicingGame` class with `run(pose_thread, calibration, scores)` method; state machine per data-model.md (MENU→CALIBRATE→COUNTDOWN→PLAYING→GAME_OVER); in PLAYING: poll pose_thread for GestureEvent, detect HAND_BLADE events, check collisions, update scoring, spawn wave fruits, remove sliced/missed/bomb fruits, track lives; 60fps main loop with `clock.tick(60)`; integrates spawner, collision, scoring, audio, renderer; keyboard fallback: Space=start, P=pause, Esc=quit; on game over: save high score, show restart prompt

**Checkpoint**: Fruit-slicing game fully playable — launch via main.py menu, slice fruits, score tracking, game over, high scores. **STOP AND VALIDATE HERE before continuing.**

---

## Phase 4: User Story 2 — Rhythm Conductor Game (P2)

**Goal**: Player conducts an orchestra with full body. Star notes approach from distance, player matches gestures to targets. Music layers build with combo. ~2-minute piece with rank at end.

**Independent Test**: Launch conductor → calibration → countdown → hit targets with correct gestures → music layers build → song ends → rank displayed → return to menu

### Implementation for User Story 2

- [x] T20 [US2] Implement `conductor/targets.py` — star note system: `StarNote` dataclass (id, target_type, approach_duration, time_remaining, target_x, target_y, ring_radius, hit, missed, score_bonus) per data-model.md; `StarTargetType` enum (LEFT_HAND cyan 10pts, RIGHT_HAND orange 10pts, DUAL_HAND purple 25pts, SQUAT gold 30pts, CONSTELLATION white 20pts); `Choreography` class that loads/generates timed note sequences for "Star Voyage" track (~2 min); `get_notes_at_time(position_sec) → list[StarNote]` returns notes that should be visible; approach animation: notes grow from distant point to target ring
- [x] T21 [P] [US2] Implement `conductor/gesture.py` — full-body gesture classifier: `ConductorGestureClassifier` class with `classify(pose: PoseFrame, calibration: CalibrationData) → GestureEvent | None`; LEFT_HAND_REACH: check left_wrist (idx 15) proximity to left screen zone; RIGHT_HAND_REACH: check right_wrist (idx 16) proximity to right zone; DUAL_HAND_SYNC: both wrists simultaneously near center zones; SQUAT: hip_y (idx 23/24 avg) drops below calibration baseline + offset; ARMS_EXTEND: both arms >120° abduction from torso, held 0.5s; uses velocity and position thresholds from calibration baseline
- [x] T22 [P] [US2] Implement `conductor/music.py` — procedural music engine: `MusicEngine` class with `MusicLayer` dataclass (name, enabled, volume, waveform_type, frequency_range, pattern, tempo_multiplier); 4 layers: drums (noise waveform, low freq), bass (saw wave, 60-200Hz), melody (sine wave, 400-800Hz), harmony (square wave, 200-400Hz); `set_tempo(bpm)` maps conductor arm speed to BPM; `set_volume(amplitude)` maps arm span to volume envelope; `activate_layer(layer_name)` on combo milestones (drums@combo5, bass@combo10, melody@combo20, harmony@combo30); `trigger_supernova()` — 8 seconds of arpeggiated chord progression, all layers max; synthesis via pygame.sndarray + numpy per research.md pattern; `update(dt)` advances playback position
- [x] T23 [P] [US2] Implement `conductor/scoring.py` — scoring engine: `ConductorScorer` class tracking score, combo, max_combo; `on_hit(target_type, timing_accuracy) → int` — base points from StarTargetType, timing bonus (perfect ±50ms, good ±150ms, ok ±300ms); `on_miss() → combo reset`; `star_power: StarPower` dataclass (current 0-1.0, decay_rate, fill_rate per hit, supernova_threshold 1.0, supernova_duration 8s); `update_star_power(dt)` — decays when not hitting; `calculate_rank(score) → str` per data-model.md (S≥9000, A≥7000, B≥5000, C≥3000, D≥1000, F<1000); `get_final_result() → dict` with score, rank, max_combo, track_name
- [x] T24 [P] [US2] Implement `conductor/renderer.py` — starfield + target rendering: `ConductorRenderer` class; `render_starfield(screen, dt)` — animated star particles moving toward viewer (z-depth illusion); `render_target_ring(screen, target_type, x, y, radius)` — colored ring per StarTargetType.color; `render_star_note(screen, note, progress)` — approaching note growing from distant point to ring; `render_gesture_indicator(screen, detected_gesture)` — visual feedback for recognized gesture; `render_star_power_meter(screen, star_power)` — circular or bar meter; `render_combo(screen, combo)` — large combo counter; `render_rank_result(screen, result)` — S/A/B/C/D/F rank with animation; `render_hud(screen, state)` — score, time remaining, layers active
- [x] T25 [US2] Implement `conductor/game.py` — main game loop: `ConductorGame` class with `run(pose_thread, calibration, scores)` method; state machine per data-model.md (MENU→CALIBRATE→COUNTDOWN→PLAYING→RESULT); in PLAYING: poll pose_thread, classify gestures, match against active StarNotes (timing window), update scoring/star_power, manage music layers, trigger supernova; track position through ~2 min choreography; 60fps main loop; keyboard fallback: Space=start, P=pause; on song end: show rank result, save high score, "raise hands to return to menu"

**Checkpoint**: Conductor game fully playable — both games accessible from main menu, independent operation

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quality assurance, testing, performance validation, and cross-cutting improvements

### Unit Tests (per constitution: ≥80% coverage, ≥90% on critical paths)

- [x] T026 [P] Implement `tests/test_landmarks.py` — unit tests for pose/landmarks.py: wrist_velocity calculation with mock PoseFrame pairs; finger_direction vector computation; joint_angle for known configurations; normalize_landmarks coordinate transform; is_hand_blade threshold behavior; GestureType enum completeness
- [x] T027 [P] Implement `tests/test_collision.py` — unit tests for fruit_slicing/collision.py: point-in-circle collision at various positions; swipe arc intersection with fruit; bomb collision detection; fruit missed detection (off-screen); edge cases (fruit at screen edge, zero-velocity blade)
- [x] T028 [P] Implement `tests/test_scoring.py` — unit tests for fruit_slicing/scoring.py and conductor/scoring.py: base fruit score per type; combo bonus at thresholds (1, 2, 4, 5, 9, 10+); combo reset on miss/bomb; golden watermelon fixed 50pts; conductor timing accuracy bonus; rank calculation for all tiers; star power fill/decay
- [x] T029 [P] Implement `tests/test_spawner.py` — unit tests for fruit_slicing/spawner.py: wave difficulty scaling formula; fruit count progression; bomb probability increases; golden watermelon spawn chance; trajectory variety; spawn interval decreases; fruits within gesture zone bounds

### Performance & Quality

- [x] T030 Performance profiling — validate pose thread achieves ≥30Hz on target hardware; validate render loop maintains 60fps; measure gesture→action latency (target ≤200ms); document memory usage; profile for GC pauses in hot paths; optimize any bottlenecks found
- [x] T031 Code quality pass — run pylint/mypy on all source files; fix any type errors or lint violations; ensure all public functions have docstrings; verify no circular imports between pose/, fruit_slicing/, conductor/, common/; confirm constitution compliance (no dead code, no type: ignore without justification)

### Validation

- [x] T032 Run quickstart.md validation scenarios A through F: A (basic fruit-slicing gameplay), B1 (camera unavailable), B2 (bomb avoidance), B3 (golden watermelon), C (basic conductor gameplay), D1 (squat gesture), D2 (arms-extend gesture), E (keyboard fallback all 5 keys), F (offline mode verification); document pass/fail for each scenario

---

## Phase 6: Enhancement — Skeleton Overlay + Calibration Removal (2026-07-12)

**Goal**: "进入游戏画面能看到站立的人，没有校准姿态过程" — Show player's pose skeleton in real-time, remove calibration step.

**Independent Test**: Launch game → skeleton visible immediately → no calibration screen → countdown with skeleton → gameplay with skeleton overlay

### Implementation for Enhancement

- [x] T033 Fix frame feeding bug in `main.py` — add `camera.read_frame()` → `pose_thread.push_frame(frame)` in the main game loop before `pose_thread.get_pose()` calls; without this fix, PoseThread._frame_queue is always empty and `get_pose()` returns None; insert frame reading at top of while loop in `_run_game_loop()`
- [x] T034 Create `common/skeleton.py` — real-time pose skeleton renderer: define `POSE_CONNECTIONS` list (35 bone pairs from MediaPipe); define `SKELETON_COLORS` dict (face: white, torso: cyan, left_arm: green, right_arm: red, left_leg: blue, right_leg: orange); implement `render_skeleton(surface, landmarks, width, height, visibility_threshold=0.5, line_width=3, joint_radius=4)` that: converts normalized [0,1] landmarks to pixel coords, filters by visibility ≥ 0.5, draws bones (lines) between connected landmarks (skip if either endpoint occluded), draws joints (circles) on top; use `pose/landmarks.py` index constants
- [x] T035 Remove calibration from `common/calibration.py` — delete the file entirely; remove import from `fruit_slicing/game.py`, `fruit_slicing/entities.py`, `conductor/game.py`, `conductor/gesture.py`
- [x] T036 Update `fruit_slicing/entities.py` — remove `CalibrationData` import, remove `CALIBRATE = "calibrate"` from GamePhase enum, remove `calibration: Optional[CalibrationData]` field from `FruitSlicingState`
- [x] T037 Update `fruit_slicing/game.py` — remove calibration phase: delete `GamePhase.CALIBRATE` import, change initial phase from `GamePhase.CALIBRATE` to `GamePhase.COUNTDOWN`, remove calibration block (lines ~104-112), remove `state.calibration` assignment; add frame feeding: `frame = camera.read_frame()` + `pose_thread.push_frame(frame)` at top of main loop
- [x] T038 Refactor `conductor/gesture.py` — replace `CalibrationData` dependency with hardcoded defaults: `__init__(self, standing_hip_y: float = 0.55, arm_span_factor: float = 0.6)`; update `classify()` to use `self._standing_hip_y` instead of `self._calibration.standing_hip_y`; update arms_extend check to use `screen_width * self._arm_span_factor` instead of `self._calibration.arm_span`
- [x] T039 Update `conductor/game.py` — remove calibration phase: delete `"calibrate"` phase, change initial phase to `"countdown"`, remove calibration block (lines ~73-81), instantiate `ConductorGestureClassifier()` with defaults instead of calibration data; add frame feeding: `frame = camera.read_frame()` + `pose_thread.push_frame(frame)` at top of main loop
- [x] T040 [P] Integrate skeleton into `fruit_slicing/game.py` — import `common.skeleton.render_skeleton`; in PLAYING phase, after `render_background()`, call `render_skeleton(screen, pose.landmarks, w, h)` using the latest pose data; also render skeleton during COUNTDOWN phase
- [x] T041 [P] Integrate skeleton into `conductor/game.py` — import `common.skeleton.render_skeleton`; in PLAYING phase, after `render_starfield()`, call `render_skeleton(screen, pose.landmarks, w, h)` using the latest pose data; also render skeleton during COUNTDOWN phase
- [x] T042 [P] Implement `tests/test_skeleton.py` — unit tests for common/skeleton.py: test POSE_CONNECTIONS has 35 pairs; test render_skeleton with mock pygame surface (verify draw calls); test visibility filtering (landmarks below threshold not drawn); test bone skipping when endpoint occluded; test color mapping per body region

### Validation

- [x] T043 Run quickstart.md validation scenario G (skeleton overlay verification): launch game, verify skeleton appears in menu, countdown, and gameplay for both games; verify no calibration screen appears; verify skeleton tracks movements in real-time

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──→ Phase 2: Foundational ──→ Phase 3: US1 ──→ Phase 4: US2 ──→ Phase 5: Polish
                                                                   │
                                                                   └──→ Phase 6: Enhancement
```

- **Phase 1 (Setup)**: No dependencies — starts immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion — MVP deliverable
- **Phase 4 (US2)**: Depends on Phase 2 completion — can start after US1 OR in parallel
- **Phase 5 (Polish)**: Depends on Phase 3 (at minimum) and Phase 4 completion
- **Phase 6 (Enhancement)**: Depends on Phase 5 completion — modifies existing code

### User Story Dependencies

- **US1 (Fruit-Slicing, P1)**: Can start after Phase 2 — NO dependencies on US2
- **US2 (Conductor, P2)**: Can start after Phase 2 — independent of US1, shares only pose pipeline + common modules

### Within Each User Story

- Entity definitions FIRST (T013 for US1, T020 for US2)
- Game logic modules in PARALLEL after entities (T014-T018 for US1, T021-T024 for US2)
- Game loop LAST (T019 for US1, T025 for US2) — depends on all game modules

### Parallel Execution Opportunities

#### Phase 1 — Setup (2 parallel groups)
```
Group 1 (sequential): T001 (directory structure)
Group 2 (parallel):   T002 (config.py) ‖ T003 (sys_ui.py)
```

#### Phase 2 — Foundational (3 parallel groups)
```
Group 1 (sequential): T004 (model_downloader)
Group 2 (parallel):   T005 (camera) ‖ T006 (detector) ‖ T007 (landmarks)
Group 3 (sequential): T008 (thread) → T009 (calibration) → T010 (scores) → T011 (menu) → T012 (main.py)
```

#### Phase 3 — US1 Fruit-Slicing (2 parallel groups)
```
Group 1 (sequential): T013 (entities)
Group 2 (parallel):   T014 (spawner) ‖ T015 (collision) ‖ T016 (scoring) ‖ T017 (audio) ‖ T018 (renderer)
Group 3 (sequential): T019 (game.py) — integrates all above
```

#### Phase 4 — US2 Conductor (2 parallel groups)
```
Group 1 (sequential): T020 (targets)
Group 2 (parallel):   T021 (gesture) ‖ T022 (music) ‖ T023 (scoring) ‖ T024 (renderer)
Group 3 (sequential): T025 (game.py) — integrates all above
```

#### Phase 5 — Polish (4 parallel tasks)
```
All parallel: T026 (test_landmarks) ‖ T027 (test_collision) ‖ T028 (test_scoring) ‖ T029 (test_spawner)
Sequential after tests: T030 (performance) → T031 (code quality) → T032 (validation)
```

#### Phase 6 — Enhancement (3 parallel groups)
```
Group 1 (sequential): T033 (frame feeding fix) → T034 (skeleton.py) → T035 (delete calibration)
Group 2 (parallel):   T036 (entities.py) ‖ T037 (fruit_slicing/game.py) ‖ T038 (gesture.py) ‖ T039 (conductor/game.py)
Group 3 (parallel):   T040 (skeleton in fruit_slicing) ‖ T041 (skeleton in conductor) ‖ T042 (test_skeleton)
Group 4 (sequential): T043 (validation)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) — Recommended

1. Complete Phase 1: Setup (~5 min)
2. Complete Phase 2: Foundational (~30 min) — **Critical path**
3. Complete Phase 3: US1 Fruit-Slicing (~20 min)
4. **🛑 STOP AND VALIDATE**: Run quickstart Scenario A. Play the game. Confirm slicing works.
5. Deploy/demo if ready — you have a working motion-sensing game!

### Incremental Delivery

1. Phase 1 + Phase 2 → Pose pipeline ready, menu launches
2. + Phase 3 → Fruit-slicing playable (MVP!)
3. + Phase 4 → Conductor playable (full feature set)
4. + Phase 5 → Production quality (tests, performance, validation)

### Key Risk Mitigations

| Risk | Mitigation | Task |
|------|------------|------|
| MediaPipe API incompatibility | Test detector.py in isolation first | T006 |
| Camera permission denied | sys_ui shows clear recovery instructions | T003, T012 |
| Frame rate below 30Hz | Profile before optimizing; use VIDEO mode not LIVE_STREAM | T030 |
| Gesture false positives | Calibrate thresholds per user; require minimum velocity | T009, T007 |
| Audio synthesis clipping | Use `// 3` averaging for chord mixing | T017, T022 |
| Model download fails | Show retry/quit dialog; allow manual model placement | T004 |
| Frame feeding bug | Fix wiring: camera.read_frame() → pose_thread.push_frame() | T033 |
| Calibration removal breaks conductor | Hardcoded defaults for squat/arm-span thresholds | T038 |

### Enhancement Strategy (Phase 6)

1. Fix frame feeding bug first (T033) — prerequisite for all pose data
2. Create skeleton renderer (T034) — independent module
3. Remove calibration (T035-T039) — parallel file modifications
4. Integrate skeleton into both games (T040-T041) — parallel
5. Add tests (T042) — parallel with integration
6. Validate (T043) — final check

---

## Notes

- [P] tasks = different files, no dependencies — safe to parallelize
- [US1]/[US2] labels trace tasks to user stories for requirements coverage
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at Phase 3 checkpoint to validate MVP before proceeding
- Constitution requires: type hints on all code, no `as any`/`type: ignore`, docstrings on public API
- No image/audio assets in repo — everything procedural (constitution + spec constraint)
- Camera frames must NEVER be written to disk or transmitted (privacy constraint)
