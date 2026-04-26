#!/usr/bin/env python3
import argparse
import signal
import sys
import time
from pathlib import Path

SERVER_DIR = Path("/home/curie/code/Adeept_AWR-V3-20260403/Code/Adeept_AWR-V3/Server")
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from RobotLight import Adeept_SPI_LedPixel


LED_COUNT = 16
LED_BRIGHTNESS = 255
WHITE = (255, 255, 255)
AMBER = (255, 140, 0)
OFF = (0, 0, 0)

RUNNING = True


def handle_signal(signum, frame) -> None:
    del signum, frame
    global RUNNING
    RUNNING = False


def build_led() -> Adeept_SPI_LedPixel:
    led = Adeept_SPI_LedPixel(LED_COUNT, LED_BRIGHTNESS)
    if led.check_spi_state() == 0:
        raise RuntimeError("LED SPI interface is unavailable.")
    return led


def set_color(led: Adeept_SPI_LedPixel, color: tuple[int, int, int]) -> None:
    led.set_all_led_color(*color)


def blink_loop(led: Adeept_SPI_LedPixel, interval: float, color: tuple[int, int, int]) -> None:
    while RUNNING:
        set_color(led, color)
        time.sleep(interval)
        if not RUNNING:
            break
        set_color(led, OFF)
        time.sleep(interval)
    set_color(led, OFF)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Control the Adeept robot LEDs.")
    parser.add_argument("mode", choices=["on", "off", "blink-fast", "blink-slow"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    led = build_led()
    try:
        if args.mode == "on":
            set_color(led, WHITE)
            print("Lights turned on.")
            return 0
        if args.mode == "off":
            set_color(led, OFF)
            print("Lights turned off.")
            return 0
        if args.mode == "blink-fast":
            blink_loop(led, 0.2, AMBER)
            return 0
        blink_loop(led, 0.5, AMBER)
        return 0
    finally:
        led.led_close()


if __name__ == "__main__":
    raise SystemExit(main())
