"""
These functions handle the construction of experiments

This module will be the one handling the construction, saving and loading of templates, aswell as handling the global
construction parameters, setup_data, pump_objects and experiment_data

"""

# global imports
import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import csv

# local imports
from GUI_functions.file_explorer import read_folder_content
from settings import settings

# not sure if necessary
list_combobox_pumps = list_entry_speed = list_check_viscous = []


def create_volume_entry_table(number_of_solutions, number_of_experiments, n_repetitions, window, coord_df):
    global list_combobox_pumps, list_entry_speed, list_check_viscous
    module = settings.module

    def save_volume_data():
        volume = []  # a 2D array to contain the values written in the entry widgets
        for row in volume_array:  # iterate through each row in the volume_array
            row_entries = []  # temporary array to hold each row entry
            for entries in row:  # iterate through each entry widget in the row
                entry_value = entries.get()  # get the user input from the entry widgets
                if not entry_value:  # test if the entry widget is kept blank, then fill with 0, else the value
                    row_entries.append(0)
                else:
                    row_entries.append(float(entry_value))
            volume.append(row_entries[0])
        # create the dataframe and rename the rows and columns iteratively
        volume_df = pd.DataFrame(volume)
        for n, row_name in enumerate(volume_df.index):
            new_row_name = f"Experiment {n + 1}"
            volume_df = volume_df.rename(index={row_name: new_row_name})
        for n, column_name in enumerate(volume_df.columns):
            new_column_name = f"Solution {n + 1}"
            volume_df = volume_df.rename(columns={column_name: new_column_name})

        # Fill the pump data into the settings
        for pump in list_combobox_pumps:
            settings.pump_labels.append(pump.get())
        for speed in list_entry_speed:
            settings.pump_speeds.append(float(speed.get()))
        for check in list_check_viscous:
            settings.pump_viscosities.append(check.get())
        for information in list_information:  # solution information
            settings.solution_information.append(information.get())
        for gantry_position in list_combobox_gantry_position:
            settings.pump_gantry_positions.append((int(gantry_position.get())))
        for trash in list_entry_trash:
            trash_coordinate = trash.get().replace(" ", "")
            trash_coordinate = trash_coordinate.split(",")
            j = 0
            for coordinate in trash_coordinate:
                trash_coordinate[j] = float(coordinate)
                j += 1
            settings.pump_trash_coordinates.append(trash_coordinate)
        # check if a prioritised dosing order is chosen
        if var_checkbutton_priority_table.get() == 0:
            repetition_df = None  # clears the repetition_df
            for n in range(n_repetitions):  # iterate through replicates
                repetition_df = pd.concat([repetition_df, volume_df], axis=0)  # save the replicated data in global dataframe
            repetition_df.reset_index(inplace=True)
            repetition_df = pd.concat([repetition_df, coord_df], axis=1)
            repetition_df = repetition_df.set_index(repetition_df.loc[:, "index"])
            repetition_df = repetition_df.drop(["index"], axis=1)
            settings.experiment_data = repetition_df
        elif var_checkbutton_priority_table.get() == 1:
            priority_table(number_of_solution=number_of_solutions,
                           number_of_experiments=number_of_experiments,
                           n_repetitions=n_repetitions,
                           window=window,
                           coord_df=coord_df, vol_df=volume_df)

    # set a volume_window up for the entry of volumes
    volume_window = tk.Toplevel(window)
    # create list of list (array) by going through all experiment in all solutions "_" is a throwaway variable
    volume_array = [[None for _ in range(number_of_solutions)] for _ in range(number_of_experiments)]
    pump_column = 4 + number_of_solutions  # column for shorthand
    # range of lists needed later
    list_information = []
    list_combobox_pumps = []
    list_entry_speed = []
    list_check_viscous = []
    list_entry_trash = []
    list_combobox_gantry_position = []
    # Get the generic waste coordinates from the module text file
    folder_path = os.getcwd()
    with open(folder_path + "\\modules\\" + module + ".txt", "r") as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:  # each row read as tuples
            if "waste coordinates" in row[0]:
                waste = row[1]

    for i in range(number_of_solutions):  # following code sets up widgets that depends on the amount of solutions
        label = tk.Label(volume_window, text="Solution {} [ml]".format(i + 1))  # column headers
        label.grid(row=0, column=2 + i, padx=0, pady=0)

        label = tk.Label(volume_window, text="Pump {}".format(i + 1))  # labels for choosing pump
        label.grid(row=1 + i, column=pump_column, padx=(10, 0), pady=0)
        # drop down menu for the pump types selectable
        combobox_pumps = ttk.Combobox(volume_window, width=20, values=read_folder_content(folder_name="saved pumps"))
        combobox_pumps.grid(row=1 + i, column=pump_column + 1)
        list_combobox_pumps.append(combobox_pumps)  # used to contain the dropdown menu for the

        # entries for selecting the pumps speed
        entry = tk.Entry(volume_window, width=10)
        entry.grid(row=1 + i, column=pump_column + 2)
        entry.insert(0, "5")
        list_entry_speed.append(entry)

        # checkboxes for checking if liquid is highly viscous
        checkbutton_var = tk.IntVar(value=0)
        checkbutton = tk.Checkbutton(volume_window, variable=checkbutton_var)
        checkbutton.grid(row=1 + i, column=pump_column + 3)
        list_check_viscous.append(checkbutton_var)

        # entries for trash coordinates
        entry = tk.Entry(volume_window, width=10)
        entry.grid(row=1 + i, column=pump_column + 4)
        entry.insert(0, waste)
        list_entry_trash.append(entry)

        # combobox for gantry positions
        combobox_gantry_position = ttk.Combobox(volume_window, width=15, values=["-2", "-1", "0", "1", "2"])
        combobox_gantry_position.grid(row=1 + i, column=pump_column + 5)
        combobox_gantry_position.current(2)
        list_combobox_gantry_position.append(combobox_gantry_position)

    for i in range(number_of_experiments):  # loop sets up the entry widgets for volume entry
        # start with labels for each row
        label = tk.Label(volume_window, text="Experiment {}".format(i + 1))
        label.grid(row=2 + i, column=1, padx=0, pady=0, sticky="w")
        for k in range(number_of_solutions):
            # create the entries according to the number of experiments chosen
            if i == 0:  # Create an entry field to allow solution information to be put in
                label = tk.Label(volume_window, text="Solution Information:")
                label.grid(row=1, column=1, padx=0, pady=0)
                entry = tk.Entry(volume_window, width=10)
                entry.grid(row=1, column=2+k, padx=0, pady=0)
                list_information.append(entry)
            volume_entry = tk.Entry(volume_window, width=10)
            volume_entry.grid(row=2 + i, column=2 + k, padx=0, pady=0)
            volume_array[i][k] = volume_entry

    # Labels for pump stuff
    widget_grid_column = 1
    label_pump = tk.Label(volume_window, text="Pumps".format(number_of_solutions + 1))
    label_pump.grid(row=0, column=pump_column + widget_grid_column, padx=0, pady=0)
    widget_grid_column += 1
    label_speed = tk.Label(volume_window, text="Pump speed [%]")
    label_speed.grid(row=0, column=pump_column + widget_grid_column, padx=0, pady=0)
    widget_grid_column += 1
    label_check_viscosity = tk.Label(volume_window, text="Viscous solution?")
    label_check_viscosity.grid(row=0, column=pump_column + widget_grid_column, padx=0, pady=0)
    widget_grid_column += 1
    label_waste = tk.Label(volume_window, text="Waste coordinates [x,y]")
    label_waste.grid(row=0, column=pump_column + widget_grid_column)
    widget_grid_column += 1
    label_gantry_position = tk.Label(volume_window, text="Gantry position")
    label_gantry_position.grid(row=0, column=pump_column + widget_grid_column)
    widget_grid_column += 1

    # Create an option to go to a prioritized table
    var_checkbutton_priority_table = tk.IntVar(value=0)
    checkbutton_priority_table = tk.Checkbutton(volume_window, text="Get a priority table",
                                                variable=var_checkbutton_priority_table)
    checkbutton_priority_table.grid(row=3 + i, column=0, columnspan=3)  # "i" refers to number of experiments loop

    # create a button for saving the volume user input and move on to the next input
    next_table = tk.Button(volume_window, text="Next  >",
                           command=lambda: [save_volume_data(), volume_window.withdraw()])
    next_table.grid(row=0, column=pump_column + widget_grid_column, padx=5, pady=5)


