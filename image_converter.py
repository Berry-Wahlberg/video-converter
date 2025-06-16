import tkinter as tk
from tkinter import ttk

class ImageConverterTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        label = tk.Label(self, text="Image conversion is under development.")
        label.pack(pady=20)