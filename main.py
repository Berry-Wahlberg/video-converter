import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
import webbrowser
from video_tool import VideoConverterTab
from audio_tool import AudioConverterTab
from image_tool import ImageConverterTab

# Configuration file path
CONFIG_FILE = "config.json"

LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")

# Language dictionary
LANGUAGES = {
    "English": {
        "title": "Berry Batch Video Format Converter",
        "github_text": "Project GitHub Homepage",
        "language_label": "Application Language:",
        "save_settings": "Save Settings",
        "settings_saved": "Settings Saved",
        "settings_saved_msg": "Your settings have been saved successfully.",
        "tab_video": "Video",
        "tab_audio": "Audio (Under Development)",
        "tab_image": "Image ",
        "tab_settings": "Settings",
    }
}

# Language judgment logic module [start]
import os 
def load_language_files():
    try:
        if os.path.exists(LOCALES_DIR):
            for filename in os.listdir(LOCALES_DIR):
                if filename.endswith(".json"):
                    lang_code = os.path.splitext(filename)[0]
                    try:
                        with open(os.path.join(LOCALES_DIR, filename), 'r', encoding='utf-8') as f:
                            lang_data = json.load(f)
                            LANGUAGES[lang_code] = lang_data
                    except Exception as e:
                        print(f"Failed to load {filename}: {e}")
    except Exception as e:
        print(f"Failed to access locales directory: {e}")

load_language_files()

# Language judgment logic module [End]


class MainApp:
    def __init__(self, root):
        self.root = root
        # Load saved language preference or default to English
        self.language = tk.StringVar(value=self.load_language_preference())

        # Create a Notebook widget for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.video_tab = VideoConverterTab(self.notebook, self.language)
        self.audio_tab = AudioConverterTab(self.notebook)
        self.image_tab = ImageConverterTab(self.notebook, self.language)
        self.setting_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook with initial labels
        self.notebook.add(self.video_tab, text="Video")
        self.notebook.add(self.audio_tab, text="Audio (Under Development)")
        self.notebook.add(self.image_tab, text="Image (Under Development)")
        self.notebook.add(self.setting_tab, text="Settings")

        # Now update tab labels based on current language
        self.update_tab_labels()

        self.update_ui()

        # Create settings UI
        self.create_settings_ui()

        # Save preferences when the application is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_tab_text(self, key):
        """Get tab text based on current language with fallback to English"""
        lang = self.language.get()
        return LANGUAGES.get(lang, LANGUAGES['English']).get(key, LANGUAGES['English'][key])

    def update_tab_labels(self):
        """Update tab labels when language changes"""
        self.notebook.tab(0, text=self.get_tab_text("tab_video"))
        self.notebook.tab(1, text=self.get_tab_text("tab_audio"))
        self.notebook.tab(2, text=self.get_tab_text("tab_image"))
        self.notebook.tab(3, text=self.get_tab_text("tab_settings"))

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
        """Update UI elements based on current language setting with fallback to English"""
        lang = self.language.get()
        self.root.title(LANGUAGES.get(lang, LANGUAGES['English']).get('title', LANGUAGES['English']['title']))
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Set font based on language
        self.font = ("SimHei", 10) if lang == "简体中文" else ("TkDefaultFont", 10)

        # GitHub link
        github_text = LANGUAGES.get(lang, LANGUAGES['English']).get('github_text', LANGUAGES['English']['github_text'])
        github_link = "https://github.com/Berry-Wahlberg/video-converter"

        link_label = tk.Label(self.root, text=github_text, fg="blue", cursor="hand2", font=self.font)
        link_label.pack(pady=10)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new(github_link))

        # Update tab labels
        self.update_tab_labels()

        # Update video tab UI
        self.video_tab.update_ui()

    def create_settings_ui(self):
        """Create the settings tab UI"""
        lang = self.language.get()

        settings_frame = ttk.Frame(self.setting_tab, padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Language selection
        ttk.Label(settings_frame, text=LANGUAGES.get(lang, LANGUAGES['English']).get('language_label', LANGUAGES['English']['language_label']), font=self.font).grid(row=0, column=0, sticky=tk.W, pady=10)
        lang_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.language,
            values=list(LANGUAGES.keys()),
            width=15,
            state="readonly"
        )
        lang_combo.grid(row=0, column=1, padx=5, pady=10)
        lang_combo.set(self.language.get())
        lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # Save settings button
        save_button = ttk.Button(
            settings_frame,
            text=LANGUAGES.get(lang, LANGUAGES['English']).get('save_settings', LANGUAGES['English']['save_settings']),
            command=self.save_settings,
            style='Accent.TButton'
        )
        save_button.grid(row=1, column=0, columnspan=2, pady=20)

    def on_language_change(self, event=None):
        """Handle language change event, update UI and save preference"""
        self.update_ui()
        self.save_language_preference()

    def save_settings(self):
        """Save all settings and show confirmation with fallback to English"""
        lang = self.language.get()
        self.save_language_preference()
        messagebox.showinfo(
            LANGUAGES.get(lang, LANGUAGES['English']).get('settings_saved', LANGUAGES['English']['settings_saved']),
            LANGUAGES.get(lang, LANGUAGES['English']).get('settings_saved_msg', LANGUAGES['English']['settings_saved_msg'])
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()