def priority_table(number_of_solution, number_of_experiments, n_repetitions, coord_df, window, vol_df):
    def save_prio_data():
        priority = []
        for row in priority_array:
            row_entries = []  # temp for row values
            for entries in row:
                entry_value = entries.get()  # get the user input from the entry widgets
                if not entry_value:  # test if the widget is kept blank, then fill with 0, else the value
                    row_entries.append(0)
                else:
                    row_entries.append(float(entry_value))
            priority.append(row_entries)
        priority_df = pd.DataFrame(priority)
        # rename rows and columns
        for m, row_name in enumerate(priority_df.index):
            new_row_name = f"Experiment {m + 1}"
            priority_df = priority_df.rename(index={row_name: new_row_name})
        for m, column_name in enumerate(priority_df.columns):
            if m < number_of_solution:  # for priority inputs
                new_column_name = f"Priority Solution {m + 1}"
                priority_df = priority_df.rename(columns={column_name: new_column_name})
            else:  # for timer inputs
                new_column_name = f"Timer Priority {m - number_of_solution + 2}"
                priority_df = priority_df.rename(columns={column_name: new_column_name})
        complete_df = pd.concat([vol_df, priority_df], axis=1)  # combine the volume input and the priority input
        for m in range(n_repetitions - 1):  # iterate through replicates
            complete_df = pd.concat([complete_df, complete_df], axis=0)  # save the replicated data in global dataframe
        complete_df.reset_index(inplace=True)
        complete_df = pd.concat([complete_df, coord_df], axis=1)
        complete_df = complete_df.set_index(complete_df.loc[:, "index"])
        complete_df = complete_df.drop(["index"], axis=1)

        complete_df = complete_df.astype(str)
        settings.experiment_data = complete_df

    # Setup pop up window to fill out priority and timer
    priority_window = tk.Toplevel(window)
    # create an array that holds priority and timer for all solutions (minus one timer for the first solution)
    priority_array = [[None for _ in range(number_of_solution * 2 - 1)] for _ in range(number_of_experiments)]
    # create appropriate headers
    for i in range(number_of_solution):
        label = tk.Label(priority_window, text="Priority Solution {}".format(i + 1))
        label.grid(row=0, column=2 + i, padx=0, pady=0)
        if i != 0:
            label = tk.Label(priority_window, text="Timer Priority {}".format(i + 1))
            label.grid(row=0, column=number_of_solution + i + 1, padx=0, pady=0)
    for i in range(number_of_experiments):
        # start with labels for each row
        label = tk.Label(priority_window, text="Experiment {}".format(i + 1))
        label.grid(row=1 + i, column=1, padx=0, pady=0, sticky="w")
        for k in range(number_of_solution):
            # create the entry widgets according to the number of experiments chosen
            col = tk.Entry(priority_window, width=10)
            col.grid(row=1 + i, column=2 + k, padx=0, pady=0)
            priority_array[i][k] = col
            if k != 0:
                col = tk.Entry(priority_window, width=10)
                col.grid(row=1 + i, column=number_of_solution + k + 1, padx=0, pady=0)
                priority_array[i][number_of_solution + k - 1] = col
    button_next_priority_window = tk.Button(priority_window, text="Next  >",
                                            command=lambda: [save_prio_data(), priority_window.withdraw()])
    button_next_priority_window.grid(row=0, column=number_of_solution * 2 + 1, padx=5, pady=5)



