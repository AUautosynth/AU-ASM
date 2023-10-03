"""
function creating a subwindow to change the machine settings

"""

# global imports
import tkinter as tk

# local imports
from settings import settings

# GUI layout stuff
box_width = 15
entry_width = 15


def change_settings(window):

    def save_settings():
        new_settings = dict(safety_height=entry_safety_height.get(), beaker_height=entry_beaker_height.get(),
                            vial_height=entry_vial_height.get(), feedrate=entry_feedrate.get())
        for setting in new_settings:
            new_settings[setting] = float(new_settings[setting])
        settings.update_settings(new_settings)

    settings_window = tk.Toplevel(window)
    # settings_window.geometry("300x200")

    # labels declaration and placement
    label_settings = tk.Label(settings_window, text="Machine settings")
    label_settings.grid(row=0, column=0, sticky='w')
    # dosing height for beakers -> e.g. waste
    entry_beaker_height = tk.Entry(settings_window, width=entry_width)
    entry_beaker_height.grid(row=2, column=1)
    entry_beaker_height.insert(0, str(settings.beaker_height))
    label_beaker_height = tk.Label(settings_window, text="Waste beaker height: ")
    label_beaker_height.grid(row=2, column=0, sticky='w')
    label_beaker_height_unit = tk.Label(settings_window, text="mm")
    label_beaker_height_unit.grid(row=2, column=3, sticky="w")
    # safe movement height
    entry_safety_height = tk.Entry(settings_window, width=entry_width)
    entry_safety_height.grid(row=3, column=1)
    entry_safety_height.insert(0, str(settings.safety_height))
    label_safety_height = tk.Label(settings_window, text="Safety height: ")
    label_safety_height.grid(row=3, column=0, sticky='w')
    label_safety_height_unit = tk.Label(settings_window, text="mm")
    label_safety_height_unit.grid(row=3, column=3, sticky="w")
    # Dosing height for in reaction vessels
    entry_vial_height = tk.Entry(settings_window, width=entry_width)
    entry_vial_height.grid(row=4, column=1)
    entry_vial_height.insert(0, str(settings.vial_height))
    label_vial_height = tk.Label(settings_window, text="Vial height: ")
    label_vial_height.grid(row=4, column=0, sticky='w')
    label_vial_height_unit = tk.Label(settings_window, text="mm")
    label_vial_height_unit.grid(row=4, column=3, sticky="w")
    # Feedrate information (machine x,y,z movement speed)
    entry_feedrate = tk.Entry(settings_window, width=entry_width)
    entry_feedrate.grid(row=5, column=1)
    entry_feedrate.insert(0, str(settings.feedrate))
    label_feedrate = tk.Label(settings_window, text="Movement speed: ")
    label_feedrate.grid(row=5, column=0, sticky='w')
    label_feedrate_unit = tk.Label(settings_window, text="mm/s")
    label_feedrate_unit.grid(row=5, column=3, sticky="w")

    # entry_marlin_speed = tk.Entry(settings_window, width=entry_width)

    save_settings_button = tk.Button(settings_window, text="Save settings", width=32,
                                     command=lambda: [save_settings(), settings_window.destroy()])
    save_settings_button.grid(row=7, column=0, columnspan=2, padx=(0, 10))
