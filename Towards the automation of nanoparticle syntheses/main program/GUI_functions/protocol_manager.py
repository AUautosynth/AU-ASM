
# global imports
import tkinter
import pandas as pd
import os
import csv

# local imports
from settings import settings

def save_protocol(protocol_name):
    folder_path = os.getcwd()
    directory = folder_path + r"\saved protocols"
    name = protocol_name.get()
    if os.path.exists(directory + "\\" + name + ".txt"):
        result = tkinter.messagebox.askyesno("Confirmation", "File with same name exists, overwrite?")
        if not result:
            return
    with open(directory + "\\" + name + ".txt", "w") as file:  # write a long list of stuff into the protocol file
        file.write("Dosing Method: " + str(settings.method) + "\n")
        file.write("Reaction module: " + str(settings.module) + "\n")
        file.write("Number of reaction vessels: " + str(settings.number_of_reaction_vessels) + "\n")
        file.write("Max Volume: " + str(settings.max_volume) + "\n")
        file.write("Module waste coordinate: " + str(settings.module_waste_coordinates) + "\n")
        file.write("Beaker height: " + str(settings.beaker_height) + "\n")
        file.write("Safety height: " + str(settings.safety_height) + "\n")
        file.write("Vial height: " + str(settings.vial_height) + "\n")
        file.write("Machine speed: " + str(settings.feedrate) + "\n")
        i = 1
        for information in settings.solution_information:
            file.write("Solution {} info: ".format(i) + information + "\n")
            i += 1
        i = 1
        for speed in settings.pump_speeds:
            file.write("Pump {} speed: ".format(i) + str(speed) + "\n")
            i += 1
        i = 1
        for viscosity in settings.pump_viscosities:
            file.write("Viscous solution {}: ".format(i) + str(viscosity) + "\n")
            i += 1
        i = 1
        for gantry_position in settings.pump_gantry_positions:
            file.write("Gantry position {}: ".format(i) + str(gantry_position) + "\n")
            i += 1
        i = 1
        for trash_coordinate in settings.pump_trash_coordinates:
            trash_float_to_string = [str(coordinate) for coordinate in trash_coordinate]
            trash_list_to_string = ",".join(trash_float_to_string)
            file.write("Waste coordinate {}: ".format(i) + trash_list_to_string + "\n")
            i += 1
        i = 1
        for pump in settings.pump_labels:
            file.write("Pump {}: ".format(i) + str(pump) + "\n")
            i += 1
    experiments = settings.experiment_data.astype(str)
    experiments.to_csv(directory + "\\" + name + ".txt", mode="a", sep="\t", index=True)
    tkinter.messagebox.showinfo("File saved", "Protocol {} successfully saved".format(name))


def load_protocol(protocol):
    # read protocol
    data = []
    with open(protocol, "r") as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            data.append(row)

    index_position = next((i for i, sublist in enumerate(data) if "index" in sublist), None)
    sliced_data = data[index_position + 1:]
    # Determine the number of columns in the "index" sublist
    number_of_columns = len(data[index_position])
    # Pad the sliced data with empty strings if the number of columns does not match
    data_index_after = [row + [""] * (number_of_columns - len(row)) for row in sliced_data]
    # sets the column headers
    experimental_df = pd.DataFrame(data_index_after, columns=[data[index_position]])
    experimental_df = experimental_df.astype(str)

    experimental_df.set_index("index", inplace=True)  # Sets the Experiment n column as the index for rows.
    experimental_df.index = [str(index[0]).strip("(), ") for index in experimental_df.index]  # changes the fucking tuple index
    # to the correct string format
    experimental_df = experimental_df.apply(pd.to_numeric, errors='coerce')
    # This firstly fixes the tuple index issue in the columns.
    # Secondly, it changes the columns from a tuple with a single
    # entry to a string, as it is supposed to be.
    experimental_df.columns = experimental_df.columns.to_flat_index()
    for index, column in enumerate(experimental_df.columns):
        experimental_df.rename(columns={column: column[0]}, inplace=True)

    data_index_before = data[:index_position]  # get all the information posted above the vial information
    # save all the data in accessible variables
    separated_data = [row[0].split(":") for row in data_index_before]
    settings.method = separated_data[0][1][1:] + ".py"
    settings.module = separated_data[1][1]
    settings.number_of_reaction_vessels = float(separated_data[2][1])
    settings.max_volume = float(separated_data[3][1])
    settings.module_waste_coordinates = []
    for coordinate in separated_data[4][1][2:-1].split(", "):
        settings.module_waste_coordinates.append(float(coordinate))
    settings.beaker_height = float(separated_data[5][1])
    settings.safety_height = float(separated_data[6][1])
    settings.vial_height = float(separated_data[7][1])
    settings.feedrate = float(separated_data[8][1])
    # clear the pump lists for information, since the loading appends and don't overwrite
    settings.pump_gantry_positions = []
    settings.pump_labels = []
    settings.pump_speeds = []
    settings.pump_viscosities = []
    settings.solution_information = []
    settings.pump_trash_coordinates = []
    for row in separated_data[9:]:
        print(row)
        if "info" in row[0]:
            settings.solution_information.append(row[1][1:])
        if "Pump" and "speed" in row[0]:
            settings.pump_speeds.append(row[1][1:])
        elif "Viscous" in row[0]:
            settings.pump_viscosities.append(row[1][1:])
        elif "Pump" in row[0]:
            settings.pump_labels.append(row[1][1:])
        elif "Gantry position" in row[0]:
            settings.pump_gantry_positions.append(int(row[1][1:]))
        elif "Waste coordinate" in row[0]:
            waste_coordinate = row[1].replace(" ", "").split(",")
            waste_coordinate = [float(coordinate) for coordinate in waste_coordinate]
            settings.pump_trash_coordinates.append(waste_coordinate)
    settings.experiment_data = experimental_df