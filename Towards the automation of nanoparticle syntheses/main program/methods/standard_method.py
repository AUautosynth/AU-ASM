# Necessary imports
from GUI_functions.method_functions import start_sequence, end_sequence, move_to
from settings import settings
import time
import math
experiment_data = settings.experiment_data
pump_objects = settings.pump_objects

experiment_timer = time.time()


start_sequence(prime=pump_objects)

print("Heyo")

priming_done = time.time()
print("Priming took: " + str(priming_done-experiment_timer) + " s")

for index, current_experiment in experiment_data.iterrows():
    # Start by moving to the vial
    x = current_experiment.loc["x-coordinate"]
    y = current_experiment.loc["y-coordinate"]
    print("move to " + str(index) + ": X" + str(x) + " Y" + str(y))
    # start_vial_timer = time.time() - start
    move_to(x, y)
    # Dose every solution starting from the first
    i = 1
    for pump in pump_objects:
        volume = float(current_experiment.loc["Solution {}".format(i)])
        i += 1
        print(volume, type(volume))
        if volume == 0 or math.isnan(volume):
            continue
        pump.dose(volume)

    move_to(z=settings.safety_height)

dosing_done = time.time()
print("Dosing took: " + str(dosing_done-experiment_timer) + " s")

end_sequence(unprime=pump_objects)
print("Everything took: " + str(time.time()-experiment_timer) + " s")

