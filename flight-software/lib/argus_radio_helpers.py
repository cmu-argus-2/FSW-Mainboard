"""
'argus_radio_helpers.py'
======================
Satellite radio class for Argus-1 CubeSat. 
Message packing/unpacking for telemetry/image TX
and acknowledgement RX. 

Authors: DJ Morvay, Akshat Sahay
"""

# Common CircuitPython Libs 
import os
import time
import sys

# PyCubed Board Lib
from pycubed import cubesat

# Argus-1 Lib
from argus_radio_protocol import *
from argus_radio_protocol import *

class SATELLITE_RADIO:
    '''
        Name: __init__
        Description: Initialization of SATELLITE class
    '''
    def __init__(self):
        self.image_strs = ['/sd/IMAGES/ohio.jpg','/sd/IMAGES/tokyo_small.jpg','/sd/IMAGES/oregon_small.jpg']
        self.image_num = 0

        self.image_get_info()
        self.send_mod = 10
        self.send_mod = 10
        self.heartbeat_sent = False
        self.image_deleted = True

        self.gs_req_ack = 0x0
        self.gs_rx_message_ID = 0x0
        self.gs_req_message_ID = 0x0
        self.gs_req_seq_count = 0
        self.sat_req_ack = 0x0
    
    '''
        Name: image_get_info
        Description: Read three images from flash, store in buffer
    '''
    def image_get_info(self):
        # Setup image class
        self.sat_images = IMAGES()
        # Setup initial image UIDs
        self.sat_images.image_UID = 0x5

        ## ---------- Image Sizes and Message Counts ---------- ## 
        # Get image #1 size and message count
        image_stat = os.stat(self.image_strs[self.image_num])
        self.sat_images.image_size = int(image_stat[6])
        self.sat_images.image_message_count = int(self.sat_images.image_size / 128)

        if ((self.sat_images.image_size % 128) > 0):
            self.sat_images.image_message_count += 1    

        print("Image size is", self.sat_images.image_size,"bytes")
        print("This image requires",self.sat_images.image_message_count,"messages")

        self.image_pack_images()

    '''
        Name: image_pack_info
        Description: Pack message ID, UID, size, and message count for all images in buffer.
    '''
    def image_pack_info(self):
        return (self.sat_images.image_UID.to_bytes(1,'big') + self.sat_images.image_size.to_bytes(4,'big') + self.sat_images.image_message_count.to_bytes(2,'big'))

    '''
        Name: image_pack_images
        Description: Pack one image into an array
        Inputs:
            IMG_CMD - image requested command
    '''
    def image_pack_images(self):
        # Initialize image arrays
        self.image_array = []
        
        # Image #Buffer Store
        bytes_remaining = self.sat_images.image_size
        send_bytes = open(self.image_strs[self.image_num],'rb')
        # Loop through image and store contents in an array
        while (bytes_remaining > 0):
            if (bytes_remaining >= 128):
                self.image_array.append(send_bytes.read(128))
            else:
                self.image_array.append(send_bytes.read(bytes_remaining))
                
            bytes_remaining -= 128
        # Close file when complete
        send_bytes.close()

    '''
        Name: unpack_message
        Description: Unpack message based on its ID
        Inputs:
            packet - Data received from RFM module
    '''
    def unpack_message(self,packet):
        # Can run deconstruct_message() for debug output 
        self.gs_req_ack = int.from_bytes(packet[0:1],'big') & 0b10000000
        self.rx_message_ID = int.from_bytes(packet[0:1],'big') & 0b01111111
        self.rx_message_sequence_count = int.from_bytes(packet[1:3],'big')
        self.rx_message_size = int.from_bytes(packet[3:4],'big')
        print("Message received header:",list(packet[0:4]))

        if (self.rx_message_ID == GS_ACK):
            self.gs_rx_message_ID = int.from_bytes(packet[4:5],'big')
            self.gs_req_message_ID = int.from_bytes(packet[5:6],'big')
            self.gs_req_seq_count = int.from_bytes(packet[6:8],'big')

            if (self.gs_req_message_ID == SAT_DEL_IMG1):
                if (self.image_num < 2):
                    self.image_num = self.image_num + 1
                else:
                    self.image_num = 0
                self.image_get_info()
        
    '''
        Name: received_message
        Description: This function waits for a message to be received from the LoRa module
    '''
    def receive_message(self):
        my_packet = cubesat.radio1.receive(timeout = 5)
        if my_packet is None:
            self.heartbeat_sent = False
            self.gs_req_message_ID = 0x00
        else:
            print(f'Received (raw bytes): {my_packet}')
            rssi = cubesat.radio1.rssi(raw=True)
            print(f'Received signal strength: {rssi} dBm')
            self.unpack_message(my_packet)

    '''
        Name: transmit_message
        Description: SAT transmits message via the LoRa module when the function is called.
    '''
    def transmit_message(self):
        send_multiple = True
        multiple_packet_count = -1
        target_sequence_count = 0

        while send_multiple:
            time.sleep(0.15)

            # This code is practically the same as Ground Station function hold_receive_mode
            if (self.gs_req_message_ID == SAT_IMG1_CMD):
                target_sequence_count = self.sat_images.image_message_count

                multiple_packet_count += 1
                # print(self.gs_req_message_ID)
                # print(((self.gs_req_seq_count + multiple_packet_count) % self.send_mod))
                # print(target_sequence_count)
                
                if (((((self.gs_req_seq_count + multiple_packet_count) % self.send_mod) > 0) and ((self.gs_req_seq_count + multiple_packet_count) < (target_sequence_count - 1))) or \
                    ((self.gs_req_seq_count + multiple_packet_count) == 0)):
                    send_multiple = True
                    self.sat_req_ack = 0x0
                else:
                    send_multiple = False
                    self.sat_req_ack = REQ_ACK_NUM
            else:
                send_multiple = False
                self.sat_req_ack = REQ_ACK_NUM

            if not self.heartbeat_sent:
                # Transmit SAT heartbeat
                # tx_header = [self.sat_req_ack | SAT_HEARTBEAT_BATT, 0x00, 0x01, 0x12]
                tx_message = construct_message(SAT_HEARTBEAT_BATT)
                self.heartbeat_sent = True
            elif self.gs_req_message_ID == SAT_IMAGES:
                # Transmit stored image info
                tx_header = bytes([(self.sat_req_ack | SAT_IMAGES),0x0,0x0,0x18])
                tx_payload = self.image_pack_info()
                tx_message = tx_header + tx_payload
            elif self.gs_req_message_ID == SAT_DEL_IMG1:
                # Transmit successful deletion of stored image 1
                tx_header = bytes([(self.sat_req_ack | SAT_DEL_IMG1),0x0,0x0,0x1])
                tx_payload = bytes([0x1])
                tx_message = tx_header + tx_payload
            elif (self.gs_req_message_ID == SAT_IMG1_CMD):
                # Transmit image in multiple packets
                # Header
                tx_header = ((self.sat_req_ack | self.gs_req_message_ID).to_bytes(1,'big') + (self.gs_req_seq_count + multiple_packet_count).to_bytes(2,'big') \
                            + len(self.image_array[self.gs_req_seq_count + multiple_packet_count]).to_bytes(1,'big'))
                # Payload
                tx_payload = self.image_array[self.gs_req_seq_count + multiple_packet_count]
                # Pack entire message
                tx_message = tx_header + tx_payload
            else:
                # Run construct_message() when telemetry information is complete
                tx_header = ((self.sat_req_ack | self.gs_req_message_ID).to_bytes(1,'big') + (0x0).to_bytes(1,'big') + (0x0).to_bytes(1,'big') + (0x0).to_bytes(1,'big'))
                tx_message = tx_header

            # Send a message to GS
            cubesat.radio1.send(tx_message)

            # Debug output of message in bytes
            print("Satellite sent message!")
            print("\n")