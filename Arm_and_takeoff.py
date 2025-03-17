from dronekit import connect, VehicleMode
import time

def arm_and_takeoff(target_altitude):
    """
    Arms the drone and flies it to the target altitude.
    """
    print("Arming motors...")
    while not vehicle.is_armable:
        print("Waiting for vehicle to become armable...")
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(target_altitude)

    while True:
        print(f"Altitude: {vehicle.location.global_relative_frame.alt:.2f}m")
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Target altitude reached!")
            break
        time.sleep(1)

# Connect to the drone
print("Connecting to drone...")
vehicle = connect("udp:192.168.4.2:14550", wait_ready=True)
print("Connected successfully!")

# Take off to 30m
arm_and_takeoff(10)

# Hover for 5 seconds
time.sleep(5)

# Land the drone
print("Landing...")
vehicle.mode = VehicleMode("LAND")

# Wait until landed
while vehicle.armed:
    print(f"Altitude: {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("Landed successfully!")

# Close connection
vehicle.close()
print("Connection closed.")

