#!/usr/bin/env python3
import argparse
import json
from gpiozero import InputDevice


LINE_PIN_LEFT = 22
LINE_PIN_MIDDLE = 27
LINE_PIN_RIGHT = 17


def read_status() -> dict[str, int | str]:
    left = InputDevice(pin=LINE_PIN_LEFT)
    middle = InputDevice(pin=LINE_PIN_MIDDLE)
    right = InputDevice(pin=LINE_PIN_RIGHT)
    try:
        left_value = int(left.value)
        middle_value = int(middle.value)
        right_value = int(right.value)
    finally:
        left.close()
        middle.close()
        right.close()

    active = [
        name
        for name, value in (
            ("left", left_value),
            ("middle", middle_value),
            ("right", right_value),
        )
        if value == 0
    ]
    return {
        "left": left_value,
        "middle": middle_value,
        "right": right_value,
        "line_detected": "yes" if active else "no",
        "active": ",".join(active) if active else "none",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read the Adeept line tracking sensors.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = read_status()
    if args.format == "json":
        print(json.dumps(status))
        return 0

    print(
        f"Line sensors: left={status['left']} middle={status['middle']} right={status['right']} "
        f"(line_detected={status['line_detected']}, active={status['active']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
