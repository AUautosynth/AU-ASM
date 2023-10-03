"""
This class is for constructing valve pump_classes. Important note is the orientation
of the NC and NO gate on the valves, which should be handled outside the code.
Follow the general valve pump guidelines.

The marlin starting speed for the pumps should be declared in the start_up sequence



"""

# Standard imports
import time

# Local imports
from GUI_functions.method_functions import move_to, move_relative_to, shake
from settings import settings


class ValvePump:
    # Instance attributes for the pump to have the correct settings, a pump need all 8 to work
    # The valve pump is the default pump
    def __init__(self, extruder_number, syringe_size, gantry_position, a_speed, b_speed, a, b,
                 speed, viscous=0, waste_coordinates=settings.module_waste_coordinates):
        self.type = "Valve pump"
        self.extruder_number = extruder_number
        self.syringe_size = float(syringe_size)
        self.gantry_position = gantry_position
        self.a_speed = float(a_speed)
        self.b_speed = float(b_speed)
        self.a = float(a)
        self.b = float(b)
        self.speed = float(speed)
        self.waste_coordinates = waste_coordinates
        # calculate the needed pump signal to fill the tubing. Right now the tubing is 0.5 ml

        # ptfe tubing with ID 0.75 mm, ~50 cm = 0.22 ml volume
        inlet_tubing_volume = 0.5
        outlet_tubing_volume = 0.35

        # there also needs to be a slight leftover of solution in the syringe.
        leftover_volume = 0.2

        self.thicc_factor = 1.3
        if int(viscous) == 1:
            self.thicc_factor = 3.5
            inlet_tubing_volume += 0.6
            outlet_tubing_volume += 0.5

        self.first_priming_signal = ((inlet_tubing_volume + leftover_volume) - self.b) / self.a
        self.second_priming_signal = ((outlet_tubing_volume + leftover_volume) - self.b) / self.a
        self.third_priming_signal = (leftover_volume - self.b) / self.a
        pass

    # Method for dosing a certain volume.
    def dose(self, volume, dynamic_timer=True, raw_signal=False, dosing_height=settings.vial_height, time_calculation=False):

        time_sum = 0
        # use the correct gantry position
        vial_position = settings.X  # save the vial position
        sleep_time = move_to(x=settings.X + (-self.gantry_position * settings.gantry_increment_distance), time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time

        # Then move down to the vial
        sleep_time = move_to(z=dosing_height, time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time
        # Ensure that the volume comes in as an actual number

        volume = float(volume)
        print("dosing " + str(volume), "ml from pump", str(self.extruder_number + 1))

        # Load the dosage
        sleep_time = self.load(volume, dynamic_timer=dynamic_timer, raw_signal=raw_signal, time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time

        # Unload the dosage
        sleep_time = self.unload(volume, dynamic_timer=dynamic_timer, raw_signal=raw_signal, time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time


        # move to central gantry position
        sleep_time = move_to(x=vial_position, time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time


        sleep_time = 1
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)  # wait a single second before flushing the buffer
            settings.serial_connection.reset_output_buffer()
            settings.serial_connection.reset_input_buffer()

        return time_sum
    # Needs to be called for all pump_classes, so they have liquids in them

    def load(self, volume, dynamic_timer=True, raw_signal=False, time_calculation=False):
        time_sum = 0

        # Calculate the signal value
        if raw_signal:
            pump_signal = volume
        elif not raw_signal:
            pump_signal = (volume - self.b) / self.a

        if not time_calculation:
            # Choose the correct extruder
            settings.serial_connection.write("T{} \n".format(self.extruder_number).encode())

            # Set the speed at which the pump should dose the liquid
            settings.serial_connection.write("M203 E{} \n".format((settings.default_dosing_speed / 100) * self.speed).encode())

            # Fill the pump with the liquid
            settings.serial_connection.write("G1 E-{} \n".format(pump_signal).encode())

        if dynamic_timer:
            sleep_time = ((self.a_speed * pump_signal + self.b_speed) * (50 / self.speed)) * self.thicc_factor
        elif not dynamic_timer:
            sleep_time = 5 * (50 / self.speed)
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)
            # Reset the speed for other dosages
            settings.serial_connection.write("M203 E{} \n".format(settings.default_dosing_speed).encode())


        return time_sum

    def unload(self, volume, dynamic_timer=True, raw_signal=False, time_calculation=False):
        time_sum = 0

        if not time_calculation:
            # Choose the correct extruder
            settings.serial_connection.write("T{} \n".format(self.extruder_number).encode())
            # Change valve state to NC
            settings.serial_connection.write("M104 T{} S100 \n".format(self.extruder_number).encode())
            # Set the speed at which the pump should dose the liquid
            settings.serial_connection.write("M203 E{} \n".format((settings.default_dosing_speed / 100)
                                                                  * self.speed).encode())
            # Make the pump dose the quantity
            settings.serial_connection.write("G1 E0 \n".encode())

        # Calculate the signal value
        if raw_signal:
            pump_signal = volume
        elif not raw_signal:
            pump_signal = (volume - self.b) / self.a

        if dynamic_timer:
            sleep_time = ((self.a_speed * (pump_signal) + self.b_speed) * (50 / self.speed)) * self.thicc_factor
        elif not dynamic_timer:
            sleep_time = 15 * (50 / self.speed)
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)
            # Change the valve state to NO
            settings.serial_connection.write("M104 T{} S0 \n".format(self.extruder_number).encode())
            # Reset the speed for other dosages
            settings.serial_connection.write("M203 E{} \n".format(settings.default_dosing_speed).encode())

        # Move up and down 6 times
        sleep_time = shake(time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time

        return time_sum

    def prime(self, time_calculation=False):
        time_sum = 0
        if not time_calculation:
            # Choose the correct extruder
            settings.serial_connection.write("T{} \n".format(self.extruder_number).encode())
            # Sets current position to 'zero'. Make sure syringe is completely plunged
            settings.serial_connection.write("G92 E0 \n".encode())

        sleep_time = move_to(x=self.waste_coordinates[0], y=self.waste_coordinates[1], time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time
        sleep_time = move_to(z=settings.beaker_height, time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time
        # use the correct gantry position
        sleep_time = move_relative_to(x=-self.gantry_position * settings.gantry_increment_distance, time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time

        if not time_calculation:
            print("Loading pump {}".format(self.extruder_number + 1))
            # set the speed
            settings.serial_connection.write("M203 E{} \n".format((settings.default_dosing_speed / 100)
                                                                  * self.speed).encode())
            # prime the first volume
            settings.serial_connection.write("G1 E-{} \n".format(self.first_priming_signal).encode())

        sleep_time = ((self.a_speed * self.first_priming_signal + self.b_speed)
                      * (50 / self.speed)) * self.thicc_factor
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)
            # Control valve with temp output
            settings.serial_connection.write("M104 T{} S100 \n".format(self.extruder_number).encode())
            # dose the first priming volume
            settings.serial_connection.write("G1 E0 \n".encode())

        sleep_time = ((self.a_speed * self.first_priming_signal + self.b_speed) * (
                    50 / self.speed)) * self.thicc_factor
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)
            # Control valve with temp output
            settings.serial_connection.write("M104 T{} S0 \n".format(self.extruder_number).encode())
            # prime the second priming volume
            settings.serial_connection.write("G1 E-{} \n".format(self.second_priming_signal).encode())

        sleep_time = ((self.a_speed * self.second_priming_signal + self.b_speed) * (
                    50 / self.speed)) * self.thicc_factor
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)
            # Control valve with temp output
            settings.serial_connection.write("M104 T{} S100 \n".format(self.extruder_number).encode())
            # dose the third priming volume
            settings.serial_connection.write("G1 E-{} \n".format(self.third_priming_signal).encode())

        sleep_time = ((self.a_speed * (self.second_priming_signal - self.third_priming_signal) + self.b_speed) *
                      (50 / self.speed)) * self.thicc_factor
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)
            # Control valve with temp output
            settings.serial_connection.write("M104 T{} S0 \n".format(self.extruder_number).encode())
            settings.serial_connection.write("G92 E0 \n".encode())
            # reset the speed
            settings.serial_connection.write("M203 E{} \n".format(settings.default_dosing_speed).encode())

        # Move side to side 6 times
        sleep_time = shake(time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time

        print("Pump {} is now ready to be used".format(self.extruder_number + 1))

        # reset gantry position
        sleep_time = move_relative_to(x=self.gantry_position
                                        * settings.gantry_increment_distance, time_calculation=time_calculation)
        if sleep_time:
            time_sum += sleep_time

        return time_sum


    def unprime(self, time_calculation=False):
        time_sum = 0
        pump_signal = self.first_priming_signal

        if not time_calculation:
            # Choose the correct extruder
            settings.serial_connection.write("T{} \n".format(self.extruder_number).encode())
            print("unloading pump {}".format(self.extruder_number))
            # Turn on to the dose end
            settings.serial_connection.write("M104 T{} S100 \n".format(self.extruder_number).encode())
            # suck in air to empty the tube
            settings.serial_connection.write("M203 E{} \n".format((settings.default_dosing_speed / 100)
                                                                  * self.speed).encode())
            settings.serial_connection.write("G1 E-{} \n".format(pump_signal).encode())

        # sleep timer
        sleep_time = ((self.a_speed * pump_signal + self.b_speed) * (50 / self.speed)) * self.thicc_factor
        if sleep_time:
            time_sum += sleep_time

        pump_signal = self.third_priming_signal
        if not time_calculation:
            time.sleep(sleep_time)
            # turn off to the solvent end
            settings.serial_connection.write("M104 T{} S0 \n".format(self.extruder_number).encode())
            # push everything down to the solvent flask
            settings.serial_connection.write("G1 E{} \n".format(pump_signal).encode())

        # sleep timer
        sleep_time = ((self.a_speed * (pump_signal + self.first_priming_signal) + self.b_speed) * (50 / self.speed)) * self.thicc_factor
        time_sum += sleep_time
        if not time_calculation:
            time.sleep(sleep_time)

        # do it one more time
        # Turn on to the dose end

        sleep_time = 2
        time_sum += sleep_time
        if not time_calculation:
            time.sleep(sleep_time)  # needs wait time apparently
            settings.serial_connection.write("M104 T{} S100 \n".format(self.extruder_number).encode())

        # suck in air to empty the tube
        pump_signal = self.first_priming_signal
        if not time_calculation:
            settings.serial_connection.write("G1 E-{} \n".format(pump_signal).encode())

        # sleep timer
        sleep_time = ((self.a_speed * (pump_signal + self.third_priming_signal) + self.b_speed) * (50 / self.speed)) * self.thicc_factor
        time_sum += sleep_time

        pump_signal = self.third_priming_signal
        if not time_calculation:
            time.sleep(sleep_time)
            # turn off to the solvent end
            settings.serial_connection.write("M104 T{} S0 \n".format(self.extruder_number).encode())
            # push everything down to the solvent flask
            settings.serial_connection.write("G1 E{} \n".format(pump_signal).encode())

        # sleep timer
        sleep_time = ((self.a_speed * (pump_signal + self.first_priming_signal) + self.b_speed) * (50 / self.speed)) * self.thicc_factor
        time_sum += sleep_time

        if not time_calculation:
            time.sleep(sleep_time)

            # turn the speed back
            settings.serial_connection.write("M203 E{} \n".format(settings.default_dosing_speed).encode())

        return time_sum



