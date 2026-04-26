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


def apply_motion(
    motors: tuple[motor.DCMotor, motor.DCMotor, motor.DCMotor, motor.DCMotor],
    direction: str,
    speed: int,
) -> None:
    motor1, motor2, motor3, motor4 = motors
    throttle = throttle_from_speed(speed)
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


def line_detected(left: InputDevice, middle: InputDevice, right: InputDevice) -> tuple[bool, tuple[int, int, int]]:
    status = (int(left.value), int(middle.value), int(right.value))
    return any(value == 0 for value in status), status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rotate until the Adeept line sensors reacquire a line.")
    parser.add_argument("--speed", type=int, default=30, help="Motor speed from 0 to 100.")
    parser.add_argument("--duration", type=float, default=6.0, help="Maximum scan time in seconds.")
    parser.add_argument("--sweep", type=float, default=0.45, help="Seconds per sweep segment.")
    parser.add_argument("--poll", type=float, default=0.05, help="Sensor poll interval in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    speed = int(clamp(args.speed, 0, 100))
    duration = clamp(args.duration, 0.2, 30.0)
    sweep = clamp(args.sweep, 0.1, 2.0)
    poll = clamp(args.poll, 0.03, 0.5)

    left = InputDevice(pin=LINE_PIN_LEFT)
    middle = InputDevice(pin=LINE_PIN_MIDDLE)
    right = InputDevice(pin=LINE_PIN_RIGHT)
    i2c = busio.I2C(SCL, SDA)
    pwm = PCA9685(i2c, address=PCA9685_ADDRESS)

    found = False
    last_status = (1, 1, 1)
    sweeps = 0

    try:
        pwm.frequency = PWM_FREQUENCY
        motors = (
            build_motor(pwm, MOTOR_M1_IN1, MOTOR_M1_IN2),
            build_motor(pwm, MOTOR_M2_IN1, MOTOR_M2_IN2),
            build_motor(pwm, MOTOR_M3_IN1, MOTOR_M3_IN2),
            build_motor(pwm, MOTOR_M4_IN1, MOTOR_M4_IN2),
        )
        deadline = time.monotonic() + duration
        direction = "rotate-left"

        while time.monotonic() < deadline:
            sweep_deadline = min(deadline, time.monotonic() + sweep)
            apply_motion(motors, direction, speed)
            sweeps += 1
            while time.monotonic() < sweep_deadline:
                found, last_status = line_detected(left, middle, right)
                if found:
                    set_all_zero(*motors)
                    break
                time.sleep(poll)
            if found:
                break
            direction = "rotate-right" if direction == "rotate-left" else "rotate-left"

        set_all_zero(*motors)
    finally:
        left.close()
        middle.close()
        right.close()
        pwm.deinit()

    print(
        f"Find line result: {'found' if found else 'not found'} "
        f"after {sweeps} sweeps. "
        f"Last sensors: left={last_status[0]} middle={last_status[1]} right={last_status[2]}."
    )
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
