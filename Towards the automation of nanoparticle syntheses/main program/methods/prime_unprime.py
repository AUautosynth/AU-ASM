# Necessary imports
from library.machine_functions import start_sequence, end_sequence, move_to
from settings import settings
import time
experiment_data = settings.experiment_data
pump_objects = settings.pump_objects

experiment_timer = time.time()

start_sequence(prime=pump_objects)

priming_done = time.time()
print("Priming took: " + str(priming_done-experiment_timer) + " s")

end_sequence(unprime=pump_objects)
print("Everything took: " + str(time.time()-experiment_timer) + " s")

