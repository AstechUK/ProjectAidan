from gpiozero import OutputDevice
import time
import sys
import threading
from PyQt5.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine


class MotorController(QObject):
    stateChanged = Signal(str)
    modeChanged = Signal(str)
    speedChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.state = "SAFE"
        self.mode = "fwd"  # Default mode
        self.speed = "low"  # Default speed
        self.motor_thread = None
        self.running = False
        self.current_direction = "forward"  # Initialize current_direction
        self.current_speed_rpm = 0  # Initialize current_speed_rpm as well
        self.steps_per_revolution = 200  # Define steps per revolution for your motor here
        self.in_sequence = False
        self.pulse_timer = None
        self.restart_timer = None


    def stop_motor_smoothly(self):
        # Target RPM is 0 for stopping
        target_rpm = 0
        # Define the number of steps and interval for ramping down
        steps = 15
        interval = 0.1  # seconds

        print("Initiating smooth stop...")
        # Use ramp_speed to decrease the speed to 0
        self.ramp_speed(target_rpm, steps, interval)

        # After ramping down to 0, ensure the motor is completely stopped
        # and perform any additional logic needed to safely stop the motor
        # This could involve sending a specific stop command to your motor controller,
        # if required, beyond just reducing the speed to zero.
        print("Motor smoothly stopped.")
        # Reset or update any necessary state variables here
        self.current_speed_rpm = 0
        # If you have a specific motor stop command or need to reset the driver state, do it here
        # e.g., self.send_motor_stop_command()

        # Optionally, update the state to reflect the motor is stopped
        self.state = "SAFE"
        self.stateChanged.emit(self.state)






    def set_motor_sequence(self, target_speed, direction, duration=None):
        self.speeds_rpm = {"low": 500, "mid": 1000, "high": 1500}
        self.steps_per_revolution = 200
        self.ramp_steps = 15
        self.ramp_interval = 0.1

        if target_speed in self.speeds_rpm:
            target_rpm = self.speeds_rpm[target_speed]

            if self.current_direction != direction:
                # Ramp down to 0 first if changing direction
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                self.current_direction = direction

            # Ramp to the target speed
            self.ramp_speed(target_rpm, self.ramp_steps, self.ramp_interval)

            # If a duration is specified, use a timer to stop or change speed later
            # This part is simplified as the main looping logic is now handled by the pulse_pattern method
            if duration is not None:
                threading.Timer(duration, lambda: self.ramp_speed(0, self.ramp_steps, self.ramp_interval)).start()
        else:
            print(f"Invalid motor sequence settings: speed={target_speed}, direction={direction}")





    def ramp_speed(self, target_rpm, steps, interval):
        if self.current_speed_rpm == target_rpm:
            print("Target speed already achieved. No adjustment needed.")
            return  # Exit early if no change in speed is needed

        current_rpm = self.current_speed_rpm
        rpm_step = (target_rpm - current_rpm) / steps
        target_reached = False  # Flag to indicate when the target speed has been reached

        for _ in range(steps):
            if not target_reached:
                current_rpm += rpm_step
                # Round current_rpm to the nearest whole number
                current_rpm = round(current_rpm)
                self.current_speed_rpm = current_rpm
                steps_per_second = round(current_rpm * self.steps_per_revolution / 60)

                # Update your motor control logic here to adjust to the new steps_per_second
                print(f"Adjusting speed: {current_rpm} RPM ({steps_per_second} steps/sec)")
                time.sleep(interval)

            if abs(self.current_speed_rpm - target_rpm) < abs(rpm_step):
                target_reached = True

        if self.current_speed_rpm != target_rpm:
            self.current_speed_rpm = target_rpm
            steps_per_second = round(target_rpm * self.steps_per_revolution / 60)
            print(f"Final speed adjustment: {target_rpm} RPM ({steps_per_second} steps/sec)")










    @Slot(str)
    def set_state(self, state):
        # Ensure mode and speed are set before starting the motor
        if state == "RUN" or state == "TIMED":
            if self.mode is None or self.speed is None:
                print("Cannot set state to RUN: Mode or speed not set.")
                return  # Early exit if mode or speed are not set
            # Start the motor if mode and speed are set
            if not self.running:  # Check if the motor is not already running
                self.state = state
                self.stateChanged.emit(self.state)
                print(f"State changed to: {self.state}")
                self.start_motor()
        elif state == "SAFE":
            self.state = state
            self.stateChanged.emit(self.state)
            print(f"State changed to: {self.state}")
            self.stop_motor()
        else:
            print(f"Invalid state: {state}")

    @Slot(str)
    def set_mode(self, mode):
        self.mode = mode
        self.modeChanged.emit(self.mode)
        print(f"Mode set to: {self.mode}")

    @Slot(str)
    def set_speed(self, speed):
        self.speed = speed
        self.speedChanged.emit(self.speed)
        print(f"Speed set to: {self.speed}")

    @Slot(str)
    def start_stop_motor(self, motorState):
        if motorState == "run":
            self.set_state("RUN")
        elif motorState == "idle":
            self.set_state("SAFE")

    def motor_operation(self):
        self.running = True
        while self.running:
            operation_method = self.get_operation_method()
            if operation_method:
                operation_method()
            time.sleep(1)  # Use time.sleep

    def get_operation_method(self):
        if self.mode is None or self.speed is None:
            print("Mode or speed not set. Cannot start motor operation.")
            return None
        method_name = f"run_{self.mode.lower()}_{self.speed.lower()}"
        return getattr(self, method_name, None)

    # Define specific motor control methods for each mode and speed combination


    def run_fwd_low(self):
        self.set_motor_sequence("low", "forward", duration=None)
        print("Running FORWARD at LOW speed indefinitely.")


    def run_fwd_mid(self):
        self.set_motor_sequence("mid", "forward", duration=None)
        print("Running FORWARD at MID speed.")

    def run_fwd_high(self):
        self.set_motor_sequence("high", "forward", duration=None)
        print("Running FORWARD at HIGH speed.")

    def run_rwd_low(self):
        self.set_motor_sequence("low", "reverse", duration=None)
        print("Running REVERSE at LOW speed indefinitely.")

    def run_rwd_mid(self):
        self.set_motor_sequence("mid", "reverse", duration=None)
        print("Running REVERSE at MID speed.")

    def run_rwd_high(self):
        self.set_motor_sequence("high", "reverse", duration=None)
        print("Running REVERSE at HIGH speed.")


    def run_pulse_low(self):
        print("Starting continuous PULSE mode: MID for 10 seconds, then LOW for 5 seconds.")
        self.running = True  # Indicate the motor operation has started

        try:
            while self.running:
                # Set to MID speed and wait
                print("Setting speed to MID.")
                self.set_motor_sequence("mid", "forward")  # Set speed without duration
                time.sleep(10)  # Wait for 10 seconds at MID speed
                if not self.running:
                    break  # Exit if the operation was stopped during the MID phase

                # Set to LOW speed and wait
                print("Switching speed to LOW.")
                self.set_motor_sequence("low", "forward")  # Set speed without duration
                time.sleep(5)  # Wait for 5 seconds at LOW speed
                if not self.running:
                    break  # Exit if the operation was stopped during the LOW phase

        except Exception as e:
            print(f"Exception in run_pulse_mid: {e}")
        finally:
            print("Ending PULSE mode.")



    def run_pulse_mid(self):
        print("Starting continuous PULSE mode: MID for 10 seconds, then LOW for 5 seconds.")
        self.running = True  # Indicate the motor operation has started

        try:
            while self.running:
                # Set to MID speed and wait
                print("Setting speed to MID.")
                self.set_motor_sequence("mid", "forward")  # Set speed without duration
                time.sleep(10)   # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the MID phase

                # Set to LOW speed and wait
                print("Switching speed to LOW.")
                self.set_motor_sequence("low", "forward")  # Set speed without duration
                time.sleep(5)   # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the LOW phase

        except Exception as e:
            print(f"Exception in run_pulse_mid: {e}")
        finally:
            print("Ending PULSE mode.")



    def run_pulse_high(self):
        print("Starting continuous PULSE mode: MID for 10 seconds, then LOW for 5 seconds.")
        self.running = True  # Indicate the motor operation has started

        try:
            while self.running:
                # Set to MID speed and wait
                print("Setting speed to MID.")
                self.set_motor_sequence("high", "forward")  # Set speed without duration
                time.sleep(10)  # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the MID phase

                # Set to LOW speed and wait
                print("Switching speed to LOW.")
                self.set_motor_sequence("mid", "forward")  # Set speed without duration
                time.sleep(5)   # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the LOW phase

        except Exception as e:
            print(f"Exception in run_pulse_mid: {e}")
        finally:
            print("Ending PULSE mode.")



    def run_mix_low(self):
        print("Starting MIX mode at LOW speed, alternating direction.")
        self.running = True  # Ensure the motor operation flag is set

        try:
            while self.running:
                # Set to forward direction at low speed
                print("Setting direction to FORWARD at LOW speed.")
                self.set_motor_sequence("low", "forward")
                # Use a responsive sleep mechanism
                for _ in range(15):  # 30 seconds split into 1-second checks
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                # Decelerate to stop before changing direction, checking for stop command
                print("Decelerating to stop...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                if not self.running:
                    break

                # Set to reverse direction at low speed
                print("Setting direction to REVERSE at LOW speed.")
                self.set_motor_sequence("low", "reverse")
                # Use a responsive sleep mechanism again
                for _ in range(5):  # 5 seconds split into 1-second checks
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                # Decelerate to stop before changing direction again
                print("Decelerating to stop...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)

        except Exception as e:
            print(f"Exception in run_mix_low: {e}")
        finally:
            print("Ending MIX mode.")


    def run_mix_mid(self):
        print("Starting MIX mode at MID speed, alternating direction.")
        self.running = True

        try:
            while self.running:
                # Set to forward direction at mid speed
                print("Setting direction to FORWARD at MID speed.")
                self.set_motor_sequence("mid", "forward")
                for _ in range(15):  # Responsive sleep for 30 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before reversing...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                if not self.running:
                    break

                # Set to reverse direction at mid speed
                print("Setting direction to REVERSE at MID speed.")
                self.set_motor_sequence("mid", "reverse")
                for _ in range(5):  # Responsive sleep for 5 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before switching direction again...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)

        except Exception as e:
            print(f"Exception in run_mix_mid: {e}")
        finally:
            print("Ending MIX mode.")


    def run_mix_high(self):
        print("Starting MIX mode at HIGH speed, alternating direction.")
        self.running = True

        try:
            while self.running:
                # Set to forward direction at high speed
                print("Setting direction to FORWARD at HIGH speed.")
                self.set_motor_sequence("high", "forward")
                for _ in range(15):  # Responsive sleep for 30 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before reversing...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                if not self.running:
                    break

                # Set to reverse direction at high speed
                print("Setting direction to REVERSE at HIGH speed.")
                self.set_motor_sequence("high", "reverse")
                for _ in range(5):  # Responsive sleep for 5 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before switching direction again...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)

        except Exception as e:
            print(f"Exception in run_mix_high: {e}")
        finally:
            print("Ending MIX mode.")


    def start_motor(self):
        if not self.running:
            self.running = True
            self.motor_thread = threading.Thread(target=self.motor_operation, daemon=True)
            self.motor_thread.start()

    def stop_motor(self):
        print("Initiating smooth stop...")

        # Signal that no new operations should start; motor is stopping
        self.running = False

        # Begin the smooth stopping process; no new motor operations will start
        target_rpm = 0
        steps = 15
        interval = 0.1  # Adjust the ramping interval as needed
        self.ramp_speed(target_rpm, steps, interval)

        # Wait for any ongoing motor operation to complete
        if self.motor_thread:
            self.motor_thread.join()

        # Reset or update necessary state variables to reflect the motor is stopped
        self.current_speed_rpm = 0
        # Additional commands to safely stop the motor could be included here

        print("Motor smoothly stopped.")
        # Update the state to reflect the motor is safely stopped
        self.state = "SAFE"
        self.stateChanged.emit(self.state)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    motorController = MotorController()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("motorController", motorController)
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


class MotorController(QObject):
    DIR_PIN = 5  # Direction control
    STEP_PIN = 7  # Step control
    EN_PIN = 3    # Enable control
    stateChanged = Signal(str)
    modeChanged = Signal(str)
    speedChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.dir = OutputDevice(self.DIR_PIN)
        self.step = OutputDevice(self.STEP_PIN)
        self.enable = OutputDevice(self.EN_PIN, active_high=False, initial_value=True)
        self.state = "SAFE"
        self.mode = "fwd"
        self.speed = "low"
        self.motor_thread = None
        self.running = False
        self.current_direction = "forward"
        self.current_speed_rpm = 0
        self.steps_per_revolution = 200
        self.in_sequence = False
        self.pulse_timer = None
        self.restart_timer = None

    def enable_motor(self):
        self.enable.off()  # Activates the motor driver by setting EN low

    def disable_motor(self):
        self.enable.on()  # Deactivates the motor driver by setting EN high

    def set_direction(self, direction):
        if direction == "forward":
            self.dir.off()  # Sets direction to forward
        else:
            self.dir.on()  # Sets direction to reverse

    def perform_step(self):
        self.step.on()  # Triggers one step
        time.sleep(0.01)  # Adjust based on your stepping requirements
        self.step.off()
        


    def stop_motor_smoothly(self):
        # Target RPM is 0 for stopping
        target_rpm = 0
        # Define the number of steps and interval for ramping down
        steps = 15
        interval = 0.1  # seconds

        print("Initiating smooth stop...")
        # Use ramp_speed to decrease the speed to 0
        self.ramp_speed(target_rpm, steps, interval)

        # After ramping down to 0, ensure the motor is completely stopped
        # and perform any additional logic needed to safely stop the motor
        # This could involve sending a specific stop command to your motor controller,
        # if required, beyond just reducing the speed to zero.
        print("Motor smoothly stopped.")
        # Reset or update any necessary state variables here
        self.current_speed_rpm = 0
        # If you have a specific motor stop command or need to reset the driver state, do it here
        # e.g., self.send_motor_stop_command()

        # Optionally, update the state to reflect the motor is stopped
        self.state = "SAFE"
        self.stateChanged.emit(self.state)






    def set_motor_sequence(self, target_speed, direction, duration=None):
        self.speeds_rpm = {"low": 500, "mid": 1000, "high": 1500}
        self.steps_per_revolution = 200
        self.ramp_steps = 15
        self.ramp_interval = 0.1

        if target_speed in self.speeds_rpm:
            target_rpm = self.speeds_rpm[target_speed]

            if self.current_direction != direction:
                # Ramp down to 0 first if changing direction
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                self.current_direction = direction

            # Ramp to the target speed
            self.ramp_speed(target_rpm, self.ramp_steps, self.ramp_interval)

            # If a duration is specified, use a timer to stop or change speed later
            # This part is simplified as the main looping logic is now handled by the pulse_pattern method
            if duration is not None:
                threading.Timer(duration, lambda: self.ramp_speed(0, self.ramp_steps, self.ramp_interval)).start()
        else:
            print(f"Invalid motor sequence settings: speed={target_speed}, direction={direction}")





   def ramp_speed(self, target_rpm, steps, interval):
    for _ in range(steps):
        if not self.running:
            break
        self.perform_step()  # Perform a single step per iteration
        time.sleep(interval)  # Delay between steps

    current_rpm = self.current_speed_rpm
    rpm_step = (target_rpm - current_rpm) / steps
    target_reached = False

    for _ in range(steps):
        if not target_reached:
            current_rpm += rpm_step
            current_rpm = round(current_rpm)
            self.current_speed_rpm = current_rpm
            steps_per_second = round(current_rpm * self.steps_per_revolution / 60)
            print(f"Adjusting speed: {current_rpm} RPM ({steps_per_second} steps/sec)")
            time.sleep(interval)

        if abs(self.current_speed_rpm - target_rpm) <= abs(rpm_step):
            target_reached = True

    if self.current_speed_rpm != target_rpm:
        self.current_speed_rpm = target_rpm
        steps_per_second = round(target_rpm * self.steps_per_revolution / 60)
        print(f"Final speed adjustment: {target_rpm} RPM ({steps_per_second} steps/sec)")








    @Slot(str)
    def set_state(self, state):
        # Ensure mode and speed are set before starting the motor
        if state == "RUN" or state == "TIMED":
            if self.mode is None or self.speed is None:
                print("Cannot set state to RUN: Mode or speed not set.")
                return  # Early exit if mode or speed are not set
            # Start the motor if mode and speed are set
            if not self.running:  # Check if the motor is not already running
                self.state = state
                self.stateChanged.emit(self.state)
                print(f"State changed to: {self.state}")
                self.start_motor()
        elif state == "SAFE":
            self.state = state
            self.stateChanged.emit(self.state)
            print(f"State changed to: {self.state}")
            self.stop_motor()
        else:
            print(f"Invalid state: {state}")

    @Slot(str)
    def set_mode(self, mode):
        self.mode = mode
        self.modeChanged.emit(self.mode)
        print(f"Mode set to: {self.mode}")

    @Slot(str)
    def set_speed(self, speed):
        self.speed = speed
        self.speedChanged.emit(self.speed)
        print(f"Speed set to: {self.speed}")

    @Slot(str)
    def start_stop_motor(self, motorState):
        if motorState == "run":
            self.set_state("RUN")
        elif motorState == "idle":
            self.set_state("SAFE")

    def motor_operation(self):
        self.running = True
        while self.running:
            operation_method = self.get_operation_method()
            if operation_method:
                operation_method()
            time.sleep(1)  # Use time.sleep

    def get_operation_method(self):
        if self.mode is None or self.speed is None:
            print("Mode or speed not set. Cannot start motor operation.")
            return None
        method_name = f"run_{self.mode.lower()}_{self.speed.lower()}"
        return getattr(self, method_name, None)

    # Define specific motor control methods for each mode and speed combination


    def run_fwd_low(self):
        self.set_motor_sequence("low", "forward", duration=None)
        print("Running FORWARD at LOW speed indefinitely.")


    def run_fwd_mid(self):
        self.set_motor_sequence("mid", "forward", duration=None)
        print("Running FORWARD at MID speed.")

    def run_fwd_high(self):
        self.set_motor_sequence("high", "forward", duration=None)
        print("Running FORWARD at HIGH speed.")

    def run_rwd_low(self):
        self.set_motor_sequence("low", "reverse", duration=None)
        print("Running REVERSE at LOW speed indefinitely.")

    def run_rwd_mid(self):
        self.set_motor_sequence("mid", "reverse", duration=None)
        print("Running REVERSE at MID speed.")

    def run_rwd_high(self):
        self.set_motor_sequence("high", "reverse", duration=None)
        print("Running REVERSE at HIGH speed.")


    def run_pulse_low(self):
        print("Starting continuous PULSE mode: MID for 10 seconds, then LOW for 5 seconds.")
        self.running = True  # Indicate the motor operation has started

        try:
            while self.running:
                # Set to MID speed and wait
                print("Setting speed to MID.")
                self.set_motor_sequence("mid", "forward")  # Set speed without duration
                time.sleep(10)  # Wait for 10 seconds at MID speed
                if not self.running:
                    break  # Exit if the operation was stopped during the MID phase

                # Set to LOW speed and wait
                print("Switching speed to LOW.")
                self.set_motor_sequence("low", "forward")  # Set speed without duration
                time.sleep(5)  # Wait for 5 seconds at LOW speed
                if not self.running:
                    break  # Exit if the operation was stopped during the LOW phase

        except Exception as e:
            print(f"Exception in run_pulse_mid: {e}")
        finally:
            print("Ending PULSE mode.")



    def run_pulse_mid(self):
        print("Starting continuous PULSE mode: MID for 10 seconds, then LOW for 5 seconds.")
        self.running = True  # Indicate the motor operation has started

        try:
            while self.running:
                # Set to MID speed and wait
                print("Setting speed to MID.")
                self.set_motor_sequence("mid", "forward")  # Set speed without duration
                time.sleep(10)   # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the MID phase

                # Set to LOW speed and wait
                print("Switching speed to LOW.")
                self.set_motor_sequence("low", "forward")  # Set speed without duration
                time.sleep(5)   # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the LOW phase

        except Exception as e:
            print(f"Exception in run_pulse_mid: {e}")
        finally:
            print("Ending PULSE mode.")



    def run_pulse_high(self):
        print("Starting continuous PULSE mode: MID for 10 seconds, then LOW for 5 seconds.")
        self.running = True  # Indicate the motor operation has started

        try:
            while self.running:
                # Set to MID speed and wait
                print("Setting speed to MID.")
                self.set_motor_sequence("high", "forward")  # Set speed without duration
                time.sleep(10)  # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the MID phase

                # Set to LOW speed and wait
                print("Switching speed to LOW.")
                self.set_motor_sequence("mid", "forward")  # Set speed without duration
                time.sleep(5)   # Duration
                if not self.running:
                    break  # Exit if the operation was stopped during the LOW phase

        except Exception as e:
            print(f"Exception in run_pulse_mid: {e}")
        finally:
            print("Ending PULSE mode.")



    def run_mix_low(self):
        print("Starting MIX mode at LOW speed, alternating direction.")
        self.running = True  # Ensure the motor operation flag is set

        try:
            while self.running:
                # Set to forward direction at low speed
                print("Setting direction to FORWARD at LOW speed.")
                self.set_motor_sequence("low", "forward")
                # Use a responsive sleep mechanism
                for _ in range(15):  # 30 seconds split into 1-second checks
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                # Decelerate to stop before changing direction, checking for stop command
                print("Decelerating to stop...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                if not self.running:
                    break

                # Set to reverse direction at low speed
                print("Setting direction to REVERSE at LOW speed.")
                self.set_motor_sequence("low", "reverse")
                # Use a responsive sleep mechanism again
                for _ in range(5):  # 5 seconds split into 1-second checks
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                # Decelerate to stop before changing direction again
                print("Decelerating to stop...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)

        except Exception as e:
            print(f"Exception in run_mix_low: {e}")
        finally:
            print("Ending MIX mode.")


    def run_mix_mid(self):
        print("Starting MIX mode at MID speed, alternating direction.")
        self.running = True

        try:
            while self.running:
                # Set to forward direction at mid speed
                print("Setting direction to FORWARD at MID speed.")
                self.set_motor_sequence("mid", "forward")
                for _ in range(15):  # Responsive sleep for 30 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before reversing...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                if not self.running:
                    break

                # Set to reverse direction at mid speed
                print("Setting direction to REVERSE at MID speed.")
                self.set_motor_sequence("mid", "reverse")
                for _ in range(5):  # Responsive sleep for 5 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before switching direction again...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)

        except Exception as e:
            print(f"Exception in run_mix_mid: {e}")
        finally:
            print("Ending MIX mode.")


    def run_mix_high(self):
        print("Starting MIX mode at HIGH speed, alternating direction.")
        self.running = True

        try:
            while self.running:
                # Set to forward direction at high speed
                print("Setting direction to FORWARD at HIGH speed.")
                self.set_motor_sequence("high", "forward")
                for _ in range(15):  # Responsive sleep for 30 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before reversing...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)
                if not self.running:
                    break

                # Set to reverse direction at high speed
                print("Setting direction to REVERSE at HIGH speed.")
                self.set_motor_sequence("high", "reverse")
                for _ in range(5):  # Responsive sleep for 5 seconds
                    if not self.running:
                        break
                    time.sleep(1)

                if not self.running:
                    break

                print("Decelerating to stop before switching direction again...")
                self.ramp_speed(0, self.ramp_steps, self.ramp_interval)

        except Exception as e:
            print(f"Exception in run_mix_high: {e}")
        finally:
            print("Ending MIX mode.")


    def start_motor(self):
        if not self.running:
            self.enable_motor()
            self.running = True
            self.motor_thread = threading.Thread(target=self.motor_operation, daemon=True)
            self.motor_thread.start()

    def stop_motor(self):
        self.running = False
        print("Initiating smooth stop...")

        # Signal that no new operations should start; motor is stopping
        self.running = False

        # Begin the smooth stopping process; no new motor operations will start
        target_rpm = 0
        steps = 15
        interval = 0.1  # Adjust the ramping interval as needed
        self.ramp_speed(target_rpm, steps, interval)

        # Wait for any ongoing motor operation to complete
        if self.motor_thread:
            self.motor_thread.join()

        # Reset or update necessary state variables to reflect the motor is stopped
        self.current_speed_rpm = 0
        # Additional commands to safely stop the motor could be included here

        print("Motor smoothly stopped.")
        # Update the state to reflect the motor is safely stopped
        self.state = "SAFE"
        self.stateChanged.emit(self.state)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    motorController = MotorController()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("motorController", motorController)
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())

