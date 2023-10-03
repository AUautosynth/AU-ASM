"""
This is a cleaning method which should be used to clean the pumps.


"""
from GUI_functions.method_functions import start_sequence, end_sequence
from settings import settings

pump_objects = settings.pump_objects

start_sequence(prime=pump_objects)
for i in range(5):
    for pump in pump_objects:
        pump.dose(volume=7, dosing_height=settings.Z)

end_sequence(unprime=pump_objects)



