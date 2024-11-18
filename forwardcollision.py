#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from pynput import keyboard

# Global variables
obstacle_nearby = False
move_cmd = Twist()

# Callback function to process laser scan data from the back
def scan_callback(data):
    global obstacle_nearby
    # Determine the indices for the back section of the scan (around 180 degrees)
    back_angles = data.ranges[len(data.ranges) // 2 + 170 : len(data.ranges) // 2 + 190]
    # Get the minimum distance in the back section
    min_distance = min(back_angles)
    obstacle_nearby = min_distance < 1.0
    # Print the minimum distance in the back section
    print(f"Back Distance to Obstacle: {min_distance:.2f} meters")

# Callback function to handle keystrokes
def on_press(key):
    global move_cmd

    try:
        if key.char == 'f':
            if not obstacle_nearby:
                # Move forward if no obstacle is within 1 meter in the back
                move_cmd.linear.x = 0.2
                move_cmd.angular.z = 0.0
            else:
                print("Obstacle detected! Cannot move forward.")
                move_cmd.linear.x = 0.0
        elif key.char == 'r':
            # Rotate right
            move_cmd.linear.x = 0.0
            move_cmd.angular.z = -0.5
        elif key.char == 'l':
            # Rotate left
            move_cmd.linear.x = 0.0
            move_cmd.angular.z = 0.5
    except AttributeError:
        pass

# Callback function to handle key release (stop movement)
def on_release(key):
    global move_cmd
    # Stop movement on key release
    move_cmd.linear.x = 0.0
    move_cmd.angular.z = 0.0

    if key == keyboard.Key.esc:
        # Stop listener on ESC
        return False

def main():
    global move_cmd

    # Initialize the ROS node
    rospy.init_node('turtlebot_key_control', anonymous=True)
    # Set up publisher and subscriber
    velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber('/scan', LaserScan, scan_callback)

    rate = rospy.Rate(10)  # 10 Hz

    # Set up the keyboard listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Main loop
    while not rospy.is_shutdown():
        # Publish movement commands
        velocity_publisher.publish(move_cmd)
        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

