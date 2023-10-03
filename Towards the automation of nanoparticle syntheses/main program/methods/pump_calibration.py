"""
This code is setup for a calibration run on the machine to calibrate the pump which is used.
It is only made to calibrate a single pump

"""
# Necessary imports
from GUI_functions.method_functions import start_sequence, end_sequence, move_to
from pump_classes.valvepump_noairflush_arduino import ValvePump
from settings import settings
experiment_data = settings.experiment_data
pump_objects = settings.pump_objects

# 1 ml pump standard values
#a:0.3462
#b:-0.0127

# Create the pump object and load it
test_pump = [ValvePump(extruder_number=2, syringe_size=5, gantry_position=0,
                             a_speed=1.3, b_speed=0.3199, a=1.2512, b=-0.1395, speed=1, viscous=1)]

# a:1.2512
# b:-0.1395

start_sequence(test_pump)


for index, experiment_data in experiment_data.iterrows():
    move_to(z=settings.safety_height)
    # Start by moving to the vial
    x = experiment_data.loc["x-coordinate"]
    y = experiment_data.loc["y-coordinate"]
    print("move to " + index + ": X" + str(x) + " Y" + str(y))
    move_to(x, y)
    pump_signal = experiment_data.loc["Solution {}".format(3)]
    test_pump[0].dose(float(pump_signal), raw_signal=True)



move_to(z=settings.safety_height)



# Make sure the pump is emptied, has to happen as a list
end_sequence(test_pump)

