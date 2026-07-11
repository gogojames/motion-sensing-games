# Data Model: Motion-Sensing Games

*Generated: 2026-07-11*

## Shared Entities

### Pose Frame
The output of a single MediaPipe Pose Landmarker inference cycle.
```python
@dataclass
class PoseFrame:
    landmarks: np.ndarray          # shape (33, 3) — normalized x, y, visibility for each keypoint
    world_landmarks: np.ndarray    # shape (33, 3) — world-space x, y, z in meters
    timestamp_ms: int              # capture timestamp for velocity computation
    handedness: str | None         # "left", "right", or None if hands not visible
```

### Calibration Data
Captured during the 2-second standing calibration phase.
```python
@dataclass
class CalibrationData:
    shoulder_width: float               # pixel distance between shoulders
    standing_hip_y: float               # baseline hip Y position (for squat detection)
    arm_span: float                     # max pixel distance between wrists
    torso_angle: float                  # torso lean from vertical (degrees)
    confidence: float                   # calibration quality score (0.0–1.0)
```

### High Score Record
Persisted to `data/highscores.json`, updated at game end.
```python
@dataclass
class HighScoreRecord:
    game_mode: str                      # "fruit_slicing" | "conductor"
    score: int                          # final score
    # Fruit-slicing specific:
    combo: int | None                   # max combo achieved
    fruits_sliced: int | None           # total fruits sliced
    # Conductor specific:
    rank: str | None                    # "S", "A", "B", "C", "D", "F"
    max_combo: int | None               # highest combo streak
    track_name: str | None              # "Star Voyage" (the ~2-min piece)
    # Common:
    date: str                           # ISO date string
```

### Gesture Event
An atomic action recognized by the gesture pipeline, consumed by game logic.
```python
@dataclass
class GestureEvent:
    type: str                           # GestureType enum member
    hand: str | None                    # "left", "right", "both", or None
    position: tuple[float, float]       # screen-space (x, y) of gesture origin
    velocity: float                     # gesture speed (pixels/sec)
    confidence: float                   # classification confidence (0.0–1.0)
    timestamp: int                      # game time (ms) when detected
```

```python
class GestureType(Enum):
    # Fruit-slicing gestures
    HAND_BLADE = "hand_blade"           # fast hand swipe
    HANDS_UP = "hands_up"               # both hands raised (menu/restart)
    WAVE_SELECT = "wave_select"         # horizontal wave for menu selection

    # Conductor gestures
    LEFT_HAND_REACH = "left_reach"      # left hand to target (cyan)
    RIGHT_HAND_REACH = "right_reach"    # right hand to target (orange)
    DUAL_HAND_SYNC = "dual_sync"        # both hands together (purple)
    SQUAT = "squat"                     # body lowers (gold)
    ARMS_EXTEND = "arms_extend"         # arms wide hold (constellation)

    # Calibration
    HANDS_UP_HOLD = "hands_up_hold"     # hands up for 1 second (start)
    STANDING_NEUTRAL = "standing"       # natural standing (calibration)
```

---

## Fruit-Slicing Game Entities

### GameState (Fruit-Slicing)
```python
@dataclass
class FruitSlicingState:
    phase: GamePhase                    # MENU, CALIBRATE, COUNTDOWN, PLAYING, GAME_OVER
    lives: int                          # start at 3, decrement on bomb hit or fruit miss
    score: int                          # current session score
    combo: int                          # current combo streak
    max_combo: int                      # best combo this session
    fruits_sliced: int                  # running total
    fruits_missed: int                  # running total (3 → game over)
    wave: int                           # current wave number (difficulty escalates)
    golden_fruit_spawned: bool          # true when golden watermelon is active
```

### GamePhase
```python
class GamePhase(Enum):
    MENU = "menu"                       # Gesture-driven main menu
    CALIBRATE = "calibrate"             # 2-second calibration pose
    COUNTDOWN = "countdown"             # 3-2-1 countdown
    PLAYING = "playing"                 # Active gameplay
    PAUSED = "paused"                   # Paused state
    GAME_OVER = "game_over"             # Results display
```

### Fruit
Spawned by the wave generator; rendered as a procedural circle with color + size.
```python
@dataclass
class Fruit:
    id: int                             # unique spawn ID
    type: FruitType                     # enum with point values
    x: float                            # current pixel x position
    y: float                            # current pixel y position
    vx: float                           # horizontal velocity (px/frame)
    vy: float                           # vertical velocity (px/frame)
    radius: float                       # collision radius in pixels
    rotation: float                     # current rotation angle (for visual variety)
    rotation_speed: float               # degrees per frame
    sliced: bool                        # true when hit by hand blade
    missed: bool                        # true when fallen off screen
    trail: list[tuple[float, float]]    # last 5 positions for motion trail effect
```

```python
class FruitType(Enum):
    WATERMELON = ("watermelon", 10, (34, 139, 34))     # dark green, 10pts
    ORANGE = ("orange", 20, (255, 165, 0))             # orange, 20pts
    APPLE = ("apple", 15, (255, 0, 0))                 # red, 15pts
    BANANA = ("banana", 15, (255, 255, 0))             # yellow, 15pts
    GOLDEN_WATERMELON = ("golden", 50, (255, 215, 0))  # gold, 50pts, rare

    def __init__(self, name, points, color):
        self.display_name = name
        self.points = points
        self.color = color
```

