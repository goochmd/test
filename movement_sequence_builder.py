#!/usr/bin/env python3
"""
Pi-top Robot Movement Sequence Builder
========================================
Interactive script to build and execute robot movement sequences.

The user is prompted to create movements one at a time, then can execute
the entire sequence with a key press.

Author: Created for pi-top robotics platform
"""

from time import sleep
from pitop.robotics import DriveController


class MovementSequenceBuilder:
    """Build and execute sequences of robot movements."""
    
    # Conversion constants
    INCHES_TO_METERS = 0.0254
    
    def __init__(self, left_motor_port="M1", right_motor_port="M2"):
        """Initialize the robot controller."""
        self.drive = DriveController(
            left_motor_port=left_motor_port,
            right_motor_port=right_motor_port
        )
        self.movements = []
        self.keep_running = True
        self.sequence_executed = False
        print("=" * 60)
        print("Pi-top Robot Movement Sequence Builder")
        print("=" * 60)
        print(f"\nRobot initialized with motors on {left_motor_port} and {right_motor_port}")
    
    def inches_to_meters(self, inches):
        """Convert inches to meters."""
        return inches * self.INCHES_TO_METERS
    
    def get_direction(self):
        """Prompt user for movement direction."""
        while True:
            print("\n" + "-" * 60)
            print("What direction would you like to go?")
            print("  1. Forward")
            print("  2. Backward")
            print("  3. Left")
            print("  4. Right")
            print("  5. Rotate")
            print("-" * 60)
            
            choice = input("Enter your choice (1-5 or name): ").strip().lower()
            
            if choice in ['1', 'forward', 'f']:
                return 'forward'
            elif choice in ['2', 'backward', 'b', 'back']:
                return 'backward'
            elif choice in ['3', 'left', 'l']:
                return 'left'
            elif choice in ['4', 'right', 'r']:
                return 'right'
            elif choice in ['5', 'rotate', 'rot']:
                return 'rotate'
            else:
                print("❌ Invalid choice. Please try again.")
    
    def get_speed(self):
        """Prompt user for movement speed."""
        while True:
            print("\n" + "-" * 60)
            print("How fast would you like to go for this movement?")
            print("  Examples: 30 (for 30%), 50, 75, 100")
            print("  Range: 1-100 percent")
            print("-" * 60)
            
            speed_input = input("Enter speed percentage: ").strip()
            
            try:
                speed_percent = float(speed_input)
                
                if 1 <= speed_percent <= 100:
                    speed_factor = speed_percent / 100.0
                    print(f"✓ Speed set to {speed_percent}% (factor: {speed_factor:.2f})")
                    return speed_factor
                else:
                    print("❌ Speed must be between 1 and 100 percent.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    def get_distance(self, direction):
        """Prompt user for movement distance."""
        while True:
            print("\n" + "-" * 60)
            if direction == 'rotate':
                print("How many degrees would you like to rotate?")
                print("  Positive values = clockwise")
                print("  Negative values = counter-clockwise")
                print("  Examples: 90, -90, 180, 45")
            else:
                print("How far would you like to go for this movement?")
                print("  Enter distance in inches")
                print("  Examples: 12, 6, 24, 3.5")
            print("-" * 60)
            
            distance_input = input("Enter distance: ").strip()
            
            try:
                distance = float(distance_input)
                
                if direction == 'rotate':
                    if distance != 0:
                        print(f"✓ Rotation set to {distance} degrees")
                        return distance
                    else:
                        print("❌ Rotation angle cannot be zero.")
                else:
                    if distance > 0:
                        distance_meters = self.inches_to_meters(distance)
                        print(f"✓ Distance set to {distance} inches ({distance_meters:.3f} meters)")
                        return distance
                    else:
                        print("❌ Distance must be greater than zero.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    def add_movement(self):
        """Add a movement to the sequence through interactive prompts."""
        print("\n" + "=" * 60)
        print(f"Creating Movement #{len(self.movements) + 1}")
        print("=" * 60)
        
        # Get direction
        direction = self.get_direction()
        
        # Get speed
        speed = self.get_speed()
        
        # Get distance
        distance = self.get_distance(direction)
        
        # Create movement dictionary
        movement = {
            'direction': direction,
            'speed': speed,
            'distance': distance
        }
        
        # Add to sequence
        self.movements.append(movement)
        
        # Display confirmation
        print("\n" + "=" * 60)
        print("✓ Movement Added Successfully!")
        print("=" * 60)
        self.display_movement(movement, len(self.movements))
    
    def display_movement(self, movement, index):
        """Display a single movement in a formatted way."""
        direction = movement['direction']
        speed = movement['speed']
        distance = movement['distance']
        
        print(f"\nMovement #{index}:")
        print(f"  Direction: {direction.capitalize()}")
        print(f"  Speed: {speed * 100:.0f}%")
        
        if direction == 'rotate':
            print(f"  Angle: {distance}°")
        else:
            distance_meters = self.inches_to_meters(distance)
            print(f"  Distance: {distance} inches ({distance_meters:.3f} meters)")
    
    def display_sequence(self):
        """Display the entire movement sequence."""
        if not self.movements:
            print("\n📋 No movements in sequence yet.")
            return
        
        print("\n" + "=" * 60)
        print("Current Movement Sequence")
        print("=" * 60)
        
        for i, movement in enumerate(self.movements, 1):
            self.display_movement(movement, i)
        
        print("\n" + "=" * 60)
        print(f"Total movements: {len(self.movements)}")
        print("=" * 60)
    
    def execute_movement(self, movement, index):
        """Execute a single movement."""
        direction = movement['direction']
        speed = movement['speed']
        distance = movement['distance']
        
        print(f"\n▶ Executing Movement #{index}: {direction.upper()}")
        
        if direction == 'forward':
            distance_meters = self.inches_to_meters(distance)
            self.drive.forward(speed_factor=speed, distance=distance_meters)
            
        elif direction == 'backward':
            distance_meters = self.inches_to_meters(distance)
            self.drive.backward(speed_factor=speed, distance=distance_meters)
            
        elif direction == 'left':
            distance_meters = self.inches_to_meters(distance)
            # Using a turn radius of 0.3 meters for curved turns
            self.drive.left(speed_factor=speed, turn_radius=0.3, distance=distance_meters)
            
        elif direction == 'right':
            distance_meters = self.inches_to_meters(distance)
            # Using a turn radius of 0.3 meters for curved turns
            self.drive.right(speed_factor=speed, turn_radius=0.3, distance=distance_meters)
            
        elif direction == 'rotate':
            self.drive.rotate(angle=distance, max_speed_factor=speed)
        
        # Wait for movement to complete
        sleep(0.5)
    
    def execute_sequence(self):
        """Execute the entire movement sequence."""
        if not self.movements:
            print("\n❌ No movements to execute! Please create a sequence first.")
            return
        
        print("\n" + "=" * 60)
        print("🚀 EXECUTING MOVEMENT SEQUENCE")
        print("=" * 60)
        
        for i, movement in enumerate(self.movements, 1):
            try:
                self.execute_movement(movement, i)
                print(f"✓ Movement #{i} completed")
            except Exception as e:
                print(f"❌ Error executing movement #{i}: {e}")
                self.drive.stop()
                break
            
            # Small pause between movements
            sleep(0.5)
        
        print("\n" + "=" * 60)
        print("✓ Sequence execution complete!")
        print("=" * 60)
        
        # Stop motors to be safe
        self.drive.stop()
    
    def build_sequence(self):
        """Interactive loop to build movement sequence."""
        print("\n" + "=" * 60)
        print("Let's build your movement sequence!")
        print("=" * 60)
        
        while True:
            # Add a movement
            self.add_movement()
            
            # Ask if they want to add another
            print("\n" + "=" * 60)
            while True:
                response = input("\nWould you like to create another movement? (yes/no): ").strip().lower()
                
                if response in ['yes', 'y']:
                    break
                elif response in ['no', 'n']:
                    return
                else:
                    print("❌ Please answer 'yes' or 'no'")
    
    def clear_sequence(self):
        """Clear all movements from the sequence."""
        self.movements = []
        print("\n✓ Sequence cleared!")
    
    def run(self):
        """Main program loop."""
        # Build the sequence
        self.build_sequence()
        
        # Display the final sequence
        self.display_sequence()
        
        if not self.movements:
            print("\n❌ No movements created. Exiting.")
            return
        
        # Set up keyboard control to run sequence
        print("\n" + "=" * 60)
        print("Sequence Created Successfully!")
        print("=" * 60)
        print("\n📝 Press the SPACEBAR to execute the sequence")
        print("   Press ESC to exit without running")
        print("\nWaiting for key press...")
        
        # Flag to control the loop
        self.keep_running = True
        self.sequence_executed = False
        
        try:
            # Create keyboard button for spacebar
            
            temp = input("Press space for yippee")
            if temp==" ":
                self.execute_sequence()
                self.sequence_executed = True
                
                # Ask if they want to run again
                while self.keep_running:
                    print("\n" + "=" * 60)
                    response = input("Run sequence again? (yes/no): ").strip().lower()
                    
                    if response in ['yes', 'y']:
                        print("\n🔄 Running sequence again...\n")
                        self.execute_sequence()
                    elif response in ['no', 'n']:
                        print("\n👋 Exiting program. Goodbye!")
                        self.keep_running = False
                        break
                    else:
                        print("❌ Please answer 'yes' or 'no'")
            
            # Keep the program running with a simple loop
            print("\n⌨️  Keyboard controls active...")
            
            while self.keep_running:
                sleep(0.1)  # Small sleep to prevent CPU spinning
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Program interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            # Ensure motors are stopped
            self.drive.stop()
            print("\n✓ Motors stopped. Program ended safely.")


def main():
    """Main entry point."""
    try:
        # Create the sequence builder
        builder = MovementSequenceBuilder(
            left_motor_port="M1",
            right_motor_port="M2"
        )
        
        # Run the interactive program
        builder.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Thank you for using the Movement Sequence Builder!")


if __name__ == "__main__":
    main()
