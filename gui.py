import os
from ttkthemes import ThemedTk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
import threading
import sys
import io
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logging.info("Starting program...")

class TextRedirector(io.StringIO):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        try:
            self.widget.config(state=tk.NORMAL)
            self.widget.insert(tk.END, str)
            self.widget.see(tk.END)
            self.widget.config(state=tk.DISABLED)
        except tk.TclError as e:
            logging.error(f"Error in TextRedirector: {e}")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify=tk.LEFT, background="#ffffff", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class AdvancedAudioSplitterUI:
    def __init__(self, master):
        logging.info("Initializing UI...")
        self.master = master
        self.master.title("AKD GUI")
        try:
            self.create_widgets()
        except Exception as e:
            logging.critical(f"Failed to initialize UI: {e}")
            print(f"Failed to initialize UI: {e}")
            raise
            
    def create_widgets(self):
        # Create main frame
        self.frame = ttk.Frame(self.master, padding="2")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E))  # Ajouté sticky=(tk.W, tk.E)

        # Create sub-frames for each group of widgets
        self.audio_frame = self.create_labeled_frame("Audio Settings", row=0, col=0)
        self.spleeter_frame = self.create_labeled_frame("Spleeter Settings", row=1, col=0)
        self.script_frame = self.create_labeled_frame("Script Settings", row=2, col=0)
        self.advanced_frame = self.create_labeled_frame("Advanced Settings", row=3, col=0)

        # Audio Settings Widgets
        self.create_audio_widgets(self.audio_frame)

        # Spleeter Settings Widgets
        self.create_spleeter_widgets(self.spleeter_frame)

        # Script Settings Widgets
        self.create_script_widgets(self.script_frame)

        # Advanced Settings Widgets
        self.create_advanced_widgets(self.advanced_frame)

        # Adding a Text widget to serve as a console
        self.console = tk.Text(self.master, wrap=tk.WORD, height=10)
        self.console.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)  # Changé row de 4 à 1
        self.console.config(state=tk.DISABLED)
        
        # Redirect stdout and stderr
        sys.stdout = TextRedirector(self.console)
        sys.stderr = TextRedirector(self.console)   
        
        # Execute button with distinct visibility
        self.execute_button = ttk.Button(self.master, text="Execute", style='TButton', command=self.execute_command_threaded)
        self.execute_button.grid(row=5, columnspan=3, pady=20)

        ToolTip(self.audio_file_entry, "Path to the audio file you want to process.")
        ToolTip(self.fps_entry, "Frames Per Second for the target animation.")
        ToolTip(self.stems_entry, "The number of audio stems to split the original audio into.")
        ToolTip(self.music_start_entry, "Start time for the audio in minute,second format.")
        ToolTip(self.music_end_entry, "End time for the audio in minute,second format.")
        ToolTip(self.speed_entry, "The amplitude/strength/intensity of your animation.")
        ToolTip(self.zoom_speed_entry, "Reactive zoom impact speed for the audio.")
        ToolTip(self.zoom_sound_combo, "Sound for zoom effect. Choose from 'drums', 'other', 'piano', 'bass'.")
        ToolTip(self.strength_sound_combo, "Sound for strength schedule. Recommended to be the same as zoom sound.")
        ToolTip(self.noise_sound_combo, "Sound for noise schedule. Recommended to be the same as zoom sound.")
        ToolTip(self.contrast_sound_combo, "Sound for contrast schedule. Recommended to be the same as zoom sound.")
        ToolTip(self.drums_drop_speed_entry, "Reactive impact of the drums audio on the animation when the audio makes a sound.")
        ToolTip(self.drums_begin_speed_entry, "Starting value on keyframe 1 for drums.")
        ToolTip(self.drums_audio_path_entry, "Path to your drums .wav file if not using Spleeter.")
        ToolTip(self.piano_audio_path_entry, "Path to your piano .wav file if not using Spleeter.")
        ToolTip(self.bass_audio_path_entry, "Path to your bass .wav file if not using Spleeter.")
        ToolTip(self.other_audio_path_entry, "Path to your other .wav file if not using Spleeter.")
        ToolTip(self.piano_drop_speed_entry, "Reactive impact of the piano audio on the animation when the audio makes a sound.")
        ToolTip(self.bass_drop_speed_entry, "Reactive impact of the bass audio on the animation when the audio makes a sound.")
        ToolTip(self.bpm_file_entry, "Path to the audio file for BPM calculations.")
        ToolTip(self.intensity_entry, "The amplitude/strength/intensity of your BPM-based animation.")

        self.fps_entry.insert(0, "30")
        self.stems_entry.insert(0, "5")
        self.music_start_entry.insert(0, "1,30")
        self.music_end_entry.insert(0, "3,20")
        self.speed_entry.insert(0, "1.5")
        self.zoom_speed_entry.insert(0, "0.8")
        self.drums_drop_speed_entry.insert(0, "0.3")
        self.drums_begin_speed_entry.insert(0, "0.1")
        self.piano_drop_speed_entry.insert(0, "0.25")
        self.bass_drop_speed_entry.insert(0, "0.4")
        self.intensity_entry.insert(0, "1.0")

    def create_labeled_frame(self, label, row, col):
        frame = ttk.LabelFrame(self.frame, text=label, padding="2")
        frame.grid(row=row, column=col, sticky=(tk.W, tk.E), pady=10)
        return frame

    def create_audio_widgets(self, frame):
        ttk.Label(frame, text="Audio File:").grid(row=0, column=0, sticky=(tk.W))
        self.audio_file_entry = ttk.Entry(frame)
        self.audio_file_entry.grid(row=0, column=1, sticky=(tk.W))
        ttk.Button(frame, text="Browse", command=lambda: self.select_audio_file(self.audio_file_entry)).grid(row=0, column=2, sticky=(tk.W))

        ttk.Label(frame, text="FPS:").grid(row=1, column=0, sticky=(tk.W))
        self.fps_entry = ttk.Entry(frame)
        self.fps_entry.grid(row=1, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Music Start:").grid(row=2, column=0, sticky=(tk.W))
        self.music_start_entry = ttk.Entry(frame)
        self.music_start_entry.grid(row=2, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Music End:").grid(row=3, column=0, sticky=(tk.W))
        self.music_end_entry = ttk.Entry(frame)
        self.music_end_entry.grid(row=3, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Drums Audio Path:").grid(row=4, column=0, sticky=(tk.W))
        self.drums_audio_path_entry = ttk.Entry(frame)
        self.drums_audio_path_entry.grid(row=4, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Piano Audio Path:").grid(row=5, column=0, sticky=(tk.W))
        self.piano_audio_path_entry = ttk.Entry(frame)
        self.piano_audio_path_entry.grid(row=5, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Bass Audio Path:").grid(row=6, column=0, sticky=(tk.W))
        self.bass_audio_path_entry = ttk.Entry(frame)
        self.bass_audio_path_entry.grid(row=6, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Other Audio Path:").grid(row=7, column=0, sticky=(tk.W))
        self.other_audio_path_entry = ttk.Entry(frame)
        self.other_audio_path_entry.grid(row=7, column=1, sticky=(tk.W))

        ttk.Label(frame, text="BPM File:").grid(row=8, column=0, sticky=(tk.W))
        self.bpm_file_entry = ttk.Entry(frame)
        self.bpm_file_entry.grid(row=8, column=1, sticky=(tk.W))

    def create_spleeter_widgets(self, frame):
        ttk.Label(frame, text="Use Spleeter:").grid(row=0, column=0, sticky=(tk.W))
        self.spleeter_var = tk.IntVar()
        ttk.Checkbutton(frame, variable=self.spleeter_var).grid(row=0, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Stems:").grid(row=1, column=0, sticky=(tk.W))
        self.stems_entry = ttk.Entry(frame)
        self.stems_entry.grid(row=1, column=1, sticky=(tk.W))

    def create_script_widgets(self, frame):
        ttk.Label(frame, text="Speed:").grid(row=0, column=0, sticky=(tk.W))
        self.speed_entry = ttk.Entry(frame)
        self.speed_entry.grid(row=0, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Zoom Speed:").grid(row=1, column=0, sticky=(tk.W))
        self.zoom_speed_entry = ttk.Entry(frame)
        self.zoom_speed_entry.grid(row=1, column=1, sticky=(tk.W))
        
        self.zoom_sound_combo = ttk.Combobox(frame, values=("drums", "other", "piano", "bass"))
        self.zoom_sound_combo.grid(row=2, column=1, sticky=(tk.W))
        
        self.strength_sound_combo = ttk.Combobox(frame, values=("drums", "other", "piano", "bass"))
        self.strength_sound_combo.grid(row=3, column=1, sticky=(tk.W))

    def create_advanced_widgets(self, frame):
        ttk.Label(frame, text="Drums Drop Speed:").grid(row=0, column=0, sticky=(tk.W))
        self.drums_drop_speed_entry = ttk.Entry(frame)
        self.drums_drop_speed_entry.grid(row=0, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Drums Begin Speed:").grid(row=1, column=0, sticky=(tk.W))
        self.drums_begin_speed_entry = ttk.Entry(frame)
        self.drums_begin_speed_entry.grid(row=1, column=1, sticky=(tk.W))

        ttk.Label(frame, text="Zoom Drop Speed:").grid(row=2, column=0, sticky=(tk.W))
        self.zoom_drop_speed_entry = ttk.Entry(frame)
        self.zoom_drop_speed_entry.grid(row=2, column=1, sticky=(tk.W))
        
        self.noise_sound_combo = ttk.Combobox(frame, values=("drums", "other", "piano", "bass"))
        self.noise_sound_combo.grid(row=3, column=1, sticky=(tk.W))
        
        self.contrast_sound_combo = ttk.Combobox(frame, values=("drums", "other", "piano", "bass"))
        self.contrast_sound_combo.grid(row=4, column=1, sticky=(tk.W))
        
        ttk.Label(frame, text="Piano Drop Speed:").grid(row=5, column=0, sticky=(tk.W))
        self.piano_drop_speed_entry = ttk.Entry(frame)
        self.piano_drop_speed_entry.grid(row=5, column=1, sticky=(tk.W))
        
        ttk.Label(frame, text="Bass Drop Speed:").grid(row=6, column=0, sticky=(tk.W))
        self.bass_drop_speed_entry = ttk.Entry(frame)
        self.bass_drop_speed_entry.grid(row=6, column=1, sticky=(tk.W))
                
        ttk.Label(frame, text="Intensity:").grid(row=6, column=0, sticky=(tk.W))
        self.intensity_entry = ttk.Entry(frame)
        self.intensity_entry.grid(row=6, column=1, sticky=(tk.W))
               
    def select_audio_file(self, audio_file_entry):
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav")])
        if file_path:
            if not os.path.exists(file_path):
                print("Selected file does not exist. Please select a valid file.")
                return
            audio_file_entry.delete(0, tk.END)
            audio_file_entry.insert(0, file_path)

    def validate_input(self):
        print("Validating input...")  # Debug
        return True

    def execute_command_threaded(self):
        logging.info("Starting threaded execution...")
        print("Starting threaded execution...")
        try:
            thread = threading.Thread(target=self.execute_command)
            thread.daemon = True
            thread.start()
        except Exception as e:
            logging.critical(f"Failed to start thread: {e}")
            print(f"Failed to start thread: {e}")

    def execute_command(self):
        logging.info("Executing command...")
        try:
            if not self.validate_input():
                logging.warning("Invalid input. Please correct.")
                return

            # Check if venv exists and is activated
            python_venv_path = "venv\\Scripts\\python.exe"  # For Windows
            if not os.path.exists(python_venv_path):
                logging.error("Python virtual environment is not set up correctly. Please check.")
                return

            # Collect the options
            audio_file = self.audio_file_entry.get()
            # Check if the audio file path exists
            if not os.path.exists(audio_file):
                logging.error("Specified audio file does not exist. Please select a valid file.")
                return

            fps = self.fps_entry.get()
            spleeter = self.spleeter_var.get()
            stems = self.stems_entry.get()
            music_start = self.music_start_entry.get()
            music_end = self.music_end_entry.get()
            zoom_sound = self.zoom_sound_combo.get()
            strength_sound = self.strength_sound_combo.get()
            noise_sound = self.noise_sound_combo.get()
            contrast_sound = self.contrast_sound_combo.get()
            drums_drop_speed = self.drums_drop_speed_entry.get()
            drums_audio_path = self.drums_audio_path_entry.get()

            # Initialize the command list with the python path and script name
            cmd = [python_venv_path if os.path.exists(python_venv_path) else "python", "advanced_audio_splitter_keyframes.py"]

            # Append arguments conditionally
            if audio_file:
                cmd.extend(["-f", audio_file])
            if fps:
                cmd.extend(["--fps", fps])
            if spleeter is not None:
                cmd.extend(["--spleeter", str(spleeter)])
            if stems:
                cmd.extend(["--stems", stems])
            if music_start:
                cmd.extend(["--musicstart", music_start])
            if music_end:
                cmd.extend(["--musicend", music_end])
            if zoom_sound:
                cmd.extend(["--zoom_sound", zoom_sound])
            if strength_sound:
                cmd.extend(["--strength_sound", strength_sound])
            if noise_sound:
                cmd.extend(["--noise_sound", noise_sound])
            if contrast_sound:
                cmd.extend(["--contrast_sound", contrast_sound])
            if drums_drop_speed:
                cmd.extend(["--drums_drop_speed", drums_drop_speed])
            if drums_audio_path:
                cmd.extend(["--drums_audio_path", drums_audio_path])

            logging.info(f"Executing command: {' '.join(cmd)}")

            # Execute the command and capture output
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            while True:
                output = process.stdout.readline()
                error_output = process.stderr.readline()

                if output:
                    logging.info(output.strip())
                    print(output.strip())
                if error_output:
                    logging.error(f"Error: {error_output.strip()}")
                    print(f"Error: {error_output.strip()}")

                if process.poll() is not None:
                    break

            if process.returncode != 0:
                logging.error("An error occurred during command execution.")
            else:
                logging.info("Command executed successfully.")

        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            print(f"File not found: {e}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess failed: {e}")
            print(f"Subprocess failed: {e}")
        except Exception as e:
            logging.critical(f"An unhandled exception occurred: {e}")
            print(f"An unhandled exception occurred: {e}")
            
if __name__ == "__main__":
    try:
        logging.info("Inside main...")
        print("Inside main...")
        root = ThemedTk(theme="arc")
        app = AdvancedAudioSplitterUI(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"An unhandled exception occurred: {e}")
        print(f"An unhandled exception occurred: {e}")