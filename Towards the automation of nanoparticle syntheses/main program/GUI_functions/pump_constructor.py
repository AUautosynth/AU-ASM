"""
Pop-window for the creation of a new pump.

"""
# global imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os

# Tkinter settings
box_width = 20
entry_width = 23
init_col = 0
create_col = 5


def construct_pump_file():
    def save_pump_file():
        # create the string
        pump_string = "Pump type:" + combobox_pump_type.get() + "\n"
        pump_string += "Syringe size:" + entry_syringe_size.get() + "\n"
        pump_string += "a:" + entry_a.get() + "\n"
        pump_string += "b:" + entry_b.get() + "\n"
        pump_string += "a_speed:" + entry_a_speed.get() + "\n"
        pump_string += "b_speed:" + entry_b_speed.get() + "\n"
        # pump_string += "speed:" + entry_pump_speed.get() + "\n"
        folder_path = os.getcwd()
        directory = folder_path + r"\saved pumps"
        name = entry_pump_name.get()
        if os.path.exists(directory + "\\" + name + ".txt"):
            result = messagebox.askyesno("Confirmation", "File with same name exists, overwrite?")
            if not result:
                return
        with open(directory + "\\" + name + ".txt", "w") as file:
            file.write(pump_string)
        messagebox.showinfo("File saved", "Pump {} successfully saved".format(name))

        # save_string(text=pump_string)

    pump_settings_window = tk.Toplevel()  # sets the window for pump settings

    # labels declaration
    label_pump_settings = tk.Label(pump_settings_window, text="Pump settings (. as decimal)")
    label_pump_settings.grid(row=0, column=0, sticky='w')

    combobox_pump_type = ttk.Combobox(pump_settings_window, values=["Valve pump"], width=box_width)
    combobox_pump_type.grid(row=2, column=1, padx=5, pady=0)
    label_pump_type = tk.Label(pump_settings_window, text="Pump type: ")
    label_pump_type.grid(row=2, column=0, sticky='w')

    entry_syringe_size = tk.Entry(pump_settings_window, width=entry_width)
    entry_syringe_size.grid(row=3, column=1)
    label_syringe_size = tk.Label(pump_settings_window, text="Syringe size [mL]: ")
    label_syringe_size.grid(row=3, column=0, sticky='w')

    entry_a = tk.Entry(pump_settings_window, width=entry_width)
    entry_a.grid(row=4, column=1)
    label_a = tk.Label(pump_settings_window, text="a: ")
    label_a.grid(row=4, column=0, sticky='w')

    entry_b = tk.Entry(pump_settings_window, width=entry_width)
    entry_b.grid(row=5, column=1)
    label_b = tk.Label(pump_settings_window, text="b: ")
    label_b.grid(row=5, column=0, sticky='w')

    entry_a_speed_variable = tk.StringVar(pump_settings_window, value="1.1171")
    entry_a_speed = tk.Entry(pump_settings_window, textvariable=entry_a_speed_variable, width=entry_width)
    entry_a_speed.grid(row=6, column=1)
    label_a_speed = tk.Label(pump_settings_window, text="a speed: ")
    label_a_speed.grid(row=6, column=0, sticky='w')

    entry_b_speed_variable = tk.StringVar(pump_settings_window, value="0.3199")
    entry_b_speed = tk.Entry(pump_settings_window, textvariable=entry_b_speed_variable, width=entry_width)
    entry_b_speed.grid(row=7, column=1)
    label_b_speed = tk.Label(pump_settings_window, text="b speed: ")
    label_b_speed.grid(row=7, column=0, sticky='w')

    entry_pump_name = tk.Entry(pump_settings_window, width=entry_width)
    entry_pump_name.grid(row=8, column=1)
    label_pump_name = tk.Label(pump_settings_window, text="Pump Name")
    label_pump_name.grid(row=8, column=0, sticky='w')

    # button for saving changes
    save_settings_button = tk.Button(pump_settings_window, text="Save pump", width=entry_width,
                                     command=lambda: [save_pump_file()])

    save_settings_button.grid(row=9, column=0)
