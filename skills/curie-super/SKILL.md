---
name: curie-super
description: Run higher-level Curie robot behaviors composed from the existing movement, distance, line, light, and camera primitives. Use for tasks like scout ahead, inspect obstacle, or sentry watch.
metadata:
  {
    "openclaw":
      {
        "emoji": "🧭",
        "os": ["linux"],
        "requires": { "bins": ["python3", "rpicam-still"] },
      },
  }
---

# curie-super

Use this skill for bounded multi-step Curie behaviors.

Routing rules:

- Always run locally on the Raspberry Pi host.
- Compose existing local robot scripts instead of inventing new control paths.
- Keep runs bounded in time or distance.

## Commands

Scout ahead:

```bash
python3 /home/curie/openclaw/skills/curie-super/scripts/scout_ahead.py --distance 100 --photo
```

Inspect obstacle:

```bash
python3 /home/curie/openclaw/skills/curie-super/scripts/inspect_obstacle.py --target 25 --view straight
```

Sentry:

```bash
python3 /home/curie/openclaw/skills/curie-super/scripts/sentry.py --threshold 35 --duration 15
```

## Response style

- Report the bounded run result succinctly.
- Include the saved photo path when a photo was captured.