### Bomb
Same class as Fruit but with `is_bomb=True`. Hitting a bomb ends the game.
```python
@dataclass
class Bomb:
    x: float
    y: float
    vx: float
    vy: float
    radius: float                       # slightly larger than fruits for visibility
    rotation: float
    rotation_speed: float
    exploded: bool
```

### Hand Blade
Registered when wrist movement exceeds velocity threshold.
```python
@dataclass
class HandBlade:
    hand: str                           # "left" | "right"
    start_pos: tuple[float, float]      # position at threshold crossing
    end_pos: tuple[float, float]        # current position while above threshold
    velocity: float                     # pixels/sec at peak
    lifetime: int                       # frames remaining for visual trail
    arc: list[tuple[float, float]]      # trajectory points for swipe trail render
```

### Wave Config
Defines the spawn pattern for a wave of fruits.
```python
@dataclass
class WaveConfig:
    wave_number: int
    fruit_count: int
    bomb_count: int
    golden_chance: float                # probability (0.0–1.0) of golden watermelon
    min_speed: float
    max_speed: float
    spawn_interval: float               # seconds between each fruit launch
    trajectory_types: list[str]         # "arc", "straight", "lob", "fan"

    # Difficulty scales with wave_number
    @property
    def difficulty_multiplier(self) -> float:
        return 1.0 + (self.wave_number - 1) * 0.15
```

### Scoring Rules
| Action | Points | Notes |
|--------|--------|-------|
| Slice fruit | Fruit type points | Base points above |
| Combo (2+) | +5 per consecutive slice | Resets on miss or bomb |
| Combo (5+) | +10 per consecutive slice | Stacks with 5+ bonus |
| Golden watermelon | +50 | Rare spawn |
| Miss fruit | -1 life | 3 lives total |
| Hit bomb | -1 life + explosion | Immediate explosion anim |

---

## Conductor Game Entities

### GameState (Conductor)
```python
@dataclass
class ConductorState:
    phase: ConductorPhase
    score: int
    combo: int
    max_combo: int
    star_power: float                   # 0.0 → 1.0, fills on hits
    supernova_active: bool
    supernova_timer: float              # seconds remaining in supernova
    music_layers: int                   # 0–4 (drums, bass, melody, harmony)
    current_track_position: float       # seconds into the ~2-min track
    rank: str | None                    # set at game end
```

### ConductorPhase
```python
class ConductorPhase(Enum):
    MENU = "menu"
    CALIBRATE = "calibrate"
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    RESULT = "result"                   # Score display
```

### StarNote
A target approaching from the distance in the conductor game.
```python
@dataclass
class StarNote:
    id: int
    target_type: StarTargetType         # defines required gesture
    approach_duration: float            # seconds from edge to target ring
    time_remaining: float               # countdown to hit window
    target_x: float                     # screen position of target ring
    target_y: float
    ring_radius: float                  # size of the target ring
    hit: bool
    missed: bool
    score_bonus: int                    # bonus points for this note
```

```python
class StarTargetType(Enum):
    LEFT_HAND = ("cyan", (0, 255, 255), 10)
    RIGHT_HAND = ("orange", (255, 165, 0), 10)
    DUAL_HAND = ("purple", (128, 0, 128), 25)
    SQUAT = ("gold", (255, 215, 0), 30)
    CONSTELLATION = ("white", (255, 255, 255), 20)

    def __init__(self, display, color, base_points):
        self.display_name = display
        self.color = color
        self.base_points = base_points
```

### MusicLayer
A procedurally generated audio layer that activates on combo milestones.
```python
@dataclass
class MusicLayer:
    name: str                           # "drums", "bass", "melody", "harmony"
    enabled: bool
    volume: float
    waveform_type: str                  # "sine", "square", "saw", "noise"
    frequency_range: tuple[float, float] # min, max Hz
    pattern: list[float]                # rhythmic pattern (relative timing)
    tempo_multiplier: float             # tempo = base_tempo * multiplier
```

### StarPower
```python
@dataclass
class StarPower:
    current: float                      # 0.0–1.0
    decay_rate: float                   # per second when not hitting notes
    fill_rate: float                    # per successful hit
    supernova_threshold: float          # 1.0 = trigger supernova
    supernova_duration: float           # 8 seconds
```

### Ranking
```
Score >= 9000 → S (Stellar)
Score >= 7000 → A (Astral)
Score >= 5000 → B (Bright)
Score >= 3000 → C (Comet)
Score >= 1000 → D (Dim)
Score  < 1000 → F (Fading)
```

---

## State Machine Transitions

### Fruit-Slicing

```
MENU ──(start gesture/key)──→ CALIBRATE
CALIBRATE ──(2s elapsed)──→ COUNTDOWN
COUNTDOWN ──(3s elapsed)──→ PLAYING
PLAYING ──(lives = 0)──→ GAME_OVER
PLAYING ──(Esc/P key)──→ PAUSED
PAUSED ──(P key)──→ PLAYING
GAME_OVER ──(restart gesture/key)──→ MENU
```

### Conductor

```
MENU ──(hands_up 1s / space)──→ CALIBRATE
CALIBRATE ──(2s neutral pose)──→ COUNTDOWN
COUNTDOWN ──(3s elapsed)──→ PLAYING
PLAYING ──(song ends)──→ RESULT
RESULT ──(hands_up 1s / space)──→ MENU
```
