"""
Making a way to automate the speed calculation of the pump, which is very important for the custom-timed protocol to
work properly.

"""

# Necessary imports
from GUI_functions.method_functions import start_sequence, end_sequence, move_to
from settings import settings
experiment_data = settings.experiment_data
pump_objects = settings.pump_objects



# Custom imports
import time
from pump_classes import valvepump_noairflush_arduino



# how do we proceed with making sure that we take the correct time?

# Start the printer
start_sequence(comport='COM5')

# Create the pump object and load it
Micro_pump = valvepump_noairflush_arduino.ValvePump(extruder_number=3, syringe_size=1, gantry_position=0,
                                                    a_speed=0, b_speed=0, a=0, b=0, speed=5)

# Load the execel data
experiment_data

time_results = []
i = 1
for index, experiment_data in experiment_data.iterrows():

    # prepare pump
    print("Pump is being prepared, please wait...\n")
    volume = experiment_data.loc["Volume Solution {}".format(1)]
    Micro_pump.load(volume, dynamic_timer=True, raw_signal=True, flush=False, speed=100)

    input("Press enter to start the timer")
    time_start = time.perf_counter()

    # send the pump signal to unload the pump
    Micro_pump.unload(sleep=False, speed=20*i)

    input("Press enter to stop the timer")
    time_end = time.perf_counter()

    time_taken = time_end-time_start
    time_results.append(time_taken)
    i += 1
    if i == 6:
        i = 1

move_to(z=settings.safety_height)

print(time_results)


# Make sure the pump is emptied, has to happen as a list
end_sequence()




