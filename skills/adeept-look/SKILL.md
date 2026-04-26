---
name: adeept-look
description: Control the local Adeept robot's viewing direction on this Raspberry Pi host. Use when the user asks the robot to look up, look down, look straight, look left, or look right. If the user addresses the assistant as Curie and asks to look somewhere, prefer this skill. This robot's camera has only one degree of freedom: tilt only. Left and right should rotate the wheels/chassis while keeping the camera tilt unchanged. Do not use connected nodes or a phone camera for this skill.
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "os": ["linux"],
        "requires": { "bins": ["python3"] },
      },
  }
---

# adeept-look

Use this skill for the local Adeept robot on this Raspberry Pi.

Important behavior:

- The camera has only one degree of freedom.
- `look up`, `look down`, and `look straight` control the tilt servo only.
- `look left` and `look right` do not pan the camera.
- For left/right, rotate the chassis briefly with the wheels and keep the camera tilt unchanged.

Default assumption for ambiguous robot-view phrases:

- `look up`
- `look down`
- `look straight`
- `look left`
- `look right`
- `curie look up`
- `curie look down`

All of these should target the local Adeept robot on this Pi unless the user explicitly asks for some other device.

Routing rules:

- Always run locally on the Raspberry Pi host.
- Never use connected nodes for this skill.
- Never use a phone camera for this skill.

## Calibrated tilt range

Use the calibrated tilt range discovered on this robot:

- top: `75`
- straight: `48`
- bottom: `20`

Do not use the old generic `0..180` assumption for camera tilt commands.

## Command

Run:

```bash
python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py <direction>
```

Supported directions:

- `up`
- `down`
- `straight`
- `left`
- `right`

Optional flags:

- `--speed <0-100>` for left/right rotation speed
- `--duration <seconds>` for left/right rotation time

Examples:

```bash
python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py up
python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py straight
python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py left --speed 35 --duration 0.35
python3 /home/curie/openclaw/skills/adeept-look/scripts/look.py right --speed 35 --duration 0.35
```

## Response style

After running the command, reply briefly with what moved, for example:

- `Camera tilted up.`
- `Camera tilted down.`
- `Camera centered to straight ahead.`
- `Robot rotated left with the wheels; camera tilt stayed fixed.`

If the command fails, report the hardware or import error briefly.
