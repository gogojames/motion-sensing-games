# Contract: Persistent Data Files

## Path

Platform-dependent user config directory:
- macOS: `~/Library/Application Support/motion-sensing-games/`
- Windows: `%APPDATA%/motion-sensing-games/`

## File: `highscores.json`

```json
{
  "schema_version": 1,
  "fruit_slicing": {
    "top_scores": [
      {
        "score": 1250,
        "combo": 15,
        "fruits_sliced": 87,
        "date": "2026-07-11"
      }
    ],
    "max_entries": 10
  },
  "conductor": {
    "top_scores": [
      {
        "score": 8500,
        "rank": "A",
        "max_combo": 42,
        "track": "Star Voyage",
        "date": "2026-07-11"
      }
    ],
    "max_entries": 10
  }
}
```

## File: `config.json`

```json
{
  "schema_version": 1,
  "camera_id": 0,
  "preferred_resolution": [640, 480],
  "fullscreen": false,
  "sound_enabled": true,
  "motion_sensitivity": 0.5,
  "model_path": "models/pose_landmarker_lite.task"
}
```
