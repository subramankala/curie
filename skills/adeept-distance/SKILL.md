---
name: adeept-distance
description: Read the current forward distance from Curie's local ultrasonic sensor on this Raspberry Pi host. Use when the user asks how far an obstacle is, whether the path ahead is clear, or for a live distance reading from the robot.
metadata:
  {
    "openclaw":
      {
        "emoji": "📏",
        "os": ["linux"],
        "requires": { "bins": ["python3"] },
      },
  }
---

# adeept-distance

Use this skill to read Curie's forward ultrasonic distance sensor.

Routing rules:

- Always run locally on the Raspberry Pi host.
- Never use connected nodes for this skill.
- Read the ultrasonic sensor directly instead of estimating from camera images.

## Command

Run:

```bash
python3 /home/curie/openclaw/skills/adeept-distance/scripts/distance.py
```

Optional machine-readable output:

```bash
python3 /home/curie/openclaw/skills/adeept-distance/scripts/distance.py --format json
```

Keep a bounded following distance:

```bash
python3 /home/curie/openclaw/skills/adeept-distance/scripts/keep_distance.py --target 30 --tolerance 5 --speed 35 --duration 5
```

## Response style

Reply briefly with the measured distance in centimeters and whether the path is clear if that was part of the request.
For keep-distance mode, report the target, duration, and last measured distance.
