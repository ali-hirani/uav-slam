#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import numpy as np
import serial
from rpisensors.eeprom16 import Eeprom16
import atexit

# pylint: disable=C0103


# Default address
VL6180X_I2CADDRESS = 0x29

VL_IDENTIFICATION_MODEL_ID = 0x000
VL_SYSTEM_INTERRUPT_CONFIG_GPIO = 0x014
VL_SYSTEM_INTERRUPT_CLEAR = 0x015
VL_SYSTEM_FRESH_OUT_OF_RESET = 0x016
VL_SYSTEM_MODE_GPIO1 = 0x011
VL_SYSRANGE_START = 0x018
VL_SYSRANGE_INTERMEASUREMENT_PERIOD = 0x01B
VL_SYSRANGE_VHV_RECALIBRATE = 0x02E
VL_SYSRANGE_VHV_REPEAT_RATE = 0x031
VL_SYSALS_START = 0x038
VL_SYSALS_INTERMEASUREMENT_PERIOD = 0x03E
VL_SYSALS_ANALOGUE_GAIN = 0x03F
VL_SYSALS_INTEGRATION_PERIOD = 0x040
VL_RESULT_INTERRUPT_STATUS_GPIO = 0x04F
VL_RESULT_ALS_VAL = 0x050
VL_RESULT_RANGE_VAL = 0x062
VL_READOUT_AVERAGING_SAMPLE_PERIOD = 0x10A

VL_IDENTIFICATION_MODEL_ID_VALUE = 0xB4

VL_ALS_GAIN_1 = 0x06
VL_ALS_GAIN_1_25 = 0x05
VL_ALS_GAIN_1_67 = 0x04
VL_ALS_GAIN_2_5 = 0x03
VL_ALS_GAIN_5 = 0x02
VL_ALS_GAIN_10 = 0x01
VL_ALS_GAIN_20 = 0x00
VL_ALS_GAIN_40 = 0x07


