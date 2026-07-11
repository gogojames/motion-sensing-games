# Feature Specification: Motion-Sensing Games

**Feature Branch**: `001-motion-sensing-games`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "一颗普通摄像头用一套姿态识别技术制作体感游戏，挥手切瓜的体感切水果、全身节奏音乐指挥家游戏。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fruit-Slicing Game (Priority: P1)

A player stands in front of their computer's webcam and plays a fruit-slicing game
using hand gestures. Fruits fly up from the bottom of the screen, and the player
swipes their hand through the air to slice them. Each sliced fruit adds to the
score. Missing fruits or hitting bombs ends the game.

**Why this priority**: This is the primary game concept and provides the most
immediate "wow factor" for motion-sensing gameplay. It serves as the MVP that
validates the core pose-tracking technology works reliably before investing in
the more complex full-body conductor game.

**Independent Test**: Can be tested by launching the game in a browser, standing
in front of the camera, and performing swipe gestures. The screen should show
fruits being sliced in response to hand movements, with score updating in
real-time and game-over triggering after missing 3 fruits or hitting a bomb.

**Acceptance Scenarios**:

1. **Given** the player has granted camera permission and is standing within
   camera view, **When** the game starts, **Then** fruits begin appearing from
   the bottom of the screen and floating upward with random trajectories.
2. **Given** fruits are visible on screen, **When** the player performs a rapid
   horizontal or vertical hand swipe through a fruit's position, **Then** the
   fruit visually splits in half with a visual effect and the score increases
   by the fruit's point value.
3. **Given** a bomb object appears among the fruits, **When** the player swipes
   through the bomb, **Then** the game ends immediately with an explosion effect
   and the final score is displayed.
4. **Given** the player misses 3 fruits (they fall off screen unsliced),
   **When** the third fruit is missed, **Then** the game ends and the final
   score is displayed.
5. **Given** the game has ended, **When** the player sees the game-over screen,
   **Then** they can restart the game with a clear hand gesture (e.g., raising
   both hands) or by clicking a restart button.

---

### User Story 2 - Full-Body Rhythm Conductor Game (Priority: P2)

A player stands in front of the webcam and uses their entire body to conduct
an orchestra. The game tracks the player's arm and body movements to control
the tempo, volume, and intensity of a musical piece. Moving arms faster
increases tempo; wider gestures increase volume.

**Why this priority**: This game showcases the full-body tracking capability of
the pose estimation system and provides a more immersive, expressive experience.
It is P2 because it requires more sophisticated gesture interpretation (two-arm
tracking, dynamic tempo mapping) and can be built on top of the pose pipeline
validated by the fruit-slicing game.

**Independent Test**: Can be tested by launching the conductor game in a
browser, standing in front of the camera, and making conducting motions with
both arms. Music should respond in real-time to gesture speed and amplitude.

**Acceptance Scenarios**:

1. **Given** the player is in camera view and the conductor game has loaded,
   **When** the player moves their right arm in a conducting pattern (up-down
   or left-right), **Then** the music plays at a tempo proportional to the arm
   movement speed.
2. **Given** music is playing, **When** the player raises both arms wider
   apart, **Then** the music volume increases proportionally to arm span.
3. **Given** the player is conducting, **When** they slow their arm movements
   significantly, **Then** the music tempo slows accordingly and gradually
   fades to silence if movements stop entirely.
4. **Given** a musical piece is selected and playing, **When** the player
   changes their gesture intensity (speed + range of motion), **Then** the
   musical arrangement dynamically shifts (e.g., from soft strings to full
   orchestra) in response.

---

### Edge Cases

- What happens when the player moves partially or fully out of camera frame?
  System should pause/resume gracefully and show an on-screen indicator when
  the player is not fully visible.
- How does the system handle multiple people in the camera frame?
  The system should track the nearest/closest person and ignore others, or
  prompt the user to ensure only one person is in frame.
- How does the system handle low-light conditions where pose detection may
  be less accurate?
  Display a "low light" warning and suggest improving lighting, while
  continuing to attempt pose detection.
- What happens when the camera is already in use by another application?
  Show a clear error message with instructions to close the other app.
- How does the fruit-slicing game handle fruits that appear at the very edge
  of the screen where gestures are harder to reach?
  Fruits should spawn within a comfortable gesture zone, not at extreme edges.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect and track the player's full-body pose
  (including arms, hands, torso, and head) using the web camera feed in
  real-time.
