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
from adafruit_motor import motor, servo
from adafruit_pca9685 import PCA9685


PCA9685_ADDRESS = 0x5F
PWM_FREQUENCY = 50

TILT_CHANNEL = 0
TILT_TOP = 75
TILT_STRAIGHT = 48
TILT_BOTTOM = 20

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


def map_speed(speed: int) -> float:
    return clamp(speed, 0, 100) / 100.0


def set_tilt(angle: int) -> None:
    i2c = busio.I2C(SCL, SDA)
    pwm = PCA9685(i2c, address=PCA9685_ADDRESS)
    try:
        pwm.frequency = PWM_FREQUENCY
        tilt_servo = servo.Servo(
            pwm.channels[TILT_CHANNEL],
            min_pulse=500,
            max_pulse=2400,
            actuation_range=180,
        )
        tilt_servo.angle = angle
        time.sleep(0.4)
    finally:
        pwm.deinit()


def build_motor(pwm: PCA9685, ch_a: int, ch_b: int) -> motor.DCMotor:
    dc_motor = motor.DCMotor(pwm.channels[ch_a], pwm.channels[ch_b])
    dc_motor.decay_mode = motor.SLOW_DECAY
    return dc_motor


def rotate(direction: str, speed: int, duration: float) -> None:
    i2c = busio.I2C(SCL, SDA)
    pwm = PCA9685(i2c, address=PCA9685_ADDRESS)
    try:
        pwm.frequency = PWM_FREQUENCY
        motor1 = build_motor(pwm, MOTOR_M1_IN1, MOTOR_M1_IN2)
        motor2 = build_motor(pwm, MOTOR_M2_IN1, MOTOR_M2_IN2)
        motor3 = build_motor(pwm, MOTOR_M3_IN1, MOTOR_M3_IN2)
        motor4 = build_motor(pwm, MOTOR_M4_IN1, MOTOR_M4_IN2)

        throttle = map_speed(speed)
        if direction == "left":
            motor1.throttle = throttle * M1_DIRECTION
            motor2.throttle = throttle * M2_DIRECTION
            motor3.throttle = throttle * (-M3_DIRECTION)
            motor4.throttle = throttle * (-M4_DIRECTION)
        else:
            motor1.throttle = throttle * (-M1_DIRECTION)
            motor2.throttle = throttle * (-M2_DIRECTION)
            motor3.throttle = throttle * M3_DIRECTION
            motor4.throttle = throttle * M4_DIRECTION

        time.sleep(clamp(duration, 0.05, 5.0))
        motor1.throttle = 0
        motor2.throttle = 0
        motor3.throttle = 0
        motor4.throttle = 0
    finally:
        pwm.deinit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Control the Adeept robot view direction on this Raspberry Pi."
    )
    parser.add_argument("direction", choices=["up", "down", "straight", "left", "right"])
    parser.add_argument("--speed", type=int, default=35, help="Wheel rotation speed for left/right.")
    parser.add_argument(
        "--duration",
        type=float,
        default=0.35,
        help="Wheel rotation duration in seconds for left/right.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.direction == "up":
        set_tilt(TILT_TOP)
        print("Camera tilted up.")
        return 0
    if args.direction == "down":
        set_tilt(TILT_BOTTOM)
        print("Camera tilted down.")
        return 0
    if args.direction == "straight":
        set_tilt(TILT_STRAIGHT)
        print("Camera centered to straight ahead.")
        return 0
    if args.direction == "left":
        rotate("left", args.speed, args.duration)
        print("Robot rotated left with the wheels; camera tilt stayed fixed.")
        return 0
    if args.direction == "right":
        rotate("right", args.speed, args.duration)
        print("Robot rotated right with the wheels; camera tilt stayed fixed.")
        return 0
    print(f"Unsupported direction: {args.direction}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
