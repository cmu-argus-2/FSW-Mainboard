"""
Satellite State Management

======================

This module defines the operational states for the satellite, represented as constants, along with the corresponding
string representations. Each state indicates a distinct operational mode, with entry and exit criteria.

States:
    STARTUP: Initial state where hardware diagnostics are conducted, and state recovery is performed.
    NOMINAL: Regular operation state following successful diagnostics, or recovery from other states.
    DOWNLINK: Communication state entered upon receiving a ground station signal; telemetry, files, and payload data
                are downlinked according to the ground station requests.
    LOW_POWER: Power-conservation state triggered when battery levels fall below a threshold; resumes nominal upon
                recharge above a recovery threshold.
    SAFE: Emergency state triggered by critical hardware or software failures, allowing for fault handling and
            eventual ground intervention.


Author: Ibrahima S. Sow
"""

from micropython import const


class TASK:
    COMMAND = const(0x00)
    WATCHDOG = const(0x01)
    EPS = const(0x02)
    OBDH = const(0x03)
    COMMS = const(0x04)
    IMU = const(0x05)
    ADCS = const(0x06)
    THERMAL = const(0x07)
    GPS = const(0x08)
    PAYLOAD = const(0x09)


class STATES:
    STARTUP = const(0x00)
    NOMINAL = const(0x01)
    DOWNLINK = const(0x02)
    LOW_POWER = const(0x03)
    SAFE = const(0x04)

    TRANSITIONS = {
        STARTUP: [NOMINAL, SAFE],
        NOMINAL: [DOWNLINK, LOW_POWER, SAFE],
        DOWNLINK: [NOMINAL, LOW_POWER, SAFE],
        LOW_POWER: [NOMINAL, SAFE],
        SAFE: [NOMINAL],
    }


STR_STATES = ["STARTUP", "NOMINAL", "DOWNLINK", "LOW_POWER", "SAFE"]