class VL6180X(Eeprom16):

    def __init__(self, bus_id, address=VL6180X_I2CADDRESS, **kwargs):
        super(VL6180X, self).__init__(bus_id, address, **kwargs)

        self.verify()
        self.prepare()

    def verify(self):
        chip_id = self.read_byte(VL_IDENTIFICATION_MODEL_ID)

        is_vl6180x = chip_id == VL_IDENTIFICATION_MODEL_ID_VALUE

        if is_vl6180x:
            self.logger.debug("VL6180X sensor found: chip id is 0xB4 ")
        else:
            self.logger.warning(
                'No VL6180X sensor found: chip id is 0x%02X, '
                'should be 0x%02X', chip_id, VL_IDENTIFICATION_MODEL_ID_VALUE)

    def prepare(self, force=False):
        status = self.read_byte(VL_SYSTEM_FRESH_OUT_OF_RESET)

        if status == 1:
            self.logger.debug("System is fresh out of reset")

        if status == 1 or force is True:
            self.logger.debug("Setting sensor parameters, force = %s", force)

            self.write_byte(0x0207, 0x01)
            self.write_byte(0x0208, 0x01)
            self.write_byte(0x0096, 0x00)
            self.write_byte(0x0097, 0xfd)
            self.write_byte(0x00e3, 0x00)
            self.write_byte(0x00e4, 0x04)
            self.write_byte(0x00e5, 0x02)
            self.write_byte(0x00e6, 0x01)
            self.write_byte(0x00e7, 0x03)
            self.write_byte(0x00f5, 0x02)
            self.write_byte(0x00d9, 0x05)
            self.write_byte(0x00db, 0xce)
            self.write_byte(0x00dc, 0x03)
            self.write_byte(0x00dd, 0xf8)
            self.write_byte(0x009f, 0x00)
            self.write_byte(0x00a3, 0x3c)
            self.write_byte(0x00b7, 0x00)
            self.write_byte(0x00bb, 0x3c)
            self.write_byte(0x00b2, 0x09)
            self.write_byte(0x00ca, 0x09)
            self.write_byte(0x0198, 0x01)
            self.write_byte(0x01b0, 0x17)
            self.write_byte(0x01ad, 0x00)
            self.write_byte(0x00ff, 0x05)
            self.write_byte(0x0100, 0x05)
            self.write_byte(0x0199, 0x05)
            self.write_byte(0x01a6, 0x1b)
            self.write_byte(0x01ac, 0x3e)
            self.write_byte(0x01a7, 0x1f)
            self.write_byte(0x0030, 0x00)

            # Enables polling for ‘New Sample ready’ when measurement completes
            self.write_byte(VL_SYSTEM_MODE_GPIO1, 0x10)

            # Set the averaging sample period (compromise between lower noise
            # and increased execution time)
            self.write_byte(VL_READOUT_AVERAGING_SAMPLE_PERIOD, 0x30)

            # Set the light and dark gain (upper nibble).
            # Dark gain should not be changed.
            self.write_byte(VL_SYSALS_ANALOGUE_GAIN, 0x40 | VL_ALS_GAIN_1)

            # Set the number of range measurements after which auto calibration
            # of system is performed
            self.write_byte(VL_SYSRANGE_VHV_REPEAT_RATE, 0xFF)

            # Set ALS integration time to 100ms
            self.write_byte(VL_SYSALS_INTEGRATION_PERIOD, 0x63)

            # Perform a single temperature calibratio of the ranging sensor
            self.write_byte(VL_SYSRANGE_VHV_RECALIBRATE, 0x01)

            # Set default ranging inter-measurement period to 100ms
            self.write_byte(VL_SYSRANGE_INTERMEASUREMENT_PERIOD, 0x09)

            # Set default ALS inter-measurement period to 500ms
            self.write_byte(VL_SYSALS_INTERMEASUREMENT_PERIOD, 0x31)

            # Configure interrupt on ‘New Sample Ready threshold event’
            self.write_byte(VL_SYSTEM_INTERRUPT_CONFIG_GPIO, 0x24)

            self.write_byte(VL_SYSTEM_FRESH_OUT_OF_RESET, 0x00)

    def read_distance(self):
        self.write_byte(VL_SYSRANGE_START, 0x01)

        value = None
        i = 0
        while i < 10:
            i += 1

            status = self.read_byte(VL_RESULT_INTERRUPT_STATUS_GPIO)
            range_status = status & 0x07
            if range_status == 0x04:
                value = self.read_byte(VL_RESULT_RANGE_VAL)
                break

            time.sleep(0.1)

        self.write_byte(VL_SYSTEM_INTERRUPT_CLEAR, 0x07)

        #self.logger.debug("Distance is %d mm", value)
        return value

    def read_lux(self, gain=VL_ALS_GAIN_1):
        reg = self.read_byte(VL_SYSTEM_INTERRUPT_CONFIG_GPIO)
        reg = reg & (~0x38)
        reg = reg | (0x4 << 3)
        self.write_byte(VL_SYSTEM_INTERRUPT_CONFIG_GPIO, reg)

        integration_time = 100
        self.write_byte(VL_SYSALS_INTEGRATION_PERIOD, 0)
        self.write_byte(VL_SYSALS_INTEGRATION_PERIOD + 1, integration_time)

        if gain > VL_ALS_GAIN_40:
            gain = VL_ALS_GAIN_40
        self.write_byte(VL_SYSALS_ANALOGUE_GAIN, 0x40 | gain)

        # start ALS
        self.write_byte(VL_SYSALS_START, 0x01)

        value = None
        i = 0
        while i < 10:
            i += 1

            status = self.read_byte(VL_RESULT_INTERRUPT_STATUS_GPIO)
            als_status = (status >> 3) & 0x07
            if als_status == 0x04:
                # reg = Eeprom16.address_to_bytes(VL_RESULT_ALS_VAL)
                # self.bus.write_byte_data(self.address, *reg)
                # data = self.bus.read_i2c_block_data(self.address, reg[0], 2)
                # print data

                value = self.read_word(VL_RESULT_ALS_VAL)
                break

            time.sleep(0.1)

        self.write_byte(VL_SYSTEM_INTERRUPT_CLEAR, 0x07)

        if value is None:
            self.logger.warning("Failed to get lux value")
            return None

        # The factory calibrated ALS lux resolution is 0.32 lux/count
        # for an analog gain of 1 & 100ms integration time (calibrated
        # without glass).
        lux = value * 0.32

        analog_gain = {
            VL_ALS_GAIN_1: 1.0,
            VL_ALS_GAIN_1_25: 1.25,
            VL_ALS_GAIN_1_67: 1.67,
            VL_ALS_GAIN_2_5: 2.5,
            VL_ALS_GAIN_5: 5.0,
            VL_ALS_GAIN_10: 10.0,
            VL_ALS_GAIN_20: 20.0,
            VL_ALS_GAIN_40: 40.0,
        }.get(gain)

        lux = lux * 100 / (analog_gain * integration_time)
        self.logger.debug("Lux is %d", lux)

        return lux


class TF_MINI_LIDAR():


    def __init__(self):

        self.ser = serial.Serial('/dev/ttyS0',115200,timeout = 1)
        self.initial_config()
        atexit.register(self.exit_handler)

    def exit_handler(self):
        self.ser.close()
        print "Closed ttyS0"

    def initial_config(self):
        #From product spec manual, STANDARD MODE
        self.ser.write(bytes(b'B'))
        self.ser.write(bytes(b'W'))
        self.ser.write(bytes(2))
        self.ser.write(bytes(0))
        self.ser.write(bytes(0))
        self.ser.write(bytes(0))
        self.ser.write(bytes(1))
        self.ser.write(bytes(6))

    #Read distance in cm
    def read_distance(self):
        header_1 = self.ser.read()
        header_2 = self.ser.read()
        header = b'Y'
        distance_total = 0
        if header_1 == b'Y' and header_2 == b'Y':
            distance_l = self.ser.read()
            distance_h = self.ser.read()
            distance_total = ord(distance_h)*256 + ord(distance_l)

        #skip strength data for now
        for i in range(0, 5):
            self.ser.read()
        
        return distance_total
