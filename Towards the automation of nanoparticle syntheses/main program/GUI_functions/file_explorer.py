"""
These functions saves files and reads folders

"""

# global imports
import tkinter as tk
from tkinter import filedialog
import os


def read_folder_content(folder_name):
    folder_path = os.getcwd()
    folder_path = r"{}\{}".format(folder_path, folder_name)
    text_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            text_files.append(file_name.split(".")[0])
    return text_files

def save_dataframe(dataframe):
    root = tk.Tk()
    root.attributes('-topmost', 1)
    root.withdraw()
    saving_path = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
    dataframe.to_csv(saving_path)




