"""
Pi-Top Precision Movement Controller

A simple text-based interface for controlling pi-top robot movement
with precise distance (inches) and angle (degrees) inputs.

Uses minimal libraries: only pitop and built-in Python.
No PID controllers, no external math libraries.
"""

from pitop.robotics import DriveController
import time

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def inches_to_meters(inches):
    """
    Convert inches to meters.
    
    Args:
        inches (float): Distance in inches
        
    Returns:
        float: Distance in meters
    """
    return inches * 0.0254


def degrees_to_radians(degrees):
    """
    Convert degrees to radians.
    
    Args:
        degrees (float): Angle in degrees
        
    Returns:
        float: Angle in radians
    """
    return degrees * (3.141592653589793 / 180.0)


def percent_to_speed_factor(percent):
    """
    Convert speed percentage (0-100) to speed factor (0.0-1.0).
    
    Args:
        percent (float): Speed as percentage (0-100)
        
    Returns:
        float: Speed factor (0.0-1.0), clamped to valid range
    """
    # Clamp between 0 and 100
    clamped = max(0, min(100, percent))
    return clamped / 100.0


def get_positive_number(prompt, unit=""):
    """
    Get a positive number from user input with validation.
    
    Args:
        prompt (str): The prompt to display
        unit (str): The unit to display (e.g., "inches", "degrees")
        
    Returns:
        float: The validated number, or None if user cancels
        
    Raises:
        ValueError: If input is not a valid positive number
    """
    while True:
        try:
            user_input = input(f"{prompt} ({unit}): ").strip()
            
            # Allow user to escape
            if user_input.lower() == "exit":
                return None
                
            value = float(user_input)
            if value <= 0:
                print("  ⚠ Must be positive. Try again.")
                continue
            return value
        except ValueError:
            print("  ⚠ Invalid input. Enter a number.")


def get_speed_percent():
    """
    Get speed percentage from user with validation (0-100).
    
    Returns:
        float: Speed as percentage (0-100), or None if user cancels
    """
    while True:
        try:
            user_input = input("Speed (0-100, %): ").strip()
            
            if user_input.lower() == "exit":
                return None
                
            value = float(user_input)
            if value < 0 or value > 100:
                print("  ⚠ Speed must be between 0 and 100.")
                continue
            return value
        except ValueError:
            print("  ⚠ Invalid input. Enter a number.")


def get_movement_type():
    """
    Get movement type from user (Forward, Backward, or Rotate).
    
    Returns:
        str: "forward", "backward", "rotate", or None to exit
    """
    valid_types = ["forward", "backward", "rotate", "exit"]
    
    while True:
        user_input = input("\nMovement type (Forward/Backward/Rotate) or 'exit': ").strip().lower()
        
        if user_input in valid_types:
            return user_input if user_input != "exit" else None
        else:
            print("  ⚠ Valid options: Forward, Backward, Rotate, or exit")


def move_forward(drive, speed_percent, distance_inches):
    """
    Move the robot forward by a specified distance.
    
    Args:
        drive (DriveController): The drive controller instance
        speed_percent (float): Speed as percentage (0-100)
        distance_inches (float): Distance in inches
    """
    speed_factor = percent_to_speed_factor(speed_percent)
    distance_meters = inches_to_meters(distance_inches)
    
    print(f"\n➜ Moving forward {distance_inches} inches at {speed_percent}% speed...")
    
    try:
        drive.forward(speed_factor, distance=distance_meters)
        print(f"✓ Movement complete")
        time.sleep(0.5)
    except Exception as e:
        print(f"✗ Error during forward movement: {e}")
    finally:
        drive.stop()


def move_backward(drive, speed_percent, distance_inches):
    """
    Move the robot backward by a specified distance.
    
    Args:
        drive (DriveController): The drive controller instance
        speed_percent (float): Speed as percentage (0-100)
        distance_inches (float): Distance in inches
    """
    speed_factor = percent_to_speed_factor(speed_percent)
    distance_meters = inches_to_meters(distance_inches)
    
    print(f"\n➜ Moving backward {distance_inches} inches at {speed_percent}% speed...")
    
    try:
        drive.backward(speed_factor, distance=distance_meters)
        print(f"✓ Movement complete")
        time.sleep(0.5)
    except Exception as e:
        print(f"✗ Error during backward movement: {e}")
    finally:
        drive.stop()


def rotate_in_place(drive, speed_percent, angle_degrees):
    """
    Rotate the robot in place by a specified angle.
    
    Args:
        drive (DriveController): The drive controller instance
        speed_percent (float): Speed as percentage (0-100)
        angle_degrees (float): Angle in degrees
    """
    speed_factor = percent_to_speed_factor(speed_percent)
    angle_radians = degrees_to_radians(angle_degrees)
    
    print(f"\n➜ Rotating {angle_degrees} degrees at {speed_percent}% speed...")
    
    try:
        drive.rotate(angle_radians, max_speed_factor=speed_factor)
        print(f"✓ Rotation complete")
        time.sleep(0.5)
    except Exception as e:
        print(f"✗ Error during rotation: {e}")
    finally:
        drive.stop()


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """
    Main control loop for the pi-top movement controller.
    """
    print("=" * 60)
    print("  PI-TOP PRECISION MOVEMENT CONTROLLER")
    print("=" * 60)
    print("  Use inches for distance, degrees for rotation")
    print("  Type 'exit' at any time to quit\n")
    
    # Initialize the drive controller
    try:
        drive = DriveController()
        print("✓ Drive controller initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize drive controller: {e}")
        print("  Make sure the pi-top is powered on and connected.")
        return
    
    # Main control loop
    while True:
        # Get movement type from user
        movement = get_movement_type()
        if movement is None:
            break
        
        # Get speed (required for all movements)
        speed = get_speed_percent()
        if speed is None:
            break
        
        # Get distance or angle based on movement type
        if movement in ["forward", "backward"]:
            distance = get_positive_number("Distance", "inches")
            if distance is None:
                break
            
            if movement == "forward":
                move_forward(drive, speed, distance)
            else:
                move_backward(drive, speed, distance)
        
        elif movement == "rotate":
            angle = get_positive_number("Angle", "degrees")
            if angle is None:
                break
            
            rotate_in_place(drive, speed, angle)
    
    # Cleanup on exit
    print("\n" + "=" * 60)
    print("  Shutting down...")
    drive.stop()
    print("  ✓ Done. Goodbye!")
    print("=" * 60)


if __name__ == "__main__":
    main()
