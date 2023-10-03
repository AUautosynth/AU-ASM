# -*- coding: utf-8 -*-
"""
The main functions which are always used to work with the printer

"""

# Standard import
import math as math
import time
import serial
import serial.tools.list_ports
import re

# Local import
from settings import settings



def start_sequence(prime=None, time_calculation=False):
    time_sum = 0
    serial_connection = None
    if not time_calculation:
        # find out what kind of board it has been connected to.
        if "Arduino" in settings.machine_board:
            baudrate = 250000
        elif "BTT Octo" in settings.machine_board: # the name of the octoprint board.... Could be confused for another board
            baudrate = 115200
        else:
            print("Uh oh, something is wrong")
            return

        print("Connecting to ", settings.comport)
        serial_connection = serial.Serial(settings.comport, baudrate=baudrate, writeTimeout=None, timeout=None)


    sleep_time = 5
    time_sum += sleep_time

    if not time_calculation:
        time.sleep(sleep_time)

    config_data = {"X": 0, "Y": 0, "Z": 0, "serial_connection": serial_connection}
    settings.configure_printer(config_data)

    sleep_time = 2

    time_sum += sleep_time

    if not time_calculation:
        time.sleep(sleep_time)
        settings.serial_connection.write("G28 \n".encode())  # homing command


    sleep_time = 35
    time_sum += sleep_time

    if not time_calculation:
        time.sleep(sleep_time)  # The longest time it will take to home the printer
        print("Home")

    sleep_time = move_to(z=settings.safety_height, time_calculation=time_calculation)
    if sleep_time:
        time_sum += sleep_time

    if prime is not None:
        for pump in prime:
            sleep_time = pump.prime(time_calculation=time_calculation)
            if sleep_time:
                time_sum += sleep_time

    return time_sum


def end_sequence(unprime=None, time_calculation=False):
    time_sum = 0
    sleep_time = move_to(x=100, y=100, time_calculation=time_calculation)
    if sleep_time:
        time_sum += sleep_time

    sleep_time = 10
    time_sum += sleep_time
    if not time_calculation:
        time.sleep(sleep_time)

    if unprime is not None:
        for pump in unprime:
            sleep_time = pump.unprime(time_calculation=time_calculation)
            if sleep_time:
                time_sum += sleep_time

    if not time_calculation:
        settings.serial_connection.write("M81 \n".encode())  ##Power off
        settings.serial_connection.close()
        settings.serial_connection = None

    return time_sum

def shake(time_calculation=False):
    time_sum = 0

    if not time_calculation:
        settings.serial_connection.write("M205 X30 \n".encode())
        for i in range(5):
            settings.serial_connection.write("G1 X{} \n".format(settings.X + 0.5).encode())
            settings.serial_connection.write("G1 X{} \n".format(settings.X - 0.5).encode())
    sleep_time = 10
    time_sum += sleep_time

    if not time_calculation:
        time.sleep(sleep_time)
        settings.serial_connection.write("M205 X10 \n".encode())

    return time_sum



def move_to(x=settings.X, y=settings.Y, z=settings.Z, time_calculation=False):
    time_sum = 0
    if x is None:
        x = settings.X
    if y is None:
        y = settings.Y
    if z is None:
        z = settings.Z
    if z != settings.Z:
        sleep = math.sqrt((z - settings.Z) ** 2)
    else:
        sleep = math.sqrt((x - settings.X) ** 2 + (y - settings.Y) ** 2)

    if not time_calculation:
        settings.serial_connection.write("G1 X{} Y{} Z{} \n".format(x, y, z).encode())
        print("Move to coordinate: X{} Y{} Z{}".format(x, y, z))


    sleep_time = (sleep / settings.feedrate) * 2
    time_sum += sleep_time

    if not time_calculation:
        time.sleep(sleep_time)

    # Update the printer head position
    settings.X, settings.Y, settings.Z = x, y, z
    return time_sum


def move_relative_to(x=settings.X, y=settings.Y, z=settings.Z, time_calculation=False):
    time_sum = 0
    # Calculate the necessary sleep time
    if x and y is not None:
        sleep = math.sqrt((x ** 2 + y ** 2))
    elif x is not None:
        sleep = math.sqrt(x ** 2)
    elif y is not None:
        sleep = math.sqrt(y ** 2)
    elif z is not None:
        sleep = math.sqrt(z ** 2)
    else:
        print("Error in move_relative_to function.")
    # Go into the relative room

    if not time_calculation:
        settings.serial_connection.write("G91\n".encode())

    sleep_time = 1
    time_sum += sleep_time

    if not time_calculation:
        time.sleep(sleep_time)

    if not time_calculation:
        # write the move function
        if x and y is not None:
            settings.serial_connection.write("G1 X{} Y{}\n".format(x, y).encode())
            print("Move X{} Y{}".format(x, y))
        elif x is not None:
            settings.serial_connection.write("G1 X{}\n".format(x).encode())
            print("Move X{}".format(x))
        elif y is not None:
            settings.serial_connection.write("G1 Y{}\n".format(y).encode())
            print("Move Y{}".format(y))
        elif z is not None:
            settings.serial_connection.write("G1 Z{}\n".format(z).encode())
            print("Move Z{}".format(z))

    sleep_time = (sleep / settings.feedrate) * 2 + 1
    time_sum += sleep_time

    if not time_calculation:
        time.sleep(sleep_time)
        # Go out of the relative room
        settings.serial_connection.write("G90 \n".encode())

    # Update the printer head position with the new relative movement
    if x is not None:
        settings.X += x
    if y is not None:
        settings.Y += y
    if z is not None:
        settings.Z += z

    return time_sum

