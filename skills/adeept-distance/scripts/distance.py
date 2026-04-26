#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

user_site = Path.home() / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
if user_site.exists():
    sys.path.insert(0, str(user_site))

from gpiozero import DistanceSensor


TRIGGER_PIN = 23
ECHO_PIN = 24
MAX_DISTANCE_METERS = 2.0


def read_distance_cm() -> float:
    sensor = DistanceSensor(
        echo=ECHO_PIN,
        trigger=TRIGGER_PIN,
        max_distance=MAX_DISTANCE_METERS,
    )
    try:
        return sensor.distance * 100.0
    finally:
        sensor.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read the Adeept ultrasonic distance sensor.")
    parser.add_argument(
        "--format",
        choices=["text", "json", "cm"],
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    distance_cm = read_distance_cm()

    if args.format == "cm":
        print(f"{distance_cm:.2f}")
        return 0
    if args.format == "json":
        print(json.dumps({"distance_cm": round(distance_cm, 2)}))
        return 0

    print(f"{distance_cm:.2f} cm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
