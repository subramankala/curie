#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


ROBOT_PYTHON = "/usr/bin/python3"
DISTANCE_SCRIPT = Path("/home/curie/openclaw/skills/adeept-distance/scripts/distance.py")
DRIVE_SCRIPT = Path("/home/curie/openclaw/skills/adeept-drive/scripts/drive.py")
PHOTO_SCRIPT = Path("/home/curie/openclaw/skills/pi-camera-whatsapp/scripts/take-photo.sh")
PHOTO_DIR = Path("/home/curie/curie-photos")

CM_PER_SECOND_AT_100_SPEED = 25.0


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def run_command(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True, check=False)


def read_distance_cm() -> float:
    result = run_command([ROBOT_PYTHON, str(DISTANCE_SCRIPT), "--format", "cm"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Distance read failed.")
    return float(result.stdout.strip())


def seconds_for_distance(distance_cm: float, speed: int) -> float:
    effective_speed = max(speed, 1) / 100.0
    return distance_cm / (CM_PER_SECOND_AT_100_SPEED * effective_speed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scout ahead in bounded hops and optionally take a photo.")
    parser.add_argument("--distance", type=float, default=100.0, help="Maximum scout distance in centimeters.")
    parser.add_argument("--hop", type=float, default=20.0, help="Per-hop distance in centimeters.")
    parser.add_argument("--speed", type=int, default=35, help="Drive speed from 0 to 100.")
    parser.add_argument("--clearance", type=float, default=25.0, help="Minimum required clearance in centimeters.")
    parser.add_argument("--photo", action="store_true", help="Capture a photo at the end of the scout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    total_distance = clamp(args.distance, 5.0, 300.0)
    hop_distance = clamp(args.hop, 5.0, 100.0)
    speed = int(clamp(args.speed, 0, 100))
    clearance = clamp(args.clearance, 5.0, 200.0)

    moved_cm = 0.0
    hops = 0
    last_distance = 0.0
    blocked = False
    photo_path = ""

    while moved_cm < total_distance:
        last_distance = read_distance_cm()
        if last_distance < clearance:
            blocked = True
            break

        this_hop = min(hop_distance, total_distance - moved_cm)
        duration = clamp(seconds_for_distance(this_hop, speed), 0.05, 5.0)
        result = run_command(
            [
                ROBOT_PYTHON,
                str(DRIVE_SCRIPT),
                "forward",
                "--speed",
                str(speed),
                "--duration",
                f"{duration:.3f}",
            ]
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Scout move failed.")
        moved_cm += this_hop
        hops += 1

    if args.photo:
        PHOTO_DIR.mkdir(parents=True, exist_ok=True)
        result = run_command(["bash", str(PHOTO_SCRIPT), str(PHOTO_DIR), "scout", "straight"])
        if result.returncode == 0:
            photo_path = result.stdout.strip()

    final_distance = read_distance_cm()
    summary = (
        f"Scout ahead finished after {hops} hops and about {moved_cm:.1f} cm traveled. "
        f"Final distance ahead: {final_distance:.1f} cm."
    )
    if blocked:
        summary += f" Stopped because clearance dropped below {clearance:.1f} cm."
    else:
        summary += " Reached the requested scout distance."
    if photo_path:
        summary += f" Photo saved: {photo_path}"
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
