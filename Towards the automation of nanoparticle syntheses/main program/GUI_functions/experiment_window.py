# imports
import os
import threading
import csv
import tkinter
import re
import sys
import math
import pandas as pd
import serial
import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import serial.tools.list_ports

# local imports
from GUI_functions.file_explorer import save_dataframe
from settings import settings
from methods.test_method import test_method

#
global hour, minute, seconds, time_unit
hour = minute = seconds = time_unit = None
box_width = entry_width = 15
# Timer:

def wait_operator():
    global hour, minute, seconds, time_unit
    # if statement that checks a 0-1 tkinter entry
    # input the start time as a time with PM or AM
    # example format
    # initiation_time = "12:00:00 AM"
    sleep_time = 0

    if "AM" in time_unit or "PM" in time_unit:
        initiation_time = hour + ":" + minute + ":" + seconds + " " + time_unit

        current_time = datetime.now().strftime("%I:%M:%S %p")
        FMT = "%I:%M:%S %p"
        tdelta = datetime.strptime(initiation_time, FMT) - datetime.strptime(current_time, FMT)
        if tdelta.days < 0:
            tdelta = timedelta(
                days=0,
                seconds=tdelta.seconds,
                microseconds=tdelta.microseconds
            )
        sleep_time = tdelta.total_seconds()

    elif time_unit == "From now":
        hour_to_seconds = minute_to_seconds = seconds_to_seconds = 0
        if hour:
            hour_to_seconds = float(hour) * 3600
        if minute:
            minute_to_seconds = float(minute) * 60
        if seconds:
            seconds_to_seconds = float(seconds)
        sleep_time = hour_to_seconds + minute_to_seconds + seconds_to_seconds
    elif time_unit == "Not timed":
        return
    print(f"I sleep for {sleep_time} seconds  (-.-)..zzZZ")
    time.sleep(sleep_time)
    current_time = datetime.now().strftime("%I:%M:%S %p")
    print(f"I have awakened at: {current_time}  (o.o)!!!")


def create_pumps():
    # find out what kind of board it has been connected to. Hard coded Arduino and BTT octo as the two options
    if "Arduino" in settings.machine_board:
        from pump_classes.valvepump_noairflush_arduino import ValvePump
    elif "BTT Octo" in settings.machine_board:
        from pump_classes.valvepump_noairflush_BTT_octo import ValvePump
    else:
        tkinter.messagebox.showerror("Error", "Board not recognized")
        return
    settings.pump_objects = []  # clean the pump_objects
    # This sets the gantry position
    extruder_number = 0
    i = 0
    for pump in settings.pump_labels:
        # read protocol
        folder_path = os.getcwd()
        protocol = folder_path + r"\saved pumps" + "\\" + pump + ".txt"

        data = []
        with open(protocol, "r") as file:
            reader = csv.reader(file, delimiter="\t")
            for row in reader:
                data.append(row[0])
        data_string = ";".join(data)
        pump_dictionary = dict(entry.split(":") for entry in data_string.split(";"))
        pump_speed = settings.pump_speeds[i]
        pump_viscous = settings.pump_viscosities[i]
        pump_gantry_position = settings.pump_gantry_positions[i]
        pump_trash_coordinates = settings.pump_trash_coordinates[i]
        if pump_dictionary["Pump type"] == "Valve pump":
            pump = ValvePump(extruder_number=extruder_number,
                             syringe_size=float(pump_dictionary["Syringe size"]),
                             gantry_position=pump_gantry_position,
                             a_speed=float(pump_dictionary["a_speed"]), b_speed=float(pump_dictionary["b_speed"]),
                             a=float(pump_dictionary["a"]), b=float(pump_dictionary["b"]),
                             speed=float(pump_speed),
                             viscous=float(pump_viscous),
                             waste_coordinates=pump_trash_coordinates)
            settings.pump_objects.append(pump)
            extruder_number += 1
            i += 1