- **FR-002**: System MUST recognize hand swipe gestures (direction and speed)
  for the fruit-slicing game mode.
- **FR-003**: System MUST recognize two-arm conducting gestures (movement
  pattern, speed, amplitude, symmetry) for the conductor game mode.
- **FR-004**: System MUST display a real-time visual overlay showing the
  detected pose skeleton to help the player understand their tracked
  positioning.
- **FR-005**: Players MUST be able to choose between fruit-slicing and
  conductor game modes from a main menu.
- **FR-006**: System MUST generate fruit objects with randomized size, type,
  trajectory, and speed in the fruit-slicing game.
- **FR-007**: System MUST track and display a running score during gameplay
  for both game modes.
- **FR-008**: System MUST provide visual and/or audio feedback for successful
  gesture actions (fruit slice effect, music response).
- **FR-009**: System MUST include a 5-second countdown with visual guidance
  before gameplay begins, showing the player their detected pose.
- **FR-010**: System MUST save the player's highest score locally and display
  it on the main menu.
- **FR-011**: System MUST handle camera permission denial gracefully, showing
  clear instructions for enabling camera access.
- **FR-012**: System MUST render smooth 2D/3D game graphics at a minimum of
  30 frames per second with no perceivable input lag.

### Key Entities

- **Player**: The human user detected by the camera. Represented by a pose
  skeleton with tracked joints (shoulders, elbows, wrists, hips, knees,
  ankles, head). Each player has a session score history.
- **Game Session**: A single play-through of either game mode. Contains:
  start time, game mode, final score, and duration.
- **Fruit Object**: In the fruit-slicing game, a spawned target with:
  type (watermelon, orange, apple, banana, bomb), size, trajectory arc,
  speed, and point value. Fruits are "sliceable" when the player's hand
  trajectory intersects their bounding area.
- **Gesture Definition**: A mapping between a recognized body movement
  pattern and a game action. Examples: "swipe_right" → slice, "arms_up" →
  increase volume, "fast_conduct" → increase tempo.
- **Music Track**: In the conductor game, a musical piece with: base tempo,
  instrument layers (strings, brass, percussion), volume envelope, and
  arrangement states that respond to gesture parameters.
- **High Score Record**: Persisted local data containing: player's highest
  score per game mode, and date achieved.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time player can successfully start and play the
  fruit-slicing game within 60 seconds of first seeing the main menu,
  without external instructions.
- **SC-002**: The gesture recognition correctly identifies a deliberate
  slicing swipe with ≥90% accuracy under normal indoor lighting conditions
  (measured across 100 test swipes by 5 different users).
- **SC-003**: The conductor game responds to arm movement tempo changes
  within ≤200ms of the gesture change, creating a perceptually instantaneous
  musical response.
- **SC-004**: 80% of playtesters report that the motion controls feel
  "responsive" or "very responsive" in a post-play survey.
- **SC-005**: The system detects and tracks the player's pose at minimum
  20 frames per second on a standard consumer laptop with built-in webcam
  (no external GPU required).
- **SC-006**: 70% of playtesters across both games report that they would
  play again in a post-play survey.

## Assumptions

- **Target platform**: Web browser (Chrome, Edge, Firefox, Safari) running on
  a desktop or laptop computer with an integrated or USB webcam. Mobile
  browser support is explicitly out of scope for v1.
- **Camera quality**: Standard consumer webcam (720p or higher, 30fps or
  higher). No specialized depth-sensing or infrared cameras required.
- **Single-player**: All games are designed for a single player at a time.
  Multiplayer is out of scope for v1.
- **Internet connection**: Pose estimation runs entirely on-device in the
  browser. No cloud processing required. An internet connection is needed
  only for initial page load.
- **Lighting conditions**: Normal indoor lighting. Very low light or extreme
  backlight may reduce tracking accuracy.
- **Player distance**: Player stands approximately 1.5-3 meters from the
  camera, with full upper body (fruit game) or full body (conductor game)
  visible in frame.
- **Audio**: The fruit-slicing game includes sound effects for slicing
  and game events. The conductor game requires audio output for the
  musical piece. Browser autoplay policies must be handled.
- **No user accounts**: No login, registration, or online leaderboard in
  v1. All scores are stored locally in the browser.
