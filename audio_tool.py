import tkinter as tk
from tkinter import ttk

class AudioConverterTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        label = tk.Label(self, text="Audio conversion is under development.")
        label.pack(pady=20)