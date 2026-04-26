#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path

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


def apply_action(action: str, speed: int, duration: float) -> None:
    i2c = busio.I2C(SCL, SDA)
    pwm = PCA9685(i2c, address=PCA9685_ADDRESS)
    try:
        pwm.frequency = PWM_FREQUENCY
        motor1 = build_motor(pwm, MOTOR_M1_IN1, MOTOR_M1_IN2)
        motor2 = build_motor(pwm, MOTOR_M2_IN1, MOTOR_M2_IN2)
        motor3 = build_motor(pwm, MOTOR_M3_IN1, MOTOR_M3_IN2)
        motor4 = build_motor(pwm, MOTOR_M4_IN1, MOTOR_M4_IN2)
        throttle = throttle_from_speed(speed)

        if action == "forward":
            motor1.throttle = throttle * M1_DIRECTION
            motor2.throttle = throttle * M2_DIRECTION
            motor3.throttle = throttle * M3_DIRECTION
            motor4.throttle = throttle * M4_DIRECTION
        elif action == "back":
            motor1.throttle = throttle * (-M1_DIRECTION)
            motor2.throttle = throttle * (-M2_DIRECTION)
            motor3.throttle = throttle * (-M3_DIRECTION)
            motor4.throttle = throttle * (-M4_DIRECTION)
        elif action == "turn-left":
            motor1.throttle = throttle * M1_DIRECTION
            motor2.throttle = throttle * M2_DIRECTION
            motor3.throttle = throttle * (-M3_DIRECTION)
            motor4.throttle = throttle * (-M4_DIRECTION)
        elif action == "turn-right":
            motor1.throttle = throttle * (-M1_DIRECTION)
            motor2.throttle = throttle * (-M2_DIRECTION)
            motor3.throttle = throttle * M3_DIRECTION
            motor4.throttle = throttle * M4_DIRECTION
        else:
            raise ValueError(f"Unsupported action: {action}")

        time.sleep(clamp(duration, 0.05, 30.0))
        set_all_zero(motor1, motor2, motor3, motor4)
    finally:
        pwm.deinit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drive the Adeept robot chassis for a fixed duration.")
    parser.add_argument("action", choices=["forward", "back", "turn-left", "turn-right"])
    parser.add_argument("--speed", type=int, default=40, help="Motor speed from 0 to 100.")
    parser.add_argument("--duration", type=float, default=1.0, help="Drive time in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    apply_action(args.action, args.speed, args.duration)
    print(f"Moved {args.action} for {clamp(args.duration, 0.05, 30.0):.2f}s at speed {clamp(args.speed, 0, 100):.0f}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
