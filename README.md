# Curie

Curie is a local robot-control bundle for an Adeept AWR robot integrated with OpenClaw.

It includes:

- `scripts/curie`: the natural-language Curie CLI router
- `extensions/curie-command-router`: an OpenClaw pre-dispatch plugin that intercepts addressed Curie commands
- `skills/`: foundational and composed robot skills for movement, sensing, camera, lighting, and higher-level routines

## Repo layout

- `scripts/`: entrypoints, including the main `curie` CLI
- `extensions/`: OpenClaw plugin/router code
- `skills/`: robot skill manifests and hardware scripts

## Runtime assumptions

- The checked-in `scripts/curie` launcher resolves skill scripts relative to this repo.
- Runtime state still lives outside the repo:
  - config: `~/.config/curie/config.json`
  - light worker pid: `~/.cache/curie/light.pid`
  - captured photos: `~/curie-photos`
- The OpenClaw router plugin defaults to `/home/curie/curie-repo/scripts/curie`.
  Override it with `CURIE_COMMAND_PATH` if you install the repo elsewhere.

## Installation

1. Clone the repo onto the Raspberry Pi host.
2. Make sure the Adeept hardware dependencies are installed.
3. Symlink or copy `scripts/curie` onto your preferred executable path.
4. Install or mirror `extensions/curie-command-router` into your OpenClaw extensions directory.
5. Install or mirror `skills/` entries into your OpenClaw skills directory as needed.

Example:

```bash
ln -sf /home/curie/curie-repo/scripts/curie /home/curie/curie
```

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

- This repo captures the working Curie integration and OpenClaw skill/plugin code.
- The skills still target the Adeept Raspberry Pi hardware stack and assume local GPIO/I2C/SPI access.
