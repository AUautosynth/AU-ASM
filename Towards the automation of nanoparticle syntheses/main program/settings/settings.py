"""
This contains the settings for the ASM
excel intepretor rewrites these variables

"""
# Standard imports

# Local imports
gantry_increment_distance = 11.5  # Offset between gantry positions
liquid_specific_sleep = 7  # Time it takes for a liquid to settle within the pump.  For more viscious liquids, it needs to be higher.
module_waste_coordinates = [180, 180]
beaker_height = 5
safety_height = 10
vial_height = 3
feedrate = 50
default_dosing_speed = 1.7
comport = None
protocol_name = None

# These are used for the machine functions
X = Y = Z = serial_connection = machine_board = comport = None

# These are needed to run an experiment
experiment_data = pump_objects = None

# These are needed to construct and organize an experiment
repetition_number = experiment_number = max_volume = number_of_reaction_vessels = module = method = None
pump_speeds = []
pump_viscosities = []
solution_information = []
pump_trash_coordinates = []
pump_labels = []
pump_gantry_positions = []


def update_settings(new_settings):
    global beaker_height, safety_height, vial_height, feedrate
    beaker_height = new_settings["beaker_height"]
    safety_height = new_settings["safety_height"]
    vial_height = new_settings["vial_height"]
    feedrate = new_settings["feedrate"]


def configure_printer(config_data):
    global X, Y, Z, serial_connection
    X = config_data["Z"]
    Y = config_data["Y"]
    Z = config_data["Z"]
    serial_connection = config_data["serial_connection"]

