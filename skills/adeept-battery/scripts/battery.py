#!/usr/bin/env python3
import sys
from pathlib import Path

user_site = Path.home() / f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
if user_site.exists():
    sys.path.insert(0, str(user_site))

import statistics
import time

import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice


ADC_ADDRESS = 0x48
ADC_CMD = 0x84
ADC_CHANNEL = 0
ADC_VREF = 5.0
FULL_VOLTAGE = 8.4
WARNING_VOLTAGE = 6.75
R15 = 3000
R17 = 1000
DIVISION_RATIO = R17 / (R15 + R17)


def read_samples(count: int = 10) -> list[float]:
    i2c = busio.I2C(board.SCL, board.SDA)
    device = I2CDevice(i2c, ADC_ADDRESS)
    control_byte = ADC_CMD | (((ADC_CHANNEL << 2 | ADC_CHANNEL >> 1) & 0x07) << 4)
    buf = bytearray(1)
    samples: list[float] = []
    for _ in range(count):
        device.write_then_readinto(bytes([control_byte]), buf)
        adc_value = buf[0]
        a0_voltage = (adc_value / 255.0) * ADC_VREF
        battery_voltage = a0_voltage / DIVISION_RATIO
        samples.append(battery_voltage)
        time.sleep(0.05)
    return samples


def main() -> int:
    samples = read_samples()
    median = statistics.median(samples)
    filtered = [value for value in samples if abs(value - median) < 1]
    average_voltage = sum(filtered) / len(filtered) if filtered else sum(samples) / len(samples)
    percentage = (average_voltage - WARNING_VOLTAGE) / (FULL_VOLTAGE - WARNING_VOLTAGE) * 100
    percentage = max(0.0, min(100.0, percentage))
    status = "LOW" if average_voltage < WARNING_VOLTAGE else "OK"
    print(f"battery_percent={percentage:.1f}")
    print(f"battery_voltage={average_voltage:.2f}")
    print(f"battery_status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
