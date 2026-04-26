#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path

user_site = Path.home() / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
if user_site.exists():
    sys.path.insert(0, str(user_site))

from gpiozero import DistanceSensor
from board import SCL, SDA
import busio
from adafruit_motor import motor
from adafruit_pca9685 import PCA9685


PCA9685_ADDRESS = 0x5F
PWM_FREQUENCY = 50
TRIGGER_PIN = 23
ECHO_PIN = 24
MAX_DISTANCE_METERS = 2.0

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


def apply_motion(
    motors: tuple[motor.DCMotor, motor.DCMotor, motor.DCMotor, motor.DCMotor],
    direction: str,
    speed: int,
) -> None:
    motor1, motor2, motor3, motor4 = motors
    throttle = throttle_from_speed(speed)
    if direction == "forward":
        motor1.throttle = throttle * M1_DIRECTION
        motor2.throttle = throttle * M2_DIRECTION
        motor3.throttle = throttle * M3_DIRECTION
        motor4.throttle = throttle * M4_DIRECTION
        return
    if direction == "back":
        motor1.throttle = throttle * (-M1_DIRECTION)
        motor2.throttle = throttle * (-M2_DIRECTION)
        motor3.throttle = throttle * (-M3_DIRECTION)
        motor4.throttle = throttle * (-M4_DIRECTION)
        return
    set_all_zero(*motors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Keep a bounded distance using the Adeept ultrasonic sensor.")
    parser.add_argument("--target", type=float, default=30.0, help="Target distance in centimeters.")
    parser.add_argument("--tolerance", type=float, default=5.0, help="Allowed deviation in centimeters.")
    parser.add_argument("--speed", type=int, default=35, help="Motor speed from 0 to 100.")
    parser.add_argument("--duration", type=float, default=5.0, help="Maximum runtime in seconds.")
    parser.add_argument("--poll", type=float, default=0.12, help="Sensor poll interval in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = clamp(args.target, 5.0, 200.0)
    tolerance = clamp(args.tolerance, 1.0, 50.0)
    speed = int(clamp(args.speed, 0, 100))
    duration = clamp(args.duration, 0.2, 30.0)
    poll = clamp(args.poll, 0.05, 0.5)

    sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIGGER_PIN, max_distance=MAX_DISTANCE_METERS)
    i2c = busio.I2C(SCL, SDA)
    pwm = PCA9685(i2c, address=PCA9685_ADDRESS)

    last_action = "stop"
    last_distance = 0.0
    samples = 0

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
            last_distance = sensor.distance * 100.0
            samples += 1

            if last_distance > target + tolerance:
                last_action = "forward"
            elif last_distance < target - tolerance:
                last_action = "back"
            else:
                last_action = "stop"

            apply_motion(motors, last_action, speed)
            time.sleep(poll)

        set_all_zero(*motors)
    finally:
        sensor.close()
        pwm.deinit()

    print(
        f"Kept distance near {target:.1f} cm for {duration:.2f}s at speed {speed}. "
        f"Last distance: {last_distance:.1f} cm. Last action: {last_action}. Samples: {samples}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
