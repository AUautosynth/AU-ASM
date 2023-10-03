# imports
import serial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# global variables
serial_connection = None


def serial_ports():
    return serial.tools.list_ports.comports()


def home_function():
    serial_connection.write(b"G28 \n")


def move_around(button):
    text = button["text"]
    if "+" in text:
        serial_connection.write(b"G91 \n")  # set relative movement
        parts = text.split("+")
        axis = parts[0]
        distance = parts[1]
        serial_connection.write("G1 {}{} \n".format(axis, distance).encode())
        # print("G1 {}{} \n".format(axis, distance))
        serial_connection.write(b"G90 \n")  # go back to absolute movement
    elif "-" in text:
        serial_connection.write(b"G91 \n")  # set relative movement
        parts = text.split("-")
        axis = parts[0]
        direction = "-"
        distance = parts[1]
        serial_connection.write("G1 {}{}{} \n".format(axis, direction, distance).encode())
        # print("G1 {}{}{} \n".format(axis, direction, distance))
        serial_connection.write(b"G90 \n")  # go back to absolute movement


def write_to_move(text_field):
    text = text_field.get() + "\n"
    serial_connection.write(text.encode())
    temp = text.split("\n", 1)
    print("Code sent: ", temp[1])


def control_window(window):
    def device_connect():
        global serial_connection
        port = comport.get().split()[0]
        if port != "":
            print("Connecting to " + port)
            serial_connection = serial.Serial(port, 250000, write_timeout=1)
        else:
            messagebox.showerror("Error", "Please select a valid comport")

    def device_disconnect():
        global serial_connection

        serial_connection.close()

        messagebox.showinfo("Arduino Disconnect", "Device disconnected")

    # Window setup
    sub_window = tk.Toplevel(window)

    # comport setup
    comport_label = tk.Label(sub_window, text="Comport:")
    comport_label.grid(row=0, column=0, sticky="w")
    comport = ttk.Combobox(sub_window, width=15, values=serial_ports())
    comport.grid(row=1, column=0)

    # widget setup
    button_connect = tk.Button(sub_window, text="Connect", width=10,
                               command=lambda: [button_home.config(state="normal"),
                                                device_connect(),
                                                button_disconnect.config(state="normal")])
    button_connect.grid(row=2, column=0)

    button_disconnect = tk.Button(sub_window, text="Disconnect", width=10, state="disabled",
                                  command=lambda: device_disconnect())
    button_disconnect.grid(row=3, column=0)

    button_send = tk.Button(sub_window, text="Send", width=10, command=lambda: write_to_move(entry_write),
                            state="disabled")
    button_send.grid(row=6, column=0)

    button_home = tk.Button(sub_window, text="Home", width=10, state="disabled",
                            command=lambda: [button_send.config(state="normal"),
                                             entry_write.config(state="normal"),
                                             home_function()])
    button_home.grid(row=4, column=0)

    entry_write = tk.Entry(sub_window, width=10, state="disabled")
    entry_write.grid(row=5, column=0)

    # control buttons
    control_column = 2
    button_x_1 = tk.Button(sub_window, text="X+1", width=5, command=lambda: move_around(button_x_1))
    button_x_5 = tk.Button(sub_window, text="X+5", width=5, command=lambda: move_around(button_x_5))
    button_x_10 = tk.Button(sub_window, text="X+10", width=5, command=lambda: move_around(button_x_10))
    button_x_1.grid(row=0, column=control_column)
    button_x_5.grid(row=1, column=control_column)
    button_x_10.grid(row=2, column=control_column)
    button_x_1_minus = tk.Button(sub_window, text="X-1", width=5,
                                 command=lambda: move_around(button_x_1_minus))
    button_x_5_minus = tk.Button(sub_window, text="X-5", width=5,
                                 command=lambda: move_around(button_x_5_minus))
    button_x_10_minus = tk.Button(sub_window, text="X-10", width=5,
                                  command=lambda: move_around(button_x_10_minus))
    button_x_1_minus.grid(row=4, column=control_column)
    button_x_5_minus.grid(row=5, column=control_column)
    button_x_10_minus.grid(row=6, column=control_column)

    button_y_1 = tk.Button(sub_window, text="Y+1", width=5, command=lambda: move_around(button_y_1))
    button_y_5 = tk.Button(sub_window, text="Y+5", width=5, command=lambda: move_around(button_y_5))
    button_y_10 = tk.Button(sub_window, text="Y+10", width=5, command=lambda: move_around(button_y_10))
    button_y_1.grid(row=0, column=control_column + 1)
    button_y_5.grid(row=1, column=control_column + 1)
    button_y_10.grid(row=2, column=control_column + 1)
    button_y_1_minus = tk.Button(sub_window, text="Y-1", width=5,
                                 command=lambda: move_around(button_y_1_minus))
    button_y_5_minus = tk.Button(sub_window, text="Y-5", width=5,
                                 command=lambda: move_around(button_y_5_minus))
    button_y_10_minus = tk.Button(sub_window, text="Y-10", width=5,
                                  command=lambda: move_around(button_y_10_minus))
    button_y_1_minus.grid(row=4, column=control_column + 1)
    button_y_5_minus.grid(row=5, column=control_column + 1)
    button_y_10_minus.grid(row=6, column=control_column + 1)

    button_z_1 = tk.Button(sub_window, text="Z+1", width=5, command=lambda: move_around(button_z_1))
    button_z_5 = tk.Button(sub_window, text="Z+5", width=5, command=lambda: move_around(button_z_5))
    button_z_10 = tk.Button(sub_window, text="Z+10", width=5, command=lambda: move_around(button_z_10))
    button_z_1.grid(row=0, column=control_column + 2)
    button_z_5.grid(row=1, column=control_column + 2)
    button_z_10.grid(row=2, column=control_column + 2)
    button_z_1_minus = tk.Button(sub_window, text="Z-1", width=5,
                                 command=lambda: move_around(button_z_1_minus))
    button_z_5_minus = tk.Button(sub_window, text="Z-5", width=5,
                                 command=lambda: move_around(button_z_5_minus))
    button_z_10_minus = tk.Button(sub_window, text="Z-10", width=5,
                                  command=lambda: move_around(button_z_10_minus))
    button_z_1_minus.grid(row=4, column=control_column + 2)
    button_z_5_minus.grid(row=5, column=control_column + 2)
    button_z_10_minus.grid(row=6, column=control_column + 2)
