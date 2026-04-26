#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


ROBOT_PYTHON = "/usr/bin/python3"
DISTANCE_SCRIPT = Path("/home/curie/openclaw/skills/adeept-distance/scripts/distance.py")
KEEP_DISTANCE_SCRIPT = Path("/home/curie/openclaw/skills/adeept-distance/scripts/keep_distance.py")
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
    parser = argparse.ArgumentParser(description="Approach an obstacle to an inspection distance and take a photo.")
    parser.add_argument("--target", type=float, default=25.0, help="Target inspection distance in centimeters.")
    parser.add_argument("--tolerance", type=float, default=5.0, help="Allowed distance deviation in centimeters.")
    parser.add_argument("--speed", type=int, default=35, help="Keep-distance speed from 0 to 100.")
    parser.add_argument("--duration", type=float, default=6.0, help="Maximum approach time in seconds.")
    parser.add_argument("--view", choices=["up", "straight", "down"], default="straight", help="Photo view.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = clamp(args.target, 5.0, 200.0)
    tolerance = clamp(args.tolerance, 1.0, 50.0)
    speed = int(clamp(args.speed, 0, 100))
    duration = clamp(args.duration, 0.2, 30.0)

    before_distance = read_distance_cm()
    adjust_result = run_command(
        [
            ROBOT_PYTHON,
            str(KEEP_DISTANCE_SCRIPT),
            "--target",
            f"{target:.3f}",
            "--tolerance",
            f"{tolerance:.3f}",
            "--speed",
            str(speed),
            "--duration",
            f"{duration:.3f}",
        ]
    )
    if adjust_result.returncode != 0:
        raise RuntimeError(adjust_result.stderr.strip() or adjust_result.stdout.strip() or "Keep distance failed.")

    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    photo_result = run_command(["bash", str(PHOTO_SCRIPT), str(PHOTO_DIR), "inspect", args.view])
    if photo_result.returncode != 0:
        raise RuntimeError(photo_result.stderr.strip() or photo_result.stdout.strip() or "Photo capture failed.")

    after_distance = read_distance_cm()
    photo_path = photo_result.stdout.strip()
    print(
        f"Inspection complete. Distance before: {before_distance:.1f} cm. "
        f"Distance after: {after_distance:.1f} cm. "
        f"Photo saved: {photo_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
