---
name: curie
description: Route commands addressed to Curie to the local `/home/curie/curie` robot CLI on this Raspberry Pi. Use when the user says Curie followed by a robot command such as hey curie go straight, curie turn left, curie battery, curie distance, curie line status, curie follow line for 5 seconds, curie find line, curie keep distance for 5 seconds, curie scout ahead, curie inspect obstacle, curie sentry for 2 minutes, curie set clearance 30 cm, curie look up, curie lights on, or curie take a photo.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎛️",
        "os": ["linux"],
        "requires": { "bins": ["python3", "rpicam-still"] },
      },
  }
---

# curie

Use this skill for the local Adeept robot on this Raspberry Pi whenever the user explicitly addresses Curie.

Primary rule:

- Prefer the local `curie` CLI as the single source of truth for command parsing.
- Do not manually reinterpret the robot command if the local CLI can handle it.
- Do not use connected nodes or a phone camera unless the user explicitly asks for those instead of Curie.

## Command routing

When the user says an addressed command such as:

- `curie battery`
- `curie distance`
- `curie line status`
- `curie follow line for 5 seconds`
- `curie find line`
- `curie keep distance for 5 seconds`
- `curie scout ahead`
- `curie inspect obstacle`
- `curie sentry for 2 minutes`
- `curie set clearance 30 cm`
- `hey curie go straight`
- `curie move forward for 2 seconds`
- `curie turn left 90 degrees`
- `curie look up`
- `curie lights on`
- `curie blinkers fast`
- `curie take a photo`

run:

```bash
/home/curie/curie "<raw addressed command>"
```

Examples:

```bash
/home/curie/curie "curie battery"
/home/curie/curie "hey curie go straight"
/home/curie/curie "curie take a photo"
```

## Behavior

- The CLI already maps natural language to the supported robot commands.
- The CLI normalizes wake phrases like `curie`, `hey curie`, `hi curie`, `hello curie`, `ok curie`, and `okay curie`.
- If the CLI returns an error or unsupported command, report that result briefly instead of guessing.

## Response style

- Reply with the command result in one short sentence when possible.
- If the command captured a photo, return the saved path the CLI printed.
