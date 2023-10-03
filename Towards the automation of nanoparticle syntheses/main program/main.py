"""

GUI

"""

# global imports
import tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join

# local imports
from settings import settings
from GUI_functions.file_explorer import read_folder_content
from GUI_functions.protocol_creator import create_volume_entry_table
from GUI_functions.protocol_manager import save_protocol, load_protocol
from GUI_functions.setting_window import change_settings
from GUI_functions.experiment_window import create_experiment_window
from GUI_functions.machine_control import control_window
from GUI_functions.pump_constructor import construct_pump_file

# settings
beaker_height = settings.beaker_height
safety_height = settings.safety_height
vial_height = settings.vial_height
feedrate = settings.feedrate
marlin_speed = settings.default_dosing_speed

# create a list of methods
methods = [f for f in listdir(os.getcwd() + r"\methods") if isfile(join(os.getcwd() + r"\methods", f))]
methods.remove("__init__.py")  # remove the init.py
i = 0
for method in methods:  # make the list more readable
    methods[i] = method.split(".py")[0]
    i += 1


# Function to handle the selection event
def confirm_setup_click():
    # See if anything is missing
    if combobox_method.get() == "":
        messagebox.showerror("Error", "Please select a method")
    elif combobox_number_of_solutions.get() == "":
        messagebox.showerror("Error", "Please select a number of solutions")
    elif combobox_reaction_module.get() == "":
        messagebox.showerror("Error", "Please select a valid layout")
    else:
        # Save the settings
        settings.method = method = combobox_method.get()
        settings.module = module = combobox_reaction_module.get()
        settings.repetition_number = number_of_replications = entry_number_of_replications.get()
        settings.experiment_number = number_of_experiments = entry_number_of_experiments.get()
        settings.pump_number = number_of_solutions = combobox_number_of_solutions.get()

    # get the layout file and load it into the coordinates_df and info(not a fitting name)
    folder_path_modules = os.getcwd()
    folder_path_modules += r"\modules" + "\\" + module + ".txt"
    coordinates_df = pd.read_csv(folder_path_modules, delimiter="\t", skiprows=3)  # get the coord part
    module_settings = np.genfromtxt(folder_path_modules, delimiter="\t", dtype=str, max_rows=3)  # save essential info

    # saves the essential info in int (number of vessels), float (max vol in vessel) and tuple (waste coordinates)
    settings.number_of_reaction_vessels = n_vessel = int(module_settings[1][1])
    volume = module_settings[0][1].split()
    settings.max_volume = V_max = float(volume[0])
    settings.module_waste_coordinates = list(map(int, module_settings[2][1].strip().split(",")))

    # if statement to control the amount of experiments
    if int(number_of_experiments) > n_vessel or int(number_of_experiments) * int(number_of_replications) > n_vessel:
        messagebox.showerror("Error", "Too many experiments or replicates")
        return

    create_volume_entry_table(number_of_solutions=int(number_of_solutions), number_of_experiments=int(number_of_experiments),
                              n_repetitions=int(number_of_replications),
                              window=window, coord_df=coordinates_df)


def choose_protocol():
    # Get entire file path + file name
    protocol_file_path = tkinter.filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if protocol_file_path:
        # Extract the file name from the full file path
        file_name = os.path.basename(protocol_file_path)
        # Update the entry widget with the file name
        entry_loaded_protocol_name.set(file_name.split(".")[0])
        settings.protocol_name = file_name.split(".")[0]
        load_protocol(protocol=protocol_file_path)


# Create the main window
window = tk.Tk()
window.title("ASM protocol creator")
# Set GUI stuff width
box_width = 20
entry_width = 23
init_col = 0
create_col = 5

# Labels declaration and placement
label_create_protocol = tk.Label(window, text="Create new protocol")  # create protocol button declarations
label_create_protocol.grid(row=0, column=init_col, padx=10, pady=0, sticky="w")
button_create_protocol = tk.Button(window, text="Create Protocol", width=box_width, height=5,
                                   command=lambda: [combobox_method.config(state="normal"),
                                                    combobox_number_of_solutions.config(state="normal"),
                                                    combobox_reaction_module.config(state="normal"),
                                                    entry_number_of_replications.config(state="normal"),
                                                    entry_number_of_experiments.config(state="normal"),
                                                    button_confirm_setup.config(state="normal")])
button_create_protocol.grid(row=1, column=init_col, padx=10, pady=0, rowspan=3)

label_load_protocol = tk.Label(window, text="Load existing protocol")  # load protocol .txt file
label_load_protocol.grid(row=3, column=create_col + 1, padx=10, pady=(10, 0), sticky="w")
button_load_protocol = tk.Button(window, text="Load Protocol", command=choose_protocol, width=box_width)
button_load_protocol.grid(row=4, column=create_col + 1, padx=10, pady=0)

