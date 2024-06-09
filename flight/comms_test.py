from apps.comms.radio_helpers import *

# Argus-1 Radio Libs
from apps.comms.radio_protocol import *
from hal.configuration import SATELLITE

SAT_RADIO = SATELLITE_RADIO(SATELLITE)
SAT_RADIO.heartbeat_seq = [SAT_HEARTBEAT_BATT]
SAT_RADIO.heartbeat_max = len(SAT_RADIO.heartbeat_seq)

## ---------- MAIN CODE STARTS HERE! ---------- ##

while True:
    if SATELLITE.RADIO is not None:
        SAT_RADIO.transmit_message()

    if SATELLITE.RADIO is not None:
        SAT_RADIO.receive_message()
