#!/usr/bin/env python3
"""
Pi-top Robot Movement Sequence Builder
========================================
Interactive script to build and execute robot movement sequences.

ARCHITECTURAL NOTES:
- All distances are in inches; converted to meters only at execution time
- All angles are in degrees
- Speed is expressed as a factor (0.0 to 1.0), where 1.0 = 100%
- Time-based motion control requires careful synchronization between
  distance/angle, speed factor, and motor capabilities
- For deterministic behavior, we separate motion specification from
  execution timing and validate constraints before executing

MOTOR CAPABILITY CONSTRAINTS:
- Linear motion: estimated max speed ~1.0 m/s (at 100% speed factor)
- Rotational motion: estimated max speed ~360°/s (at 100% speed factor)
- Minimum speed factor for reliable motion: ~0.1 (10%)
- Maximum execution time per command: ~60 seconds (library dependent)
- All calculations include safety margins

Author: Created for pi-top robotics platform
"""

from time import sleep
from pitop.robotics import DriveController


class MovementSequenceBuilder:
    """Build and execute sequences of robot movements with deterministic behavior."""
    
    # ==================== CONSTANTS ====================
    # Unit conversions
    INCHES_TO_METERS = 0.0254
    METERS_TO_INCHES = 1 / INCHES_TO_METERS
    
    # Motor capability estimates (derived from testing)
    # These represent maximum theoretical speeds at 100% speed factor
    MAX_LINEAR_VELOCITY_MS = 1.0  # meters/second at 100% speed
    MAX_ANGULAR_VELOCITY_DEG_S = 360.0  # degrees/second at 100% speed
    
    # Safety constraints
    MIN_SPEED_FACTOR = 0.1  # 10% minimum for reliable operation
    MAX_EXECUTION_TIME = 60.0  # seconds; prevents infinite loops
    
    # Time safety margin: add to calculated time to ensure motor has budget
    # This prevents "too fast for current speed" errors
    TIME_SAFETY_MARGIN = 1.2  # multiply calculated time by this factor
    
    def __init__(self, left_motor_port: str = "M1", right_motor_port: str = "M2") -> None:
        """Initialize the robot controller with specified motor ports."""
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
        print("\n📋 Motor Specifications:")
        print(f"  Max linear speed: {self.MAX_LINEAR_VELOCITY_MS} m/s (at 100%)")
        print(f"  Max rotational speed: {self.MAX_ANGULAR_VELOCITY_DEG_S}°/s (at 100%)")
        print(f"  Min speed factor: {self.MIN_SPEED_FACTOR * 100}%")
    
    # ==================== UNIT CONVERSION ====================
    
    def inches_to_meters(self, inches: float) -> float:
        """Convert inches to meters."""
        return inches * self.INCHES_TO_METERS
    
    def meters_to_inches(self, meters: float) -> float:
        """Convert meters to inches."""
        return meters * self.METERS_TO_INCHES
    
    # ==================== TIMING & CONSTRAINT CALCULATIONS ====================
    
    def calculate_linear_time(self, distance_inches: float, speed_factor: float) -> float:
        """
        Calculate time required for linear movement.
        
        Args:
            distance_inches: Distance in inches
            speed_factor: Speed as fraction (0.0 to 1.0)
        
        Returns:
            time_seconds: Time in seconds, clamped to safety limits
        
        Formula:
            velocity = speed_factor * MAX_LINEAR_VELOCITY_MS
            time = distance_meters / velocity
        
        Safety:
            - Clamps speed_factor to valid range
            - Applies margin to prevent "too fast" errors
            - Limits maximum execution time
        """
        # Clamp speed factor to valid range
        speed_factor = max(self.MIN_SPEED_FACTOR, min(1.0, speed_factor))
        
        # Calculate velocity at this speed factor
        velocity_ms = speed_factor * self.MAX_LINEAR_VELOCITY_MS
        
        # Convert distance to meters
        distance_meters = self.inches_to_meters(distance_inches)
        
        # Calculate base time
        time_base = distance_meters / velocity_ms if velocity_ms > 0 else 0
        
        # Apply safety margin to prevent timing conflicts
        time_with_margin = time_base * self.TIME_SAFETY_MARGIN
        
        # Clamp to maximum execution time
        time_final = min(time_with_margin, self.MAX_EXECUTION_TIME)
        
        return time_final
    
    def calculate_rotational_time(self, angle_degrees: float, speed_factor: float) -> float:
        """
        Calculate time required for rotational movement.
        
        Args:
            angle_degrees: Rotation angle in degrees (positive=clockwise)
            speed_factor: Speed as fraction (0.0 to 1.0)
        
        Returns:
            time_seconds: Time in seconds, clamped to safety limits
        
        Formula:
            angular_velocity = speed_factor * MAX_ANGULAR_VELOCITY_DEG_S
            time = |angle_degrees| / angular_velocity
        
        Safety:
            - Uses absolute value of angle
            - Clamps speed_factor to valid range
            - Applies margin to prevent "too fast" errors
            - Validates against motor capability constraints
        """
        # Clamp speed factor to valid range
        speed_factor = max(self.MIN_SPEED_FACTOR, min(1.0, speed_factor))
        
        # Use absolute angle (direction determined by sign, not magnitude)
        angle_abs = abs(angle_degrees)
        
        # Calculate angular velocity at this speed factor
        angular_velocity_deg_s = speed_factor * self.MAX_ANGULAR_VELOCITY_DEG_S
        
        # Calculate base time
        time_base = angle_abs / angular_velocity_deg_s if angular_velocity_deg_s > 0 else 0
        
        # Apply safety margin—THIS IS THE KEY FIX FOR LOW-SPEED ROTATION ERROR
        # By multiplying the time, we give the motor more budget at lower speeds
        time_with_margin = time_base * self.TIME_SAFETY_MARGIN
        
        # Clamp to maximum execution time
        time_final = min(time_with_margin, self.MAX_EXECUTION_TIME)
        
        return time_final
    
    # ==================== USER INPUT ====================
    
    def get_direction(self) -> str:
        """Prompt user for movement direction.
        
        Returns:
            str: Direction name ('forward', 'backward', 'left', 'right', 'rotate')
        """
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
    
    def get_speed(self) -> float:
        """Prompt user for movement speed.
        
        Returns:
            float: Speed factor between MIN_SPEED_FACTOR and 1.0
        """
        while True:
            print("\n" + "-" * 60)
            print("How fast would you like to go for this movement?")
            print(f"  Range: {self.MIN_SPEED_FACTOR*100:.0f}-100 percent")
            print("  Examples: 30, 50, 75, 100")
            print("-" * 60)
            
            speed_input = input("Enter speed percentage: ").strip()
            
            try:
                speed_percent = float(speed_input)
                
                if self.MIN_SPEED_FACTOR * 100 <= speed_percent <= 100:
                    speed_factor = speed_percent / 100.0
                    print(f"✓ Speed set to {speed_percent}% (factor: {speed_factor:.2f})")
                    return speed_factor
                else:
                    print(f"❌ Speed must be between {self.MIN_SPEED_FACTOR*100:.0f} and 100 percent.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    def get_distance(self, direction: str) -> float:
        """Prompt user for movement distance or rotation angle.
        
        Args:
            direction: Type of movement ('forward', 'backward', 'left', 'right', 'rotate')
        
        Returns:
            float: Distance in inches (or angle in degrees if rotating)
        """
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
                print("  Examples: 12, 6, 24, 3.5, 36, 48")
            print("-" * 60)
            
            distance_input = input("Enter distance: ").strip()
            
            try:
                distance = float(distance_input)
                
                if direction == 'rotate':
                    if distance != 0:
                        print(f"✓ Rotation set to {distance}°")
                        return distance
                    else:
                        print("❌ Rotation angle cannot be zero.")
                else:
                    if distance > 0:
                        distance_meters = self.inches_to_meters(distance)
                        print(f"✓ Distance set to {distance} inches ({distance_meters:.3f} m)")
                        return distance
                    else:
                        print("❌ Distance must be greater than zero.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
    
    def add_movement(self) -> None:
        """Add a movement to the sequence through interactive prompts.
        
        Guides user through direction, speed, and distance selection,
        then appends the movement to the sequence and displays confirmation.
        """
        print("\n" + "=" * 60)
        print(f"Creating Movement #{len(self.movements) + 1}")
        print("=" * 60)
        
        direction = self.get_direction()
        speed = self.get_speed()
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
    
    # ==================== DISPLAY ====================
    
    def display_movement(self, movement: dict, index: int) -> None:
        """Display a single movement with timing information.
        
        Args:
            movement: Movement dict with 'direction', 'speed', 'distance' keys
            index: Movement sequence number
        """
        direction = movement['direction']
        speed = movement['speed']
        distance = movement['distance']
        
        print(f"\nMovement #{index}:")
        print(f"  Direction: {direction.upper()}")
        print(f"  Speed: {speed * 100:.0f}%")
        
        if direction == 'rotate':
            time_required = self.calculate_rotational_time(distance, speed)
            print(f"  Angle: {distance}°")
            print(f"  Estimated time: {time_required:.2f}s")
        else:
            distance_meters = self.inches_to_meters(distance)
            time_required = self.calculate_linear_time(distance, speed)
            print(f"  Distance: {distance} inches ({distance_meters:.3f} m)")
            print(f"  Estimated time: {time_required:.2f}s")
    
    def display_sequence(self) -> None:
        """Display the entire movement sequence with timing summary.
        
        Shows all movements in sequence with individual and total timing estimates.
        """
        if not self.movements:
            print("\n📋 No movements in sequence yet.")
            return
        
        print("\n" + "=" * 60)
        print("Current Movement Sequence")
        print("=" * 60)
        
        total_time = 0
        for i, movement in enumerate(self.movements, 1):
            self.display_movement(movement, i)
            
            if movement['direction'] == 'rotate':
                total_time += self.calculate_rotational_time(
                    movement['distance'], movement['speed']
                )
            else:
                total_time += self.calculate_linear_time(
                    movement['distance'], movement['speed']
                )
        
        print("\n" + "=" * 60)
        print(f"Total movements: {len(self.movements)}")
        print(f"Estimated total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        print("=" * 60)
    
    # ==================== EXECUTION ====================
    
    def execute_movement(self, movement: dict, index: int) -> None:
        """
        Execute a single movement with proper timing.
        
        All movements are time-based to ensure:
        1. Distance/angle traveled is independent of speed
        2. Rotation angle is deterministic
        3. No timing conflicts at low speeds
        """
        direction = movement['direction']
        speed = movement['speed']
        distance = movement['distance']
        
        print(f"\n▶ Executing Movement #{index}: {direction.upper()}")
        
        try:
            if direction == 'forward':
                distance_meters = self.inches_to_meters(distance)
                time_to_take = self.calculate_linear_time(distance, speed)
                print(f"  → {distance} inches at {speed*100:.0f}% speed ({time_to_take:.2f}s)")
                self.drive.forward(speed_factor=speed, distance=distance_meters)
                
            elif direction == 'backward':
                distance_meters = self.inches_to_meters(distance)
                time_to_take = self.calculate_linear_time(distance, speed)
                print(f"  ← {distance} inches at {speed*100:.0f}% speed ({time_to_take:.2f}s)")
                self.drive.backward(speed_factor=speed, distance=distance_meters)
                
            elif direction == 'left':
                distance_meters = self.inches_to_meters(distance)
                time_to_take = self.calculate_linear_time(distance, speed)
                print(f"  ↶ {distance} inches at {speed*100:.0f}% speed ({time_to_take:.2f}s)")
                # Turn radius of 0.3m provides tight turns
                self.drive.left(speed_factor=speed, turn_radius=0.3, distance=distance_meters)
                
            elif direction == 'right':
                distance_meters = self.inches_to_meters(distance)
                time_to_take = self.calculate_linear_time(distance, speed)
                print(f"  ↷ {distance} inches at {speed*100:.0f}% speed ({time_to_take:.2f}s)")
                # Turn radius of 0.3m provides tight turns
                self.drive.right(speed_factor=speed, turn_radius=0.3, distance=distance_meters)
                
            elif direction == 'rotate':
                time_to_take = self.calculate_rotational_time(distance, speed)
                print(f"  ↻ {distance}° at {speed*100:.0f}% speed ({time_to_take:.2f}s)")
                # KEY FIX: Pass calculated time_to_take to rotate()
                # This ensures rotation is deterministic and speed-independent
                self.drive.rotate(
                    angle=distance,
                    max_speed_factor=speed,
                    time_to_take=time_to_take
                )
            
            # Wait for movement to complete
            sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.drive.stop()
            raise
    
    def execute_sequence(self) -> None:
        """Execute the entire movement sequence safely.
        
        Runs all movements in order with error handling and stops motors on completion.
        """
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
    
    def build_sequence(self) -> None:
        """Interactive loop to build movement sequence.
        
        Allows user to add multiple movements until they choose to finish.
        """
        print("\n" + "=" * 60)
        print("Let's build your movement sequence!")
        print("=" * 60)
        
        while True:
            self.add_movement()
            
            print("\n" + "=" * 60)
            while True:
                response = input("\nWould you like to create another movement? (yes/no): ").strip().lower()
                
                if response in ['yes', 'y']:
                    break
                elif response in ['no', 'n']:
                    return
                else:
                    print("❌ Please answer 'yes' or 'no'")
    
    def clear_sequence(self) -> None:
        """Clear all movements from the sequence."""
        self.movements = []
        print("\n✓ Sequence cleared!")
    
    def run(self) -> None:
        """Main program loop.
        
        Orchestrates sequence building, display, and execution with user interaction.
        """
        # Build the sequence
        self.build_sequence()
        
        # Display the final sequence
        self.display_sequence()
        
        if not self.movements:
            print("\n❌ No movements created. Exiting.")
            return
        
        # Ready to execute
        print("\n" + "=" * 60)
        print("Sequence Created Successfully!")
        print("=" * 60)
        print("\n📝 Press SPACEBAR to execute the sequence")
        print("   Press anything else to exit")
        print("\nWaiting for key press...")
        
        self.keep_running = True
        self.sequence_executed = False
        
        try:
            temp = input("Press space to execute: ")
            if temp == " ":
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
            
            while self.keep_running:
                sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Program interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.drive.stop()
            print("\n✓ Motors stopped. Program ended safely.")


def main() -> None:
    """Main entry point.
    
    Initializes MovementSequenceBuilder and runs the interactive program.
    """
    try:
        builder = MovementSequenceBuilder(
            left_motor_port="M1",
            right_motor_port="M2"
        )
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
