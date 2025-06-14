import os
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import webbrowser
import json  # Added for language preference persistence

# Configuration file path
CONFIG_FILE = "config.json"

# Language dictionary
LANGUAGES = {
    "English": {
        "title": "Berry Batch Video Format Converter",
        "input_folder_label": "Input Folder:",
        "output_folder_label": "Output Folder:",
        "target_format_label": "Target Format:",
        "include_subfolders": "Include Subfolders",
        "overwrite_existing": "Overwrite Existing Files",
        "thread_count_label": "Concurrent Threads:",
        "start_conversion": "Start Conversion",
        "status_label": "Status:",
        "progress_label": "Progress:",
        "file_stats_label": "File Statistics:",
        "log_label": "Conversion Log:",
        "github_text": "Project GitHub Homepage",
        "browse_button": "Browse...",
        "auto_set_button": "Auto Set",
        "error_no_input_folder": "Error",
        "error_no_input_folder_msg": "Please select an input folder",
        "error_invalid_input_folder": "Error",
        "error_invalid_input_folder_msg": "Input folder does not exist: ",
        "error_no_output_folder": "Error",
        "error_no_output_folder_msg": "Please select an output folder",
        "error_create_output_folder": "Error",
        "error_create_output_folder_msg": "Unable to create output folder: ",
        "error_ffmpeg": "Error",
        "error_ffmpeg_msg": "Unable to execute FFmpeg: ",
        "no_video_files": "No video files found",
        "no_video_files_msg": "No video files found in directory: ",
        "conversion_start": "Searching for video files...",
        "conversion_start_log": "Starting to scan video files...",
        "video_files_found": "Found {} video files",
        "using_threads": "Using {} threads for conversion",
        "target_format": "Target Format: {}",
        "output_directory": "Output Directory: {}",
        "converting": "Converting...",
        "conversion_complete": "Conversion completed",
        "conversion_complete_msg": "Conversion completed! Processed {} files, {} succeeded, {} failed.",
        "conversion_failed": "Conversion failed",
        "conversion_failed_msg": "An error occurred during conversion: ",
        "file_conversion_start": "Starting conversion: {}",
        "file_conversion_success": "Success: {}",
        "file_conversion_error": "Error: Error processing {} - {}",
        "file_conversion_skip": "Skipping: {} already exists",
        "file_not_found": "Error: {} is not a valid file",
        "unknown_error": "Unknown error: An exception occurred while converting {} - {}",
        "conversion_finished_title": "Completed",
        "conversion_finished_msg": "Conversion completed!\nSuccess: {}\nFailed: {}",
        "set_output_folder": "Automatically set output folder to: {}",
    },

    "简体中文": {
        "title": "花花视频格式批量转换工具",
        "input_folder_label": "输入文件夹:",
        "output_folder_label": "输出文件夹:",
        "target_format_label": "目标格式:",
        "include_subfolders": "包含子文件夹",
        "overwrite_existing": "覆盖已存在文件",
        "thread_count_label": "并发线程数:",
        "start_conversion": "开始转换",
        "status_label": "状态:",
        "progress_label": "进度:",
        "file_stats_label": "文件统计:",
        "log_label": "转换日志:",
        "github_text": "项目GitHub主页",
        "browse_button": "浏览...",
        "auto_set_button": "自动设置",
        "error_no_input_folder": "错误",
        "error_no_input_folder_msg": "请选择输入文件夹",
        "error_invalid_input_folder": "错误",
        "error_invalid_input_folder_msg": "输入文件夹不存在: ",
        "error_no_output_folder": "错误",
        "error_no_output_folder_msg": "请选择输出文件夹",
        "error_create_output_folder": "错误",
        "error_create_output_folder_msg": "无法创建输出文件夹: ",
        "error_ffmpeg": "错误",
        "error_ffmpeg_msg": "无法执行FFmpeg: ",
        "no_video_files": "未找到视频文件",
        "no_video_files_msg": "未找到视频文件在目录: ",
        "conversion_start": "正在查找视频文件...",
        "conversion_start_log": "开始扫描视频文件...",
        "video_files_found": "找到 {} 个视频文件",
        "using_threads": "使用 {} 个线程进行转换",
        "target_format": "目标格式: {}",
        "output_directory": "输出目录: {}",
        "converting": "正在转换...",
        "conversion_complete": "转换完成",
        "conversion_complete_msg": "转换完成！共处理 {} 个文件，成功 {} 个，失败 {} 个。",
        "conversion_failed": "转换失败",
        "conversion_failed_msg": "转换过程中发生错误: ",
        "file_conversion_start": "开始转换: {}",
        "file_conversion_success": "成功: {}",
        "file_conversion_error": "错误: 处理 {} 时出错 - {}",
        "file_conversion_skip": "跳过: {} 已存在",
        "file_not_found": "错误: {} 不是有效的文件",
        "unknown_error": "未知错误: 转换 {} 时发生异常 - {}",
        "conversion_finished_title": "完成",
        "conversion_finished_msg": "转换完成！\n成功: {}\n失败: {}",
        "set_output_folder": "自动设置输出文件夹为: {}",
    }
}


