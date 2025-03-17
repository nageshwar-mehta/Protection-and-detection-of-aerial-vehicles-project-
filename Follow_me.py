"""
© Copyright 2015-2016, 3D Robotics.
Modified to use pynmea2 and serial for GPS reading.

This script tracks the GPS position of your computer and moves the drone accordingly.

Example documentation: http://python.dronekit.io/examples/follow_me.html
"""
from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobalRelative
import serial
import pynmea2
import socket
import time
import sys
import argparse  

# Set up option parsing to get connection string
parser = argparse.ArgumentParser(description='Tracks GPS position of your computer.')
parser.add_argument('--connect', help="vehicle connection target string.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

# Connect to the vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, timeout=300)

# Set the serial port and baud rate for GPS
SERIAL_PORT = "/dev/ttyUSB0"  # Change this based on your system (e.g., "/dev/ttyUSB0" for Linux)
BAUD_RATE = 4800  # Check your GPS module's baud rate


def read_gps():
    """
    Reads GPS data from a serial-connected GPS module.
    Returns latitude, longitude if successful; otherwise, returns None.
    """
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                msg = pynmea2.parse(line)
                return msg.latitude, msg.longitude
    except (pynmea2.ParseError, UnicodeDecodeError, serial.SerialException) as e:
        print(f"GPS Error: {e}")
    return None, None


def arm_and_takeoff(aTargetAltitude):
    """
    Arms the vehicle and flies to the specified altitude.
    """
    print("Basic pre-arm checks")
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True    

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)

    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


try:
    # Arm and take off to 5 meters
    arm_and_takeoff(5)

    while True:
        if vehicle.mode.name != "GUIDED":
            print("User has changed flight modes - aborting follow-me")
            break    

        # Read GPS data
        lat, lon = read_gps()
        if lat is not None and lon is not None:
            altitude = 10  # Fixed altitude
            dest = LocationGlobalRelative(lat, lon, altitude)
            print(f"Going to: {dest}")

            # Send new waypoint
            vehicle.simple_goto(dest)

        # Update every 0.1 seconds
        time.sleep(0.1)

except socket.error:
    print("Error: GPS module is not connected properly.")
    sys.exit(1)

# Close vehicle connection before exiting
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started
if sitl is not None:
    sitl.stop()

print("Completed")

