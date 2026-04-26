#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path

from gpiozero import InputDevice

user_site = Path.home() / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
if user_site.exists():
    sys.path.insert(0, str(user_site))

from board import SCL, SDA
import busio
from adafruit_motor import motor
from adafruit_pca9685 import PCA9685


PCA9685_ADDRESS = 0x5F
PWM_FREQUENCY = 50

MOTOR_M1_IN1 = 15
MOTOR_M1_IN2 = 14
MOTOR_M2_IN1 = 12
MOTOR_M2_IN2 = 13
MOTOR_M3_IN1 = 11
MOTOR_M3_IN2 = 10
MOTOR_M4_IN1 = 8
MOTOR_M4_IN2 = 9

M1_DIRECTION = 1
M2_DIRECTION = -1
M3_DIRECTION = 1
M4_DIRECTION = -1

LINE_PIN_LEFT = 22
LINE_PIN_MIDDLE = 27
LINE_PIN_RIGHT = 17

DEFAULT_POLL_SECONDS = 0.08


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def throttle_from_speed(speed: int) -> float:
    return clamp(speed, 0, 100) / 100.0


def build_motor(pwm: PCA9685, ch_a: int, ch_b: int) -> motor.DCMotor:
    dc_motor = motor.DCMotor(pwm.channels[ch_a], pwm.channels[ch_b])
    dc_motor.decay_mode = motor.SLOW_DECAY
    return dc_motor


def set_all_zero(*motors: motor.DCMotor) -> None:
    for dc_motor in motors:
        dc_motor.throttle = 0


def apply_motion(motors: tuple[motor.DCMotor, motor.DCMotor, motor.DCMotor, motor.DCMotor], direction: str, speed: int) -> None:
    motor1, motor2, motor3, motor4 = motors
    throttle = throttle_from_speed(speed)

    if direction == "forward":
        motor1.throttle = throttle * M1_DIRECTION
        motor2.throttle = throttle * M2_DIRECTION
        motor3.throttle = throttle * M3_DIRECTION
        motor4.throttle = throttle * M4_DIRECTION
        return
    if direction == "rotate-left":
        motor1.throttle = throttle * M1_DIRECTION
        motor2.throttle = throttle * M2_DIRECTION
        motor3.throttle = throttle * (-M3_DIRECTION)
        motor4.throttle = throttle * (-M4_DIRECTION)
        return
    if direction == "rotate-right":
        motor1.throttle = throttle * (-M1_DIRECTION)
        motor2.throttle = throttle * (-M2_DIRECTION)
        motor3.throttle = throttle * M3_DIRECTION
        motor4.throttle = throttle * M4_DIRECTION
        return
    set_all_zero(*motors)


def choose_direction(left_value: int, middle_value: int, right_value: int) -> str:
    if middle_value == 0:
        if left_value == 0 and right_value == 1:
            return "rotate-right"
        if left_value == 1 and right_value == 0:
            return "rotate-left"
        return "forward"

    if left_value == 0 and right_value == 1:
        return "rotate-right"
    if left_value == 1 and right_value == 0:
        return "rotate-left"
    if left_value == 0 and right_value == 0:
        return "forward"
    return "stop"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Follow a line with the Adeept line tracking sensors.")
    parser.add_argument("--speed", type=int, default=35, help="Motor speed from 0 to 100.")
    parser.add_argument("--duration", type=float, default=5.0, help="Follow duration in seconds.")
    parser.add_argument("--poll", type=float, default=DEFAULT_POLL_SECONDS, help="Polling interval in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    speed = int(clamp(args.speed, 0, 100))
    duration = clamp(args.duration, 0.2, 30.0)
    poll = clamp(args.poll, 0.03, 0.5)

    left = InputDevice(pin=LINE_PIN_LEFT)
    middle = InputDevice(pin=LINE_PIN_MIDDLE)
    right = InputDevice(pin=LINE_PIN_RIGHT)
    i2c = busio.I2C(SCL, SDA)
    pwm = PCA9685(i2c, address=PCA9685_ADDRESS)

    last_direction = "stop"
    iterations = 0
    saw_line = False

    try:
        pwm.frequency = PWM_FREQUENCY
        motors = (
            build_motor(pwm, MOTOR_M1_IN1, MOTOR_M1_IN2),
            build_motor(pwm, MOTOR_M2_IN1, MOTOR_M2_IN2),
            build_motor(pwm, MOTOR_M3_IN1, MOTOR_M3_IN2),
            build_motor(pwm, MOTOR_M4_IN1, MOTOR_M4_IN2),
        )
        deadline = time.monotonic() + duration

        while time.monotonic() < deadline:
            left_value = int(left.value)
            middle_value = int(middle.value)
            right_value = int(right.value)
            saw_line = saw_line or any(value == 0 for value in (left_value, middle_value, right_value))
            direction = choose_direction(left_value, middle_value, right_value)
            apply_motion(motors, direction, speed)
            last_direction = direction
            iterations += 1
            time.sleep(poll)

        set_all_zero(*motors)
    finally:
        left.close()
        middle.close()
        right.close()
        pwm.deinit()

    print(
        f"Followed line for {duration:.2f}s at speed {speed}. "
        f"Last action: {last_direction}. "
        f"Line seen: {'yes' if saw_line else 'no'}. "
        f"Samples: {iterations}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
