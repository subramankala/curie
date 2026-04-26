---
name: adeept-battery
description: Read the current battery voltage and percentage for the local Adeept robot on this Raspberry Pi host. Use when the user asks for battery, battery status, battery level, charge level, or power status. Do not use connected nodes for this skill.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔋",
        "os": ["linux"],
        "requires": { "bins": ["python3"] },
      },
  }
---

# adeept-battery

Use this skill to read the battery level from the local Adeept robot.

Routing rules:

- Always run locally on the Raspberry Pi host.
- Never use connected nodes.
- Read the robot battery ADC directly.

## Command

Run:

```bash
python3 /home/curie/openclaw/skills/adeept-battery/scripts/battery.py
```

## Response style

Reply briefly with:

- battery percentage
- measured voltage
- a short warning if the battery is low

Example:

- `Battery is 18% at 6.9V. Low battery; recharge soon.`
