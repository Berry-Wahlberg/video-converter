import tkinter as tk
from tkinter import ttk, filedialog
import os
import subprocess
import json
import glob

# Hard-coded English language configuration
DEFAULT_LANGUAGES = {
    "input_folder_label": "Input Folder:",
    "browse_button": "Browse",
    "output_folder_label": "Output Folder:",
    "auto_set_button": "Auto Set",
    "input_format_label": "Input Format:",
    "output_format_label": "Output Format:",
    "jpeg_quality_label": "JPEG Quality: ",
    "convert_button": "Convert",
    "file_stats_label": "File Stats:",
    "log_label": "Conversion Log:",
    "error_no_io_folders": "Please select input and output folders.",
    "no_files_found": "No files found to convert.",
    "conversion_complete": "Conversion completed.",
    "conversion_failed": "Conversion failed"
}

# Load language configuration from config.json
LANGUAGES = DEFAULT_LANGUAGES
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        lang_code = config.get('language', 'en')
        lang_file = os.path.join('locales', f'{lang_code}.json')
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as lang_f:
                LANGUAGES = json.load(lang_f)
        else:
            print(f"Language file {lang_file} not found, using default.")
except Exception as e:
    print(f"Error loading language configuration: {e}")

class ImageConverterTab(ttk.Frame):
    def __init__(self, parent, language):
        super().__init__(parent)
        self.language = "en"  
        self.update_ui()

    def update_ui(self):
        """Update UI elements based on current language setting"""
        lang = self.language

        # Create variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.input_format = tk.StringVar(value="heic")
        self.output_format = tk.StringVar(value="jpg")
        self.total_files = tk.IntVar(value=0)
        self.successful_files = tk.IntVar(value=0)
        self.failed_files = tk.IntVar(value=0)
        self.jpeg_quality = tk.IntVar(value=80)  # Add JPEG quality variable

        # Create the UI on the image tab
        self.create_widgets()

    def create_widgets(self):
        """Create all UI widgets with proper indentation"""
        # Clear previous widgets
        for widget in self.winfo_children(): 
            widget.destroy()

        lang = self.language

        # Create the main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid layout to be responsive
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.rowconfigure(6, weight=1)  # Give extra space to the log area

        # Input folder selection
        ttk.Label(main_frame, text=LANGUAGES["input_folder_label"]).grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.input_folder).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(main_frame, text=LANGUAGES["browse_button"], command=self.browse_input_folder).grid(row=0, column=2, padx=5, pady=5)

        # Input format selection
        ttk.Label(main_frame, text=LANGUAGES["input_format_label"]).grid(row=1, column=0, sticky=tk.W)
        format_combo = ttk.Combobox(
            main_frame,
            textvariable=self.input_format,
            values=["heic", "png", "jpeg", "jpg", "webp"],  # Add webp to input formats
            width=10
        )
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        format_combo.set("heic")  # Default selection

        # Output folder selection
        ttk.Label(main_frame, text=LANGUAGES["output_folder_label"]).grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.output_folder).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(main_frame, text=LANGUAGES["browse_button"], command=self.browse_output_folder).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(main_frame, text=LANGUAGES["auto_set_button"], command=self.auto_set_output_folder).grid(row=2, column=3, padx=5, pady=5)

        # Output format selection
        ttk.Label(main_frame, text=LANGUAGES["output_format_label"]).grid(row=3, column=0, sticky=tk.W)
        format_combo = ttk.Combobox(
            main_frame,
            textvariable=self.output_format,
            values=["jpg", "png", "jpeg", "webp", "heic"],  # Add heic to output formats
            width=10
        )
        format_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        format_combo.set("jpg")  # Default selection
        format_combo.bind("<<ComboboxSelected>>", self.update_quality_state)  # Bind event to combobox

        # JPEG Quality slider
        self.quality_label = ttk.Label(main_frame, text=LANGUAGES["jpeg_quality_label"] + "80%")
        self.quality_label.grid(row=4, column=0, sticky=tk.W)
        self.quality_slider = ttk.Scale(
            main_frame,
            from_=1,
            to=100,
            variable=self.jpeg_quality,
            command=self.update_quality_label
        )
        self.quality_slider.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.update_quality_state(None)  # Initial state

        # Convert button
        ttk.Button(main_frame, text=LANGUAGES["convert_button"], command=self.convert_images).grid(row=5, column=1, pady=20)

        # Move status label, file count, and log area to the bottom left
        bottom_left_frame = ttk.Frame(main_frame)
        bottom_left_frame.grid(row=7, column=0, columnspan=4, sticky=tk.W+tk.S+tk.E, pady=5)
        bottom_left_frame.columnconfigure(0, weight=1)
        bottom_left_frame.rowconfigure(3, weight=1)

        ttk.Label(bottom_left_frame, textvariable=self.status).pack(anchor=tk.W)

        ttk.Label(bottom_left_frame, text=LANGUAGES["file_stats_label"]).pack(anchor=tk.W)
        ttk.Label(bottom_left_frame, textvariable=lambda: 
                  f"Total: {self.total_files.get()} | "
                  f"Success: {self.successful_files.get()} | "
                  f"Failed: {self.failed_files.get()}").pack(anchor=tk.W)

        ttk.Label(bottom_left_frame, text=LANGUAGES["log_label"]).pack(anchor=tk.W)
        self.log_text = tk.Text(bottom_left_frame, width=80, height=10)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(bottom_left_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def browse_input_folder(self):
        """Open a dialog to select the input folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)
            self.auto_set_output_folder()

    def browse_output_folder(self):
        """Open a dialog to select the output folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def auto_set_output_folder(self):
        """Automatically set output folder based on input folder"""
        input_folder = self.input_folder.get()
        if input_folder:
            output_folder = os.path.join(input_folder, "converted")
            self.output_folder.set(output_folder)

    def update_quality_state(self, event):
        """Enable/disable quality controls based on output format"""
        output_format = self.output_format.get().lower()
        is_jpeg = output_format in ["jpg", "jpeg"]
        state = "normal" if is_jpeg else "disabled"
        self.quality_slider.config(state=state)
        self.quality_label.config(state=state)

    def update_quality_label(self, value):
        """Update the quality label text"""
        quality = int(float(value))
        self.quality_label.config(text=LANGUAGES["jpeg_quality_label"] + f"{quality}%")

    def convert_images(self):
        """Convert images using ImageMagick"""
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()
        input_format = self.input_format.get()
        output_format = self.output_format.get()

        if not input_folder or not output_folder:
            self.status.set(LANGUAGES["error_no_io_folders"])
            return

        try:
            # Ensure output folder exists
            os.makedirs(output_folder, exist_ok=True)

            # Get list of input files
            input_files = glob.glob(os.path.join(input_folder, f"*.{input_format}"))
            self.total_files.set(len(input_files))
            self.successful_files.set(0)
            self.failed_files.set(0)
            self.log_text.delete(1.0, tk.END)

            if not input_files:
                self.status.set(LANGUAGES["no_files_found"])
                return

            for index, input_file in enumerate(input_files):
                file_name = os.path.basename(input_file)
                output_file = os.path.join(output_folder, os.path.splitext(file_name)[0] + f".{output_format}")

                # Check ImageMagick path
                magick_path = os.path.join(os.path.dirname(__file__), 'bin', 'imagemagick', 'magick.exe')
                if not os.path.exists(magick_path):
                    raise FileNotFoundError(f"ImageMagick not found at {magick_path}")

                # Constructing ImageMagick commands
                command = [
                    magick_path,
                    "convert",
                    input_file
                ]

                # Add JPEG quality option if needed
                if output_format.lower() in ["jpg", "jpeg"]:
                    command.extend(["-quality", str(self.jpeg_quality.get())])

                command.append(output_file)

                try:
                    # Run the command
                    subprocess.run(command, check=True)
                    self.successful_files.set(self.successful_files.get() + 1)
                    log_msg = f"Success: {file_name}"
                    self.log_text.insert(tk.END, log_msg + "\n")
                except Exception as e:
                    self.failed_files.set(self.failed_files.get() + 1)
                    log_msg = f"Error: {file_name} - {str(e)}"
                    self.log_text.insert(tk.END, log_msg + "\n")

            self.status.set(LANGUAGES["conversion_complete"])
        except Exception as e:
            self.status.set(f"{LANGUAGES['conversion_failed']}: {str(e)}")
        finally:
            self.log_text.see(tk.END)