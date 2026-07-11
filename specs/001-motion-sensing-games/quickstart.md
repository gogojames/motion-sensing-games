# Quickstart: Motion-Sensing Games

*Validation guide for running and testing the feature*

## Prerequisites

- Python 3.11 or 3.12 installed
- A built-in or USB webcam (720p+ recommended)
- Standing area ~1.5–2.5m from camera
- Internet connection (first run only — for model download)

## Setup

```bash
# 1. Navigate to project root
cd motion-sensing-games

# 2. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate   # macOS
# .venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

**`requirements.txt` content:**
```
mediapipe-tasks>=0.10.0
opencv-python>=4.8.0
numpy>=1.24.0
pygame>=2.5.0
```

## First Run

```bash
python main.py
```

On first launch:
1. **Model download**: If `models/pose_landmarker_lite.task` is missing, a
   download dialog appears. The ~5.5MB model downloads once from Google's
   CDN. Shows progress bar.
2. **Camera permission**: macOS will prompt for camera access. Grant it.
3. **Calibration**: Stand naturally for 2 seconds — the game detects your
   pose and calibrates.
4. **Main menu**: Both game modes are available.

Subsequent runs: fully offline, no network access.

## Validation Scenarios

### Scenario A: Fruit-Slicing — Basic Gameplay

```bash
python main.py
# Main menu appears — select "Fruit Slicing" by slicing the menu option
```

**Expected outcomes:**
1. Calibration screen appears → stand naturally for 2 seconds
2. 3-2-1 countdown → fruits begin flying from screen bottom
3. Wave hand rapidly → "hand blade" visual trail appears
4. Hand intersects a fruit → fruit splits with particle effect + slicing sound
5. Score increments on screen
6. Miss 3 fruits → game ends, score displayed

**Pass criteria**: Within 3 minutes, player can start game, slice ≥1 fruit,
and reach game-over screen.

### Scenario B: Fruit-Slicing — Edge Cases

**B1 — Camera unavailable:**
1. Start `main.py` while camera is in use (e.g., Zoom call)
2. Expected: Native dialog "Camera is in use by another application. Please
   close it and restart."
3. **Pass**: Message appears, app exits gracefully.

**B2 — Bomb avoidance:**
1. Play until a dark/spiky fruit (bomb) appears among normal fruits
2. Slice through the bomb
3. Expected: Explosion effect, lives decrement from 3 to 2, game continues
   if lives remain, or game over if last life
4. **Pass**: Bomb hit correctly reduces lives with explosion effect.

**B3 — Golden watermelon:**
1. Play through multiple waves until golden watermelon spawns (5% chance per wave)
2. Slice it
3. Expected: +50 points with special golden sparkle effect
4. **Pass**: Golden watermelon awards 50 points when sliced.

### Scenario C: Conductor Game — Basic Gameplay

```bash
python main.py
# Main menu — select "Rhythm Conductor"
```

**Expected outcomes:**
1. Calibration: Stand naturally for 2 seconds
2. 3-2-1 countdown begins
3. Star notes approach from distance toward target rings
4. Reach hand to cyan target → drum layer activates
5. Reach other hand to orange target → bass layer activates
6. Hold both hands for purple target → melody layer activates
7. Miss notes → combo resets, score stops growing
8. Song ends after ~2 minutes → rank + score displayed
9. Raise both hands 1 second → returns to menu

**Pass criteria**: Player can complete one full play-through, achieving at
least rank "C" and hearing at least 2 music layers.

### Scenario D: Conductor — Special Gestures

**D1 — Squat detection (gold star gate):**
1. During gameplay, a gold target ring appears with a down-arrow indicator
2. Player squats (lowers hips below calibration baseline)
3. Expected: Gold burst effect, score bonus (+30), star power meter fills
4. **Pass**: Squat gesture triggers gold target hit.

**D2 — Arms extended (constellation):**
1. During gameplay, a target appears with an "arms wide" indicator
2. Player extends both arms wide (>120° from torso) and holds
3. Expected: White constellation outline appears, hold for ~0.5s triggers hit
4. **Pass**: Arms-extend gesture triggers constellation hit.

### Scenario E: Keyboard Fallback

All game actions must also work via keyboard:

| Key | Action | Test |
|-----|--------|------|
| Space | Start game / restart | Press at menu → game starts |
| P | Pause/Resume | Press during gameplay → game pauses |
| F | Toggle fullscreen | Press → window toggles fullscreen |
| R | Restart (game over) | Press on game-over → returns to menu |
| Esc | Quit | Press → exit game (with confirmation) |

### Scenario F: Offline Mode Verification

1. Complete first run (model downloaded)
2. Disconnect from internet
3. Launch `main.py` again
4. Game should start without any network errors or delays
5. Play both games — full functionality should work offline

## Test Data Locations

| Data | Path (macOS) | Path (Windows) |
|------|-------------|----------------|
| High scores | `~/Library/Application Support/motion-sensing-games/highscores.json` | `%APPDATA%/motion-sensing-games/highscores.json` |
| Config | `~/Library/Application Support/motion-sensing-games/config.json` | `%APPDATA%/motion-sensing-games/config.json` |
| Model | `./models/pose_landmarker_lite.task` | `.\models\pose_landmarker_lite.task` |

## Validation Summary Log

```text
Validation Run: ___________   Date: ___________

[ ] A: Basic fruit-slicing gameplay
[ ] B1: Camera unavailable error
[ ] B2: Bomb avoidance
[ ] B3: Golden watermelon (if encountered)
[ ] C: Basic conductor gameplay
[ ] D1: Squat gesture (conductor)
[ ] D2: Arms-extend gesture (conductor)
[ ] E: Keyboard fallback (all 5 keys)
[ ] F: Offline mode verification

Notes: ________________________________________
```