class VideoConverter:
    def __init__(self, root):
        self.root = root
        # Load saved language preference or default to English
        self.language = tk.StringVar(value=self.load_language_preference())
        self.update_ui()
        
        # Save preferences when the application is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_language_preference(self):
        """Load saved language preference from config file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("language", "English")
        except Exception as e:
            print(f"Failed to load config: {e}")
        return "English"  # Default to English if config is missing or invalid

    def save_language_preference(self):
        """Save current language preference to config file"""
        try:
            config = {"language": self.language.get()}
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def on_closing(self):
        """Handle application close event, save preferences"""
        self.save_language_preference()
        self.root.destroy()

    def update_ui(self):
        """Update UI elements based on current language setting"""
        lang = self.language.get()
        self.root.title(LANGUAGES[lang]["title"])
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Set font based on language
        self.font = ("SimHei", 10) if lang == "简体中文" else ("TkDefaultFont", 10)

        # Create variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.include_subfolders = tk.BooleanVar(value=True)
        self.overwrite_existing = tk.BooleanVar(value=False)
        self.thread_count = tk.IntVar(value=4)
        self.status = tk.StringVar(value="Ready")
        self.total_files = tk.IntVar(value=0)
        self.processed_files = tk.IntVar(value=0)
        self.successful_files = tk.IntVar(value=0)
        self.failed_files = tk.IntVar(value=0)
        self.target_format = tk.StringVar(value="mp4")

        # FFmpeg path (relative)
        self.ffmpeg_path = os.path.abspath("./bin/ffmpeg.exe")

        # Create the UI
        self.create_widgets()

    def create_widgets(self):
        """Create all UI widgets with proper indentation"""
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        lang = self.language.get()

        # Create the main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create custom styles
        self.style = ttk.Style()
        self.style.configure('TButton', font=self.font)
        self.style.configure('TLabel', font=self.font)
        
        # Configure Accent.TButton with blue background and black text
        self.style.configure('Accent.TButton', 
                             font=self.font, 
                             foreground='black',  # Black text
                             background='#1e88e5',  # Medium blue background
                             bordercolor='#1976d2',
                             focuscolor='#1976d2',
                             highlightcolor='#1976d2'
                             )

        # Input folder selection
        ttk.Label(main_frame, text=LANGUAGES[lang]["input_folder_label"]).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text=LANGUAGES[lang]["browse_button"], command=self.browse_input_folder).grid(row=0, column=2, padx=5, pady=5)

        # Output folder selection
        ttk.Label(main_frame, text=LANGUAGES[lang]["output_folder_label"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text=LANGUAGES[lang]["browse_button"], command=self.browse_output_folder).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(main_frame, text=LANGUAGES[lang]["auto_set_button"], command=self.auto_set_output_folder).grid(row=1, column=3, padx=5, pady=5)

        # Target format selection
        ttk.Label(main_frame, text=LANGUAGES[lang]["target_format_label"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        format_combo = ttk.Combobox(
            main_frame,
            textvariable=self.target_format,
            values=["mp4", "mkv", "avi", "mov", "flv", "wmv"],
            width=10
        )
        format_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        format_combo.set("mp4")  # Default selection

        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Checkbutton(options_frame, text=LANGUAGES[lang]["include_subfolders"], variable=self.include_subfolders).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text=LANGUAGES[lang]["overwrite_existing"], variable=self.overwrite_existing).pack(side=tk.LEFT, padx=10)

        # Thread count selection
        ttk.Label(main_frame, text=LANGUAGES[lang]["thread_count_label"]).grid(row=4, column=0, sticky=tk.W, pady=5)
        thread_combo = ttk.Combobox(main_frame, textvariable=self.thread_count, values=[1, 2, 3, 4, 5, 6, 7, 8], width=5)
        thread_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        # Conversion button with increased width
        ttk.Button(main_frame, text=LANGUAGES[lang]["start_conversion"], command=self.start_conversion, style='Accent.TButton').grid(row=5, column=0, columnspan=10, pady=20)

        # Status information
        ttk.Label(main_frame, text=LANGUAGES[lang]["status_label"]).grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=self.status).grid(row=6, column=1, sticky=tk.W, pady=5)

        # Progress bar
        ttk.Label(main_frame, text=LANGUAGES[lang]["progress_label"]).grid(row=7, column=0, sticky=tk.W, pady=5)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, variable=progress_var, length=400)
        progress_bar.grid(row=7, column=1, padx=5, pady=5)

        # File count
        ttk.Label(main_frame, text=LANGUAGES[lang]["file_stats_label"]).grid(row=8, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=lambda:
                  f"Total: {self.total_files.get()} | "
                  f"Success: {self.successful_files.get()} | "
                  f"Failed: {self.failed_files.get()}").grid(row=8, column=1, sticky=tk.W, pady=5)

        # Log area
        ttk.Label(main_frame, text=LANGUAGES[lang]["log_label"]).grid(row=9, column=0, sticky=tk.NW, pady=5)
        self.log_text = tk.Text(main_frame, width=80, height=10, font=self.font)
        self.log_text.grid(row=9, column=1, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)
        scrollbar = ttk.Scrollbar(main_frame, command=self.log_text.yview)
        scrollbar.grid(row=9, column=3, sticky=tk.NS)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Set weights to make the log area scalable
        main_frame.grid_rowconfigure(9, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Language selection
        lang_combo = ttk.Combobox(
            main_frame,
            textvariable=self.language,
            values=["简体中文", "English"],
            width=10
        )
        lang_combo.grid(row=10, column=0, sticky=tk.W, padx=5, pady=5)
        lang_combo.set(self.language.get())
        lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # GitHub link
        github_text = LANGUAGES[lang]["github_text"]
        github_link = "https://github.com/Berry-Wahlberg/video-converter"

        link_label = tk.Label(main_frame, text=github_text, fg="blue", cursor="hand2", font=self.font)
        link_label.grid(row=10, column=1, columnspan=3, pady=10)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new(github_link))

    def on_language_change(self, event=None):
        """Handle language change event, update UI and save preference"""
        self.update_ui()
        self.save_language_preference()

    def browse_input_folder(self):
        """Open dialog to select input folder"""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            folder = os.path.normpath(folder)
            self.input_folder.set(folder)
            self.auto_set_output_folder()

    def browse_output_folder(self):
        """Open dialog to select output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            folder = os.path.normpath(folder)
            self.output_folder.set(folder)

    def auto_set_output_folder(self):
        """Automatically set output folder to input_folder/mp4"""
        input_folder = self.input_folder.get()
        lang = self.language.get()
        if input_folder:
            output_folder = os.path.join(input_folder, "mp4")
            output_folder = os.path.normpath(output_folder)
            self.output_folder.set(output_folder)
            self.log(LANGUAGES[lang]["set_output_folder"].format(output_folder))

    def start_conversion(self):
        """Start the video conversion process"""
        lang = self.language.get()
        # Input validation
        input_folder = self.input_folder.get()
        if not input_folder:
            messagebox.showerror(LANGUAGES[lang]["error_no_input_folder"], LANGUAGES[lang]["error_no_input_folder_msg"])
            return

        if not os.path.isdir(input_folder):
            messagebox.showerror(LANGUAGES[lang]["error_invalid_input_folder"], LANGUAGES[lang]["error_invalid_input_folder_msg"] + input_folder)
            return

        # Output folder validation
        output_folder = self.output_folder.get()
        if not output_folder:
            self.auto_set_output_folder()
            output_folder = self.output_folder.get()

        if not os.path.isdir(output_folder):
            try:
                os.makedirs(output_folder)
                self.log(LANGUAGES[lang]["set_output_folder"].format(output_folder))
            except Exception as e:
                messagebox.showerror(LANGUAGES[lang]["error_create_output_folder"], LANGUAGES[lang]["error_create_output_folder_msg"] + output_folder + "\n" + str(e))
                return

        # Check FFmpeg availability
        try:
            subprocess.run([self.ffmpeg_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            messagebox.showerror(LANGUAGES[lang]["error_ffmpeg"], LANGUAGES[lang]["error_ffmpeg_msg"] + self.ffmpeg_path + "\nPlease ensure ffmpeg.exe exists in the bin directory")
            return

        # Reset counters
        self.total_files.set(0)
        self.processed_files.set(0)
        self.successful_files.set(0)
        self.failed_files.set(0)

        # Clear log
        self.log_text.delete(1.0, tk.END)

        # Start conversion in a new thread
        thread = threading.Thread(target=self.perform_conversion, args=(self.target_format.get(),))
        thread.daemon = True
        thread.start()

    def perform_conversion(self, target_format):
        """Perform the actual video conversion process"""
        lang = self.language.get()
        try:
            self.status.set(LANGUAGES[lang]["conversion_start"])
            self.log(LANGUAGES[lang]["conversion_start_log"])

            input_folder = self.input_folder.get()
            output_folder = self.output_folder.get()
            include_subfolders = self.include_subfolders.get()
            thread_count = self.thread_count.get()

            # Find video files
            video_files = self.find_video_files(input_folder, include_subfolders)

            self.total_files.set(len(video_files))

            if not video_files:
                self.status.set(LANGUAGES[lang]["no_video_files"])
                self.log(LANGUAGES[lang]["no_video_files_msg"].format(input_folder))
                return

            self.log(LANGUAGES[lang]["video_files_found"].format(len(video_files)))
            self.log(LANGUAGES[lang]["using_threads"].format(thread_count))
            self.log(LANGUAGES[lang]["target_format"].format(target_format.upper()))
            self.log(LANGUAGES[lang]["output_directory"].format(output_folder))

            # Create task queue
            task_queue = queue.Queue()

            # Add all files to the queue
            for video_file in video_files:
                task_queue.put((video_file, input_folder, output_folder))

            # Create result queue
            result_queue = queue.Queue()

            # Start worker threads
            self.status.set(LANGUAGES[lang]["converting"])

            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = []
                for _ in range(thread_count):
                    future = executor.submit(
                        self.worker_thread,
                        task_queue,
                        result_queue,
                        self.ffmpeg_path,
                        target_format
                    )
                    futures.append(future)

                # Process results
                while self.processed_files.get() < self.total_files.get():
                    if not result_queue.empty():
                        success = result_queue.get()
                        if success:
                            self.successful_files.set(self.successful_files.get() + 1)
                        else:
                            self.failed_files.set(self.failed_files.get() + 1)
                        self.processed_files.set(self.processed_files.get() + 1)

                    # Update progress bar
                    progress = (self.processed_files.get() / self.total_files.get()) * 100
                    self.root.update_idletasks()

                    # Short sleep to reduce CPU usage
                    time.sleep(0.1)

            # Wait for all tasks to complete
            for future in futures:
                future.result()

            self.status.set(LANGUAGES[lang]["conversion_complete"])
            self.log(LANGUAGES[lang]["conversion_complete_msg"].format(self.total_files.get(), self.successful_files.get(), self.failed_files.get()))
            messagebox.showinfo(LANGUAGES[lang]["conversion_finished_title"], LANGUAGES[lang]["conversion_finished_msg"].format(self.successful_files.get(), self.failed_files.get()))

        except Exception as e:
            self.status.set(LANGUAGES[lang]["conversion_failed"])
            self.log(LANGUAGES[lang]["conversion_failed_msg"] + str(e))
            messagebox.showerror(LANGUAGES[lang]["conversion_failed"], LANGUAGES[lang]["conversion_failed_msg"] + str(e))

    def worker_thread(self, task_queue, result_queue, ffmpeg_path, target_format):
        """Worker thread to process video conversion tasks"""
        lang = self.language.get()
        while True:
            try:
                # Get task with timeout
                video_file, input_folder, output_folder = task_queue.get(timeout=1)
            except queue.Empty:
                break

            try:
                # Perform conversion
                self.log(LANGUAGES[lang]["file_conversion_start"].format(os.path.basename(video_file)))
                success = self.convert_video(
                    video_file,
                    ffmpeg_path,
                    self.overwrite_existing.get(),
                    target_format,
                    input_folder,
                    output_folder
                )

                # Report result
                result_queue.put(success)

            except Exception as e:
                self.log(LANGUAGES[lang]["file_conversion_error"].format(os.path.basename(video_file), str(e)))
                result_queue.put(False)
            finally:
                # Mark task as done
                task_queue.task_done()

    def convert_video(self, video_file, ffmpeg_path, overwrite=False, target_format="mp4", input_folder=None, output_folder=None):
        """Convert a single video file using FFmpeg"""
        lang = self.language.get()
        # Check if file exists
        if not os.path.isfile(video_file):
            self.log(LANGUAGES[lang]["file_not_found"].format(video_file))
            return False

        # Build output file path
        if input_folder and output_folder:
            # Preserve directory structure
            rel_path = os.path.relpath(os.path.dirname(video_file), input_folder)
            output_subfolder = os.path.join(output_folder, rel_path)
            output_subfolder = os.path.normpath(output_subfolder)
            os.makedirs(output_subfolder, exist_ok=True)

            base_name = os.path.basename(os.path.splitext(video_file)[0])
            output_file = os.path.join(output_subfolder, f"{base_name}.{target_format}")
            output_file = os.path.normpath(output_file)
        else:
            # Use original path if no input/output folders provided
            base_name, _ = os.path.splitext(video_file)
            output_file = f"{base_name}.{target_format}"

        # Check if output file exists
        if os.path.exists(output_file):
            if not overwrite:
                self.log(LANGUAGES[lang]["file_conversion_skip"].format(output_file))
                return True

        # Build FFmpeg command
        cmd = [
            ffmpeg_path,
            '-i', video_file,
            '-c', 'copy',  # Copy streams without re-encoding
            '-y' if overwrite else '-n',  # Overwrite existing files
            output_file
        ]

        try:
            # Execute command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            self.log(LANGUAGES[lang]["file_conversion_success"].format(output_file))
            return True
        except subprocess.CalledProcessError as e:
            self.log(LANGUAGES[lang]["file_conversion_error"].format(video_file, e.stdout))
            return False
        except Exception as e:
            self.log(LANGUAGES[lang]["unknown_error"].format(video_file, str(e)))
            return False

    def find_video_files(self, directory, recursive=True):
        """Find all supported video files in the directory"""
        if not os.path.isdir(directory):
            raise ValueError(f"Error: Directory does not exist - {directory}")

        # Supported video formats
        video_extensions = [
            '.m4s', '.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv',
            '.ts', '.webm', '.vob', '.mts', '.m2ts', '.3gp'
        ]

        video_files = []

        if recursive:
            # Recursive search
            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in video_extensions):
                        video_files.append(os.path.join(root, file))
        else:
            # Non-recursive search
            for file in os.listdir(directory):
                if any(file.lower().endswith(ext) for ext in video_extensions) and os.path.isfile(os.path.join(directory, file)):
                    video_files.append(os.path.join(directory, file))

        return video_files

    def log(self, message):
        """Add message to the log display"""
        self.root.after(0, lambda: self._append_to_log(message))

    def _append_to_log(self, message):
        """Helper method to append message to log text widget"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to bottom


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverter(root)
    root.mainloop()