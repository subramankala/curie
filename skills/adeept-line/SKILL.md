---
name: adeept-line
description: Read Curie's line tracking sensors and follow a floor line on this Raspberry Pi host. Use when the user asks for line status, whether a line is detected, or to follow a line for a bounded amount of time.
metadata:
  {
    "openclaw":
      {
        "emoji": "➖",
        "os": ["linux"],
        "requires": { "bins": ["python3"] },
      },
  }
---

# adeept-line

Use this skill for Curie's line-tracking sensors.

Routing rules:

- Always run locally on the Raspberry Pi host.
- Never use connected nodes for this skill.
- Keep line following bounded in time; do not start an indefinite vendor loop.

## Commands

Read line sensor state:

```bash
python3 /home/curie/openclaw/skills/adeept-line/scripts/line_status.py
```

Follow a line for a bounded interval:

```bash
python3 /home/curie/openclaw/skills/adeept-line/scripts/follow_line.py --speed 35 --duration 5
```

Reacquire a line by scanning left and right:

```bash
python3 /home/curie/openclaw/skills/adeept-line/scripts/find_line.py --speed 30 --duration 6
```

## Response style

- For status, report left/middle/right values and whether a line is detected.
- For follow mode, report the duration, speed, and whether Curie actually saw a line.
- For find mode, report whether a line was found and the last sensor values.
