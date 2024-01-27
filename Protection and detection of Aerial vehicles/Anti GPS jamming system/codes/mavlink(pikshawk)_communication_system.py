from pymavlink import mavutil
import time

# Set your serial port and baudrate
serial_port = 'COM11'
baudrate = 57600

def handle_global_position(msg):
    # Extract latitude, longitude, and altitude from GLOBAL_POSITION_INT message
    latitude = msg.lat / 1e7  # Convert from degrees * 1e7 to degrees
    longitude = msg.lon / 1e7  # Convert from degrees * 1e7 to degrees
    altitude = msg.alt / 1000.0  # Convert from millimeters to meters

    print(f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude} meters")

def main():
    try:
        # Connect to the serial port
        mavlink = mavutil.mavlink_connection(serial_port, baud=baudrate)

        print(f"Reading GPS data from {serial_port}... Press Ctrl+C to stop.")

        while True:
            # Wait for a MAVLink message
            msg = mavlink.recv_msg()

            if msg is not None:
                # Check for GLOBAL_POSITION_INT message
                if msg.get_type() == 'GLOBAL_POSITION_INT':
                    handle_global_position(msg)

    except Exception as e:
        print(f"Error: {e}")

if _name_ == "_main_":
    main()