def create_experiment_window(window):
    exp_window = tk.Toplevel(window)  # main window
    exp_window.title("Experiment run")
    grid_frame = tk.Frame(exp_window)  # main sub frame
    # Declaration of variables
    hour_estimation = tkinter.StringVar()
    minute_estimation = tkinter.StringVar()
    second_estimation = tkinter.StringVar()
    # setting the default value as 0
    hour_estimation.set("00")
    minute_estimation.set("00")
    second_estimation.set("00")

    def update_pump(button, window):
        pump_number = int(button["text"][-2])
        pump = settings.pump_objects[pump_number - 1]

        def save_pump():
            pump.gantry_position = int(entry_gantry_position.get())
            pump.extruder_number = int(entry_extruder_number.get())
            waste_coordinates = entry_waste_coord.get()
            waste_coordinates = waste_coordinates.replace("[", "")
            waste_coordinates = waste_coordinates.replace("]", "")
            list_waste_coordinates = [float(waste_coordinates.split(",")[0]), float(waste_coordinates.split(",")[1])]
            pump.waste_coordinates = list_waste_coordinates
            pump.speed = float(entry_pump_dose_speed.get())
            settings.pump_objects[pump_number - 1] = pump
            time_estimation()

        pump_settings_window = tk.Toplevel(window)  # pump settings pop up window
        # labels declaration
        label_settings = tk.Label(pump_settings_window, text="Pump {} settings".format(pump_number))
        label_settings.grid(row=0, column=0, sticky="w")
        label_extruder_number = tk.Label(pump_settings_window, text="Extruder number: ")
        label_extruder_number.grid(row=2, column=0, sticky="w")
        label_gantry_position = tk.Label(pump_settings_window, text="Gantry position: ")
        label_gantry_position.grid(row=3, column=0, sticky="w")
        label_pump_dose_speed = tk.Label(pump_settings_window, text="Dosing speed: ")
        label_pump_dose_speed.grid(row=4, column=0, sticky="w")
        label_waste_coordinates = tk.Label(pump_settings_window, text="Waste coordinates [x,y]: ")
        label_waste_coordinates.grid(row=5, column=0, sticky="w")
        label_pump_dose_speed_unit = tk.Label(pump_settings_window, text="%")
        label_pump_dose_speed_unit.grid(row=4, column=3, sticky="w")

        # entry declaration -> holds the settings
        entry_extruder_number = tk.Entry(pump_settings_window, width=entry_width)
        entry_extruder_number.insert(0, str(pump.extruder_number))
        entry_extruder_number.grid(row=2, column=1)
        entry_gantry_position = tk.Entry(pump_settings_window, width=entry_width)
        entry_gantry_position.insert(0, str(pump.gantry_position))
        entry_gantry_position.grid(row=3, column=1)
        entry_pump_dose_speed = tk.Entry(pump_settings_window, width=entry_width)
        entry_pump_dose_speed.insert(0, str(pump.speed))
        entry_pump_dose_speed.grid(row=4, column=1)
        entry_waste_coord = tk.Entry(pump_settings_window, width=entry_width)
        entry_waste_coord.insert(0, str(pump.waste_coordinates))
        entry_waste_coord.grid(row=5, column=1)

        # Button for saving changes to the pump settings
        save_pump_settings_button = tk.Button(pump_settings_window, text="Save settings", width=32,
                                              command=lambda: [save_pump(), pump_settings_window.destroy()])
        save_pump_settings_button.grid(row=7, column=0, columnspan=2, padx=(0, 10))

    def time_estimation():
        """
        this function is a bit complex and hard to follow. There is also a high chance of needing to fix it in the future
        Firstly, it loads in the method to run as a string. It then checks that string for the time_calculation argument
        which is an argument that can be given to all machine functions. It then adds that argument if it is not there
        and sets it to true. This makes the functions return their sleep_time as a float. That is then continously
        added to the time:sum variable. The complex part of this function is the string modification, since it needs
        to take into account a lot of details and it is probably the easiest code to break of all the ASM code.
        If the code does not work and you want it to estimate your custom method, then please help the function along
        accordingly. Make a time_sum variable at the start of your method and set it to 0. Then write every method
        function and pump function as follows:

        time_sum += function(arg, time_calculation=False)

        This makes it much easier for the time_esitmation function to recognize where it needs to do modifications.
        Another important thing to take into account is if you have made new functions the machine should do. You
        basically need to wrap the operations inside an "if not time_calculation:" statement so that the operation will be
        able to return a time_sum value to the time_estimation function. Do take a look at how it has been written in
        the pump classes as well as method functions

        Good luck using it :)

        :return:
        """

        time_sum = 0
        folder_path = os.getcwd()
        method = settings.method
        if ".py" not in method:
            method = method + ".py"
        with open(folder_path + "\\methods\\" + method) as method_file:
            method_as_string = method_file.read()

        # insert time_calculation into the functions:
        # define the functions to be searched for
        functions_to_look_for = ["start_sequence(", ".dose(", "move_to(", "move_relative_to(", "end_sequence(",
                                 ".prime(",
                                 ".unprime("]
        # iterate through every function type
        time_sum_check = method_as_string.find("time_sum = ")
        for function in functions_to_look_for:

            last_save = 0

            while True:

                function_start = method_as_string.find(function, last_save)

                if function_start == -1:
                    break

                function_end = method_as_string.find(")", function_start) + 1
                # check to see if the string contains the substring "time_calculation"
                function_as_string = method_as_string[function_start:function_end]

                if "time_calculation=" in function_as_string:
                    function_modification = function_as_string.replace("time_calculation=False",
                                                                       "time_calculation=True")

                    method_as_string = method_as_string[:function_start] + function_modification + method_as_string[
                                                                                                       function_end:]
                else:
                    if function == ".prime(" or function == ".unprime(":
                        function_modification = function_as_string.replace(")", "time_calculation=True)")
                    else:
                        function_modification = function_as_string.replace(")", ", time_calculation=True)")
                    if time_sum_check == -1:

                        t = method_as_string[function_start]

                        # need to find if it is a function, needs the time_sum in another place
                        if method_as_string[function_start] == ".":
                            last_new_line = method_as_string.rfind('\n', 0, function_start)
                             # find first not mathcing string
                            first_char_index = re.search(r"[^ ]",
                                                         method_as_string[last_new_line + 1:function_start]).start()
                            char_to_replace = method_as_string[last_new_line + first_char_index - 1]

                            time_sum_insert = method_as_string[
                                              :last_new_line + first_char_index] + char_to_replace + "time_sum += "

                            method_as_string = time_sum_insert + \
                                               method_as_string[last_new_line + first_char_index + 1:function_start] + \
                                               function_modification + \
                                               method_as_string[function_end:]
                        else:
                            method_as_string = method_as_string[
                                               :function_start] + "time_sum += " + function_modification + method_as_string[
                                                                                                           function_end:]
                    else:
                        method_as_string = method_as_string[:function_start] + function_modification + method_as_string[
                                                                                                       function_end:]

                last_save = function_end
        pass

        # run the modified string as a python code.
        variable_dictionary = {}
        exec(f"time_sum=0; " + method_as_string, globals(), variable_dictionary)
        time_sum = variable_dictionary["time_sum"]
        run_minute, run_seconds = divmod(time_sum, 60)
        run_hour, run_minute = divmod(run_minute, 60)
        print("Estimated time: " + str(time_sum))
        hour_estimation.set(str(math.floor(run_hour)))
        minute_estimation.set(str(math.floor(run_minute)))
        second_estimation.set(str(math.floor(run_seconds)))
        exp_window.update()


    def thread_countdown():
        countdown_thread = threading.Thread(target=countdown)
        countdown_thread.start()
    def countdown():
        # Calculate everything into seconds
        temp = int(hour_estimation.get()) * 3600 + int(minute_estimation.get()) * 60 + int(second_estimation.get())
        while temp > -1:

            # divmod(firstvalue = temp//60, secondvalue = temp%60)
            mins, secs = divmod(temp, 60)

            # Converting the input entered in mins or secs to hours,
            # mins ,secs(input = 110 min --> 120*60 = 6600 => 1hr :
            # 50min: 0sec)
            hours = 0
            if mins > 60:
                # divmod(firstvalue = temp//60, secondvalue
                # = temp%60)
                hours, mins = divmod(mins, 60)

            # using format () method to store the value up to
            # two decimal places
            hour_estimation.set("{0:2d}".format(hours))
            minute_estimation.set("{0:2d}".format(mins))
            second_estimation.set("{0:2d}".format(secs))

            # updating the GUI window after decrementing the
            # temp value every time
            exp_window.update()
            time.sleep(1)

            # when temp value = 0; then a tkinter.messagebox pop's up
            # with a message:"Time's up"
            if (temp == 0):
                tkinter.messagebox.showinfo("Time Countdown", "The machine is done with the experiment ")

            # after every one sec the value of temp will be decremented
            # by one
            temp -= 1

    def trigger_create_pumps(eventObject):  # Used to trigger the create_pump function when creating a board
        settings.machine_board = combobox_board_type.get()
        create_pumps()

    def thread_run_experiment():
        run_thread = threading.Thread(target=run_method)
        run_thread.start()

    def run_method():

        # set the comport used
        comport_index = combobox_serial_port.current()
        ports = serial.tools.list_ports.comports()
        settings.comport = [port.device for port in ports][comport_index]

        experiment_data = settings.experiment_data
        i = 0
        for idx, row in experiment_data.iterrows():
            if idx != "":
                i += 1
            elif type(idx) is tuple and idx[0] != "":
                i += 1
        experiment_data = experiment_data.iloc[:i, :]
        settings.experiment_data = experiment_data

        # make the output txt file for log purposes name will be: protocol + current date and time
        # The log feature is ready, but commented out right now. It should be turned on by a checkmark on the GUI
       #now = datetime.now()
       #current_time = now.strftime("%d_%m_%Y %H_%M_%S")
       #protocol_name = settings.protocol_name
       #file_name = protocol_name + " " + current_time

       #folder_path = os.getcwd()
       #file_place = f"{folder_path}\log outputs\{file_name}"

       #sys.stdout = open(file_place + ".txt", 'w')

        # This function is to give easy access to experiment with new methods.
        # test_method()

        # reads the python script as a string and executes it line for line
        folder_path = os.getcwd()
        method = settings.method
        if method[-3:] == ".py":
            pass
        else:
            method = method + ".py"
        # Sets up a timer
        wait_operator() # if it should start delayed
        thread_countdown() # to estimate how much time it would take to run

        start_timer = time.time()
        with open(folder_path + "\\methods\\" + method) as method_file:
            exec(method_file.read())
        end_time = time.time()
        print("Time it actually took: " + str(end_time-start_timer))

        #sys.stdout.close()



    def serial_ports():
        return serial.tools.list_ports.comports()

    def set_time():
        global hour, minute, seconds, time_unit
        hour = hour_entry.get()
        minute = minute_entry.get()
        seconds = second_entry.get()
        time_unit = time_unit_combobox.get()

    def randomize_coordinates():
        experiment_data = settings.experiment_data
        experiment_data = experiment_data.astype(float)
        # Save the position of the X and Y coordinates, remove the index and replace with the random, then conjoin them
        coordinate_df = experiment_data[["x-coordinate", "y-coordinate"]]
        coordinate_df = coordinate_df.reset_index(drop=True)

        experiment_data.pop("x-coordinate")
        experiment_data.pop("y-coordinate")
        experiment_data.index.astype(str)
        i = 0
        for idx, row in experiment_data.iterrows():
            if idx != "" and pd.isna(idx) is False:
                i += 1
            elif type(idx) is tuple and idx[0] != "":
                i += 1

        randomized_data = experiment_data.iloc[:i, :]  # get the part of the data that needs randomizing
        concat_df = experiment_data.iloc[i:, :]  # Keep the remaining data
        randomized_data = randomized_data.sample(frac=1)  # randomize
        experiment_data = pd.concat([randomized_data, concat_df], axis=0)  # combine with the remaining data

        # Set the new index
        coordinate_df = coordinate_df.set_index(experiment_data.index)
        experiment_data = pd.concat([experiment_data, coordinate_df], axis=1)
        settings.experiment_data = experiment_data

        construct_canvas()

    def construct_canvas():
        experiment_data = settings.experiment_data
        experiment_data = experiment_data.astype(float)
        # Make plot of the reaction vials
        fig = plt.Figure(figsize=(2.5, 2.5), dpi=200)
        ax = fig.add_subplot(111)
        fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        # Coordinates from dataframe
        for idx, row in experiment_data.iterrows():
            x = row["x-coordinate"]
            y = row["y-coordinate"]
            # Check if the index is "NaN"/"
            if idx == "":
                ax.scatter(x, y, marker="o", facecolors="none", s=250, color="black")
            elif isinstance(idx, float):
                ax.scatter(x, y, marker="o", facecolors="none", s=250, color="black")
            elif type(idx) is tuple:  # initiates if loaded from txt file
                # Extract the experiment number
                experiment_number = str(idx)
                experiment_number = experiment_number.split(" ")  # split to obtain the number without "Experiment"
                ax.scatter(x, y, marker="o", s=250, facecolors="none", color="green")
                ax.text(x, y, f"Exp. {experiment_number[1]}", fontsize=3.5, ha="center", va="center")
            else:  # initiates if initiated directly without loading existing protocol
                # Extract the experiment number
                experiment_number = str(idx)
                experiment_number = experiment_number.split(" ")[1]  # split to obtain the number without "Experiment"
                ax.scatter(x, y, marker="o", s=250, facecolors="none", color="green")
                ax.text(x, y, f"Exp. {experiment_number}", fontsize=3.5, ha="center", va="center")
        # Remove the x-axis ticks and numbers
        ax.set_xticks([])
        ax.set_xticklabels([])
        # Remove the y-axis ticks and numbers
        ax.set_yticks([])
        ax.set_yticklabels([])
        # Adjust the black frame dimensions
        xlim = (0, 220)  # Adjust these values according to your desired x-axis limits
        ylim = (0, 220)  # Adjust these values according to your desired y-axis limits
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        # tk canvas
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        # place the plot
        canvas.get_tk_widget().grid(row=0, column=0, sticky="n")

    # "Run experiment window setup" -> create sub-frames in the window for individual grids

    grid_frame.grid(row=0, column=0)
    plot_frame = tk.Frame(exp_window)   # holds the layout plot
    plot_frame.grid(row=0, column=1)
    info_frame = tk.Frame(exp_window)   # holds information on the experiments
    info_frame.grid(row=0, column=2)
    timer_frame = tk.Frame(exp_window)  # holds the timer
    timer_frame.grid(row=1, column=0)

    # set up widgets
    # combobox for selection the serial port -> set up
    serial_port_label = tk.Label(grid_frame, text="Comports: ")
    serial_port_label.grid(row=0, column=0)
    combobox_serial_port = ttk.Combobox(grid_frame, width=15, values=serial_ports())
    combobox_serial_port.grid(row=1, column=0)
    combobox_serial_port.current(0)  # Set the default value to the first comport

    # combobox for board type selection -> set up
    board_type_label = tk.Label(grid_frame, text="Board Type: ")
    board_type_label.grid(row=2, column=0)
    combobox_board_type = ttk.Combobox(grid_frame, width=15, values=["Arduino", "BTT Octo"])
    combobox_board_type.grid(row=3, column=0)
    combobox_board_type.current(0)  # set default value to the first entry in list
    settings.machine_board = combobox_board_type.get()  # get the default value from the list
    combobox_board_type.bind("<<ComboboxSelected>>", trigger_create_pumps)  # trigger the create_pump function



    # create the correct labels
    label_method = tk.Label(grid_frame, text="Method: " + str(settings.method))
    label_method.grid(row=0, column=1, columnspan=2, sticky="w")
    label_module = tk.Label(grid_frame, text="Module: " + str(settings.module))
    label_module.grid(row=1, column=1, columnspan=2, sticky="w")
    label_number_of_reaction_vessels = tk.Label(grid_frame,
                                                text="Reaction vessels: " + str(settings.number_of_reaction_vessels))

    label_number_of_reaction_vessels.grid(row=2, column=1, columnspan=2, sticky="w")
    label_max_volume = tk.Label(grid_frame, text="Max volume: " + str(settings.max_volume))
    label_max_volume.grid(row=3, column=1, columnspan=2, sticky="w")
    label_waste_coordinates = tk.Label(grid_frame, text="Waste : " + str(settings.module_waste_coordinates))
    label_waste_coordinates.grid(row=4, column=1, columnspan=2, sticky="w")
    label_beaker_height = tk.Label(grid_frame, text="Waste height: " + str(settings.beaker_height))
    label_beaker_height.grid(row=5, column=1, columnspan=2, sticky="w")
    label_safety_height = tk.Label(grid_frame, text="Safety height: " + str(settings.safety_height))
    label_safety_height.grid(row=6, column=1, columnspan=2, sticky="w")
    label_vial_height = tk.Label(grid_frame, text="Vial height: " + str(settings.vial_height))
    label_vial_height.grid(row=7, column=1, columnspan=2, sticky="w")
    label_feedrate = tk.Label(grid_frame, text="Machine speed: " + str(settings.feedrate))
    label_feedrate.grid(row=8, column=1, columnspan=2, sticky="w")


    # Button declaration
    button_start = tk.Button(grid_frame, width=15, text="Start Experiment",
                             command=lambda: [set_time(), thread_run_experiment()])
    button_random = tk.Button(grid_frame, width=15, text="Randomize positions", command=randomize_coordinates)
    button_save_positions = tk.Button(grid_frame, width=15, text="Save layout as csv",
                                      command=lambda: [save_dataframe(settings.experiment_data)])

    # position widgets
    button_start.grid(row=4, column=0)
    button_random.grid(row=5, column=0)
    button_save_positions.grid(row=6, column=0)

    # Setup of the buttons for checking the pump settings
    pump_buttons = []
    for i in range(len(settings.pump_labels)):
        pump_buttons.append(tk.Button(grid_frame, text="Pump {}:".format(i + 1)))
        pump_buttons[i].configure(command=lambda c=i: update_pump(pump_buttons[c], grid_frame))
        pump_buttons[i].grid(row=i + 9, column=1, sticky="w")
        label = tk.Label(grid_frame, text=settings.pump_labels[i])
        label.grid(row=i + 9, column=2, sticky="w")

    # declaration and setup of the delayed start widgets
    time_unit_combobox = ttk.Combobox(timer_frame, width=10, values=["Not timed", "AM", "PM", "From now"])
    time_unit_combobox.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 5))
    time_unit_combobox.current(0)


    time_unit_label = tk.Label(timer_frame, text="Timer")
    time_unit_label.grid(row=0, column=0, sticky="w", padx=5)
    hour_label = tk.Label(timer_frame, text="Hrs.", width=2)
    hour_label.grid(row=0, column=1, padx=5)
    hour_entry = tk.Entry(timer_frame, width=2)
    hour_entry.grid(row=1, column=1, padx=5, pady=(0, 5))
    minute_label = tk.Label(timer_frame, text="Min.", width=2)
    minute_label.grid(row=0, column=2, padx=5)
    minute_entry = tk.Entry(timer_frame, width=2)
    minute_entry.grid(row=1, column=2, padx=5, pady=(0, 5))
    second_label = tk.Label(timer_frame, text="Sec.", width=2)
    second_label.grid(row=0, column=3, padx=5)
    second_entry = tk.Entry(timer_frame, width=2)
    second_entry.grid(row=1, column=3, padx=5, pady=(0, 5))


    time_estimation_label = tk.Label(timer_frame, text="Estimated Time for protocol")
    time_estimation_label.grid(row=0+2, column=0, sticky="w", padx=5)
    hour_estimation_title = tk.Label(timer_frame, text="Hrs.", width=2)
    hour_estimation_title.grid(row=0+2, column=1, padx=5)
    hour_estimation_counter = tk.Label(timer_frame, width=2, textvariable=hour_estimation)
    hour_estimation_counter.grid(row=1+2, column=1, padx=5, pady=(0, 5))
    minute_esitmation_title = tk.Label(timer_frame, text="Min.", width=2)
    minute_esitmation_title.grid(row=0+2, column=2, padx=5)
    minute_esitmation_counter = tk.Label(timer_frame, width=2, textvariable=minute_estimation)
    minute_esitmation_counter.grid(row=1+2, column=2, padx=5, pady=(0, 5))
    second_estimation_title = tk.Label(timer_frame, text="Sec.", width=2)
    second_estimation_title.grid(row=0+2, column=3, padx=5)
    second_estmation_counter = tk.Label(timer_frame, width=2, textvariable=second_estimation)
    second_estmation_counter.grid(row=1+2, column=3, padx=5, pady=(0, 5))

    rows = []
    i = 0
    for idx, row in settings.experiment_data.iterrows():  # Iterate over the DataFrame rows
        j = 0
        volume_tot = 0
        if "Experiment" in str(idx) and idx not in rows:  # Ensure only one of each experiment is printed in the GUI
            rows.append(idx)  # Ensure only one of each experiment is printed in the GUI
            label = tk.Label(info_frame, text="{}".format(idx))  # Write the index value as label
            label.grid(row=i + 1, column=0, padx=10, pady=2, sticky="w")  # place label
            for column in settings.experiment_data.columns:  # retrieve volume entries from the row
                if type(column) is tuple:
                    column_str = str(column[0])
                elif type(column) is str:
                    column_str = column
                if "Solution" in column_str:  # look for the different "Solution" headers
                    if i == 0:  # sets up labels for columns just once
                        label = tk.Label(info_frame, text="{} [mL]".format(column_str))
                        label.grid(row=0, column=j + 1, sticky="w")
                    label = tk.Label(info_frame, text="{}".format(row[column]))
                    label.grid(row=i + 1, column=j + 1)
                    volume_tot += float(row[column])
                j += 1
            if i == 0:  # Set up last label (total volume)
                label = tk.Label(info_frame, text="Total Volume [mL]")
                label.grid(row=0, column=j + 1)
            label = tk.Label(info_frame, text="{}".format(round(volume_tot, 3)))
            label.grid(row=i + 1, column=j + 1)
        i += 1
    # solution information
    k = 0
    info_labels = []
    for information in settings.solution_information:
        if k == 0:
            label_information = tk.Label(info_frame, text="Solution information: ")
            label_information.grid(row=i + 1, column=k, sticky="w")
        label_information = tk.Label(info_frame, text=str(information))
        label_information.grid(row=i+1, column=k+1)
        info_labels.append(information)
        k += 1

    # Create the pump objects and create the plot of the experimental layout
    create_pumps()
    construct_canvas()
    time_estimation()


