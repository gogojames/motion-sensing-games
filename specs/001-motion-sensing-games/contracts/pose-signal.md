# Contract: Pose → Gesture Event Pipeline

*Interface between the pose detection thread and game logic*
*Updated: 2026-07-12 — Removed calibration, added skeleton overlay*

## Data Flow

```
Camera (OpenCV) → Pose Landmarker (MediaPipe) → Gesture Classifier → Game Loop
    30Hz                30Hz                       30Hz               60fps
     |                    |                          |                   |
  frame_buffer    PoseFrame (33 kpts)         GestureEvent       consume events
                                                |
                                          render_skeleton()
```

## Thread-Safe Shared State

```python
# Written by: pose thread (30Hz)
# Read by:     main/render thread (60fps)
# Synchronization: queue.Queue(maxsize=2) for pose frames, Lock for shared state

pose_queue: Queue["PoseFrame"]        # latest pose results (reader takes newest)
gesture_queue: Queue["GestureEvent"]  # recognized gestures (reader dequeues)
shared_state: dict = {                # protected by Lock
    "latest_pose": None,              # most recent PoseFrame for rendering
    "is_tracking": False,             # true when pose is detected
    "frame_width": 640,               # camera resolution
    "frame_height": 480,
}
```

## Gesture Event Format

```json
{
  "type": "HAND_BLADE",
  "hand": "right",
  "position": [0.45, 0.62],
  "velocity": 850.0,
  "confidence": 0.92,
  "timestamp": 15234
}
```

## Skeleton Overlay Contract

The skeleton overlay renders the detected pose in real-time on the pygame surface.

### Input
```python
def render_skeleton(
    surface: pygame.Surface,          # target surface
    landmarks: np.ndarray,            # shape (33, 3) — x, y, visibility
    width: int,                       # surface width in pixels
    height: int,                      # surface height in pixels
    visibility_threshold: float = 0.5, # skip landmarks below this
    line_width: int = 3,              # bone line thickness
    joint_radius: int = 4,            # joint circle radius
) -> None:
```

### Behavior
- Converts normalized [0,1] landmarks to pixel coordinates
- Filters landmarks by visibility (default ≥ 0.5)
- Draws bones (lines) between connected landmarks — skips if either endpoint is occluded
- Draws joints (circles) on top of bones
- Color-coded by body region:
  - Face (0-10): white
  - Torso (11,12,23,24): cyan
  - Left arm (13,15,17,19,21): green
  - Right arm (14,16,18,20,22): red
  - Left leg (25,27,29,31): blue
  - Right leg (26,28,30,32): orange

### MediaPipe POSE_CONNECTIONS (35 bone pairs)
```python
POSE_CONNECTIONS = [
    # Face
    (0,1),(1,2),(2,3),(3,7), (0,4),(4,5),(5,6),(6,8), (9,10),
    # Torso
    (11,12),(11,23),(12,24),(23,24),
    # Left arm
    (11,13),(13,15),(15,17),(15,19),(15,21),(17,19),
    # Right arm
    (12,14),(14,16),(16,18),(16,20),(16,22),(18,20),
    # Left leg
    (23,25),(25,27),(27,29),(29,31),(27,31),
    # Right leg
    (24,26),(26,28),(28,30),(30,32),(28,32),
]
```

### Integration Points
| Game | When | After | Before |
|------|------|-------|--------|
| Fruit slicing | PLAYING phase | render_background() | render_fruit() |
| Conductor | PLAYING phase | render_starfield() | render_target_ring() |
| Both games | COUNTDOWN phase | screen.fill() | countdown text |

## Gesture Thresholds (Hardcoded Defaults)

Since calibration is removed, gesture classifier uses fixed thresholds:

| Threshold | Value | Usage |
|-----------|-------|-------|
| `standing_hip_y` | 0.55 | Squat detection baseline |
| `arm_span_factor` | 0.6 | Arms extend: wrist_distance > screen_width * 0.6 |
| `squat_offset` | 0.12 | Squat trigger: hip_y > standing_hip_y + 0.12 |
