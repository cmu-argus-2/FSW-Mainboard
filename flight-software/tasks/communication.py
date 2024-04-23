"""
communication.py 
================
Comms FSW Task
"""

# Template task from taskio
from tasks.template_task import DebugTask

# State manager and OBDH
from state_manager import state_manager as SM
from apps.data_handler import DataHandler as DH

# PyCubed Board Lib
from hal.configuration import SATELLITE

# Argus-1 Radio Libs
from apps.comms.radio_helpers import *

class Task(DebugTask):

    name = "COMMS"
    ID = 0x12

    data_keys = [
        "time", 
    ]

    # Time for frequency checking 
    curr_time = time.monotonic_ns()
    SAT_RADIO = SATELLITE_RADIO(SATELLITE)
    tx_header = 0

    async def main_task(self):
        
        

        # Only transmit if SAT in NOMINAL state 
        if SM.current_state == "NOMINAL":
            # In NOMINAL state, we can transmit 

            # If process not registered, register it 
            if DH.data_process_exists("comms") == False:
                DH.register_data_process(
                    "comms", self.data_keys, "f", True, line_limit=50
                )

            # Read time, not sure if necessary 
            readings = {
                "time": time.time(),  # temporary fake time
            } 

            """
            Heartbeats transmitted every 20s based on task frequency 
            Once transmitted, run receive_message, waits for 1s 
            """

            self.tx_header = self.SAT_RADIO.transmit_message()
            
            # Debug message 
            print(f"[{self.ID}][{self.name}] Sent message with ID:", self.tx_header)

            # Receive message, blocking for 1s
            self.SAT_RADIO.receive_message()

            # Time for frequency checking 
            prev_time = self.curr_time
            self.curr_time = time.monotonic_ns()

            # # Debug messages for frequency check 
            # print(
            #     f"[{self.ID}][{self.name}] Frequency check: {self.curr_time - prev_time}"
            # )