label_method = tk.Label(window, text="Dosing Method")  # combobox to hold the various dosing methods
label_method.grid(row=0, column=create_col, padx=10, pady=0, sticky="w")
combobox_method = ttk.Combobox(window, values=methods, width=box_width,
                               state="disabled")
combobox_method.grid(row=1, column=create_col, padx=10, pady=0, sticky="w")
combobox_method.current(0)

label_number_of_solutions = tk.Label(window, text="Number of solutions")  # combobox to hold the number of solutions
label_number_of_solutions.grid(row=2, column=create_col, padx=10, pady=(10, 0), sticky="w")
combobox_number_of_solutions = ttk.Combobox(window, values=["1", "2", "3", "4", "5"], width=box_width, state="disabled")
combobox_number_of_solutions.grid(row=3, column=create_col, padx=10, pady=0, sticky="w")
combobox_number_of_solutions.current(0)

label_reaction_module = tk.Label(window, text="Reaction module")  # combobox to hold the reaction modules
label_reaction_module.grid(row=4, column=create_col, padx=10, pady=(10, 0), sticky="w")
combobox_reaction_module = ttk.Combobox(window, values=read_folder_content("modules"),
                                        width=box_width, state="disabled")
combobox_reaction_module.grid(row=5, column=create_col, padx=10, pady=0, sticky="w")
combobox_reaction_module.current(0)

# entry field to write number of replications
label_number_of_replications = tk.Label(window, text="Number of replicates")
label_number_of_replications.grid(row=6, column=create_col, padx=10, pady=(10, 0), sticky="w")
entry_number_of_replications = tk.Entry(window, width=entry_width, state="disabled")
entry_number_of_replications.grid(row=7, column=create_col, padx=10, pady=0, sticky="w")

label_number_of_experiments = tk.Label(window, text="Number of experiments")  # entry to write number of experiments
label_number_of_experiments.grid(row=8, column=create_col, padx=10, pady=(10, 0), sticky="w")
entry_number_of_experiments = tk.Entry(window, width=entry_width, state="disabled")
entry_number_of_experiments.grid(row=9, column=create_col, padx=10, pady=0, sticky="w")

label_save_protocol = tk.Label(window, text="Protocol name")  # save the created protocol as .txt in protocol folder
label_save_protocol.grid(row=0, column=create_col + 1, padx=10, pady=(10, 0), sticky="w")
button_save_protocol = tk.Button(window, text="Save Protocol",
                                 command=lambda: [save_protocol(protocol_name=entry_protocol_name)],
                                 width=box_width-8, state="disabled")
button_save_protocol.grid(row=2, column=create_col + 1, padx=0, pady=0)
entry_protocol_name = tk.Entry(window, width=entry_width, state="disabled")  # entry to write the protocol name
entry_protocol_name.grid(row=1, column=create_col + 1, padx=10, pady=0, sticky="w")

# Button for updating the ASM settings
button_settings = tk.Button(window, text="Machine settings", command=lambda: [change_settings(window=window)],
                            width=box_width)
button_settings.grid(row=7, column=init_col, padx=10, pady=0)

# Button for creating a new pump
button_pump_creation = tk.Button(window, text="Create new pump type", command=construct_pump_file, width=box_width)
button_pump_creation.grid(row=5, column=init_col, padx=10, pady=0)

# Button for confirming the experiment setup from the GUI main window
button_confirm_setup = tk.Button(window, text="Confirm Setup",
                                 command=lambda: [confirm_setup_click(),
                                                  button_save_protocol.config(state="normal"),
                                                  button_initiate_experiment.config(state="normal"),
                                                  entry_protocol_name.config(state="normal")],
                                 width=box_width-8, state="disabled")
button_confirm_setup.grid(row=12, column=create_col, padx=0, pady=10)

# Button for initiating the experiment from the chosen protocol file
button_initiate_experiment = tk.Button(window, text="Initiate experiment", width=box_width,
                                       command=lambda: [create_experiment_window(window=window)])
button_initiate_experiment.grid(row=7, column=create_col + 1, padx=10)

# Button for controlling the machine with buttons
button_machine_control = tk.Button(window, text="Control machine", width=box_width,
                                   command=lambda: control_window(window))
button_machine_control.grid(row=9, column=init_col, padx=10)

# Entry holding the protocol name after loading the protocol
entry_loaded_protocol_name = tk.StringVar()  # variable to hold the loaded protocol name
entry_load_protocol = tk.Entry(window, textvariable=entry_loaded_protocol_name, state="readonly", width=entry_width)
entry_load_protocol.grid(row=5, column=create_col + 1, padx=10, pady=0)

# Run the main event loop
window.mainloop()
