# Transition.py

A command-line tool for moving a UAV mission file (waypoints or polygon geofence) from one field's home/reference point to a different field's home point, with an optional rotation.

This is useful when a competition mission plan is designed around a specific field's home coordinate, but you want to rehearse it at a different practice field with a different location and/or orientation — the tool preserves the shape and relative geometry of the mission while re-anchoring it to the new home point.

## How it works

1. Each coordinate in the input file is converted from lat/lon into a local flat-earth offset `(dx, dy)` in meters, measured from the **original** home point.
2. That offset is rotated by the given `--rotation` angle (positive = counter-clockwise, negative = clockwise).
3. The rotated offset is converted back into lat/lon by adding it onto the **new** home point.

This keeps distances and angles between waypoints unchanged — only the origin and orientation shift.

## Supported file types

- `wp` — Mission Planner / ArduPilot `.waypoints` file (tab-separated). The header line is preserved, and any waypoint at `(0, 0)` is left untouched.
- `poly` — Polygon/geofence file (space-separated `lat lon` per line). Comment lines (`#`) and blank lines are preserved.

## Usage

```
python Transition.py --mode=<wp|poly> --input=<input file> --output=<output file> --orig=<lat,lon> --target=<lat,lon> --rotation=<degrees>
```

| Flag | Required | Description |
|---|---|---|
| `--mode` | Yes | File type: `wp` or `poly` |
| `--input` | Yes | Path to the input file |
| `--output` | Yes | Path to write the transformed file |
| `--orig` | Yes | Home point of the original field, as `lat,lon` |
| `--target` | Yes | Home point of the new field, as `lat,lon` |
| `--rotation` | No | Rotation angle in degrees (default `0`) |

### Example

```
python Transition.py --mode=wp --input="C:\Project\UAV\UAS2026\Waypoint\WPTestUKMod.waypoints" --output="C:\Project\UAV\UAS2026\Waypoint\WPUKPracticeMod.waypoints" --orig=52.780562,-0.707918 --target=52.623818,-1.1750744 --rotation=160
```

This moves a waypoint mission originally anchored at `52.780562, -0.707918` to a practice field anchored at `52.623818, -1.1750744`, rotating the whole plan 160° counter-clockwise.
