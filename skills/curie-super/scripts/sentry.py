#!/usr/bin/env python3
import argparse
import subprocess
import time
from pathlib import Path


ROBOT_PYTHON = "/usr/bin/python3"
DISTANCE_SCRIPT = Path("/home/curie/openclaw/skills/adeept-distance/scripts/distance.py")
LIGHT_SCRIPT = Path("/home/curie/openclaw/skills/adeept-light/scripts/light.py")
PHOTO_SCRIPT = Path("/home/curie/openclaw/skills/pi-camera-whatsapp/scripts/take-photo.sh")
PHOTO_DIR = Path("/home/curie/curie-photos")


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def run_command(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True, check=False)


def read_distance_cm() -> float:
    result = run_command([ROBOT_PYTHON, str(DISTANCE_SCRIPT), "--format", "cm"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Distance read failed.")
    return float(result.stdout.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch distance and alert with lights and a photo when something approaches.")
    parser.add_argument("--threshold", type=float, default=35.0, help="Trigger threshold in centimeters.")
    parser.add_argument("--duration", type=float, default=15.0, help="Maximum watch time in seconds.")
    parser.add_argument("--poll", type=float, default=0.5, help="Polling interval in seconds.")
    parser.add_argument("--cooldown", type=float, default=5.0, help="Minimum seconds between triggers.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    threshold = clamp(args.threshold, 5.0, 200.0)
    duration = clamp(args.duration, 0.5, 300.0)
    poll = clamp(args.poll, 0.1, 5.0)
    cooldown = clamp(args.cooldown, 0.0, 60.0)

    deadline = time.monotonic() + duration
    last_trigger_at = 0.0
    samples = 0
    triggers = 0
    last_distance = 0.0
    photo_paths: list[str] = []

    while time.monotonic() < deadline:
        last_distance = read_distance_cm()
        samples += 1
        now = time.monotonic()
        if last_distance <= threshold and now - last_trigger_at >= cooldown:
            last_trigger_at = now
            triggers += 1
            run_command([ROBOT_PYTHON, str(LIGHT_SCRIPT), "on"])
            PHOTO_DIR.mkdir(parents=True, exist_ok=True)
            photo_result = run_command(["bash", str(PHOTO_SCRIPT), str(PHOTO_DIR), "sentry", "straight"])
            if photo_result.returncode == 0:
                photo_paths.append(photo_result.stdout.strip())
            run_command([ROBOT_PYTHON, str(LIGHT_SCRIPT), "off"])
        time.sleep(poll)

    summary = (
        f"Sentry finished after {duration:.1f}s with {samples} samples and {triggers} triggers. "
        f"Last distance: {last_distance:.1f} cm."
    )
    if photo_paths:
        summary += f" Latest photo: {photo_paths[-1]}"
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
