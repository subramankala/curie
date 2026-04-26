# Curie

Curie is a local robot-control bundle for an Adeept AWR robot integrated with OpenClaw.

It includes:

- `scripts/curie`: the natural-language Curie CLI router
- `extensions/curie-command-router`: an OpenClaw pre-dispatch plugin that intercepts addressed Curie commands
- `skills/`: foundational and composed robot skills for movement, sensing, camera, lighting, and higher-level routines

## Main capabilities

- Addressed command routing like `hey curie go straight`
- Battery, ultrasonic distance, and line-sensor reads
- Safe forward motion with clearance checks
- Camera control and photo capture
- Line following and line reacquisition
- Distance keeping
- Higher-level routines like `scout ahead`, `inspect obstacle`, and `sentry`

## Example commands

- `curie battery`
- `curie distance`
- `curie line status`
- `curie follow line for 5 seconds`
- `curie find line`
- `curie keep distance for 5 seconds`
- `curie scout ahead 1 meter and take a photo`
- `curie inspect obstacle`
- `curie sentry for 2 minutes`

## Notes

- The current file paths are set up for the Raspberry Pi host at `/home/curie`.
- This repo captures the working Curie integration and OpenClaw skill/plugin code, not a full standalone installer.
