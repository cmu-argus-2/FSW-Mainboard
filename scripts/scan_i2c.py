# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# pylint: disable=broad-except, eval-used, unused-import

"""CircuitPython I2C Device Address Scan"""
import time

import board
import busio


class i2c_device:
    def __init__(self, name, scl, sda):
        self.name = name
        self.i2c = busio.I2C(scl, sda)


# List of potential I2C busses
I2C0 = i2c_device("I2C0", board.SCL0, board.SDA0)
I2C1 = i2c_device("I2C1", board.SCL1, board.SDA1)
ALL_I2C = [I2C0, I2C1]

# Determine which busses are valid
found_i2c = []
for bus in ALL_I2C:
    try:
        print("Checking {}...".format(bus.name), end="")
        bus.i2c.unlock()
        found_i2c.append((bus.name, bus.i2c))
        print("ADDED.")
    except Exception as e:
        print("SKIPPED:", e)

# Scan valid busses
if len(found_i2c):
    print("-" * 40)
    print("I2C SCAN")
    print("-" * 40)
    while True:
        for bus_info in found_i2c:
            name = bus_info[0]
            bus = bus_info[1]

            while not bus.try_lock():
                pass

            print(
                name,
                "addresses found:",
                [hex(device_address) for device_address in bus.scan()],
            )

            bus.unlock()

        time.sleep(2)
else:
    print("No valid I2C bus found.")
