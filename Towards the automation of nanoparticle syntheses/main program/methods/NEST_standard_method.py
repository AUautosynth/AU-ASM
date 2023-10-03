"""
This is a template to create your own methods. The GUI handles creation of the dataset and the pump objects.
There is the necessary imports which gives the needed functions to handle moveing, and dosing.

"""
# Necessary imports
from GUI_functions.method_functions import start_sequence, end_sequence, move_to
from settings import settings
import time

print("Hey")

experiment_data = settings.experiment_data
pump_objects = settings.pump_objects

experiment_start = time.time()

start_sequence(prime=[pump_objects[0], pump_objects[1], pump_objects[2]])

# dose the MQ water, Base and ROH first
for index, current_experiment in experiment_data.iterrows():
    x = current_experiment.loc["x-coordinate"]
    y = current_experiment.loc["y-coordinate"]
    move_to(x, y)
    time.sleep(2)
    i = 1
    for pump in pump_objects:
        if i == 4:
            continue
        volume = float(current_experiment.loc["Solution {}".format(i)])
        i += 1
        print(volume, type(volume))
        if volume == 0:
            continue
        pump.dose(volume)

# end timer
experiment_end = time.time()
time_taken = experiment_end-experiment_start
print("Time taken for experiment prep: " + str(time_taken))



# wait for user input to dose the gold
input("Ready to dose the the gold :)")

# new timer
experiment_start = time.time()

# dose the GOLD!

pump_objects[3].prime()

for index, current_experiment in experiment_data.iterrows():
    # Start by moving to the vial
    x = current_experiment.loc["x-coordinate"]
    y = current_experiment.loc["y-coordinate"]
    # start_vial_timer = time.time() - start
    move_to(x, y)
    # Dose every solution starting from the first
    volume = float(current_experiment.loc["Solution 4"])
    if volume == 0:
        continue
    pump_objects[3].dose(volume)

end_sequence(unprime=pump_objects)

# end timer
experiment_end = time.time()
time_taken = experiment_end-experiment_start
print("Time taken for gold dosing: " + str(time_taken))
