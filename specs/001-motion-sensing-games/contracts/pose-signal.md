# Contract: Pose → Gesture Event Pipeline

*Interface between the pose detection thread and game logic*

## Data Flow

```
Camera (OpenCV) → Pose Landmarker (MediaPipe) → Gesture Classifier → Game Loop
    30Hz                30Hz                       30Hz               60fps
     |                    |                          |                   |
  frame_buffer    PoseFrame (33 kpts)         GestureEvent       consume events
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

## Calibration Contract

Calibration produces a `CalibrationData` object that all gesture classifiers
reference as baseline. Re-calibration occurs on each game start.

```python
@dataclass
class CalibrationData:
    shoulder_width: float        # used for: distance scaling
    standing_hip_y: float        # used for: squat threshold (hip_y > baseline + offset)
    arm_span: float              # used for: arms_extend threshold (> 80% of span)
    torso_angle: float           # used for: lean detection
    confidence: float            # >0.7 required to proceed
```
