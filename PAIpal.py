import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import time
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
try:
    import winsound
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# [AI-NOTE] Helper to get executable path for browse dialogs
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# [AI-NOTE] Main Application Class
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PAIpal")
        self.root.geometry("700x750")
        self.base_width = 700
        self.expanded_width = 1400
        
        # [AI-NOTE] Dark mode colors
        self.bg_dark = "#1e1e1e"
        self.bg_secondary = "#2d2d2d"
        self.bg_input = "#3c3c3c"
        self.fg_light = "#e0e0e0"
        self.fg_gray = "#888888"
        self.accent = "#0078d4"
        
        # Apply dark theme to root
        self.root.configure(bg=self.bg_dark)
        
        # [AI-NOTE] Application State
        self.commands = [] # List of strings
        self.filepath = None # Current file path if editing
        self.currently_playing = None # Track which audio button is playing
        self.audio_start_time = None # Track when audio started
        self.audio_duration = None # Track audio duration
        self.preview_window = None # Track hover preview window
        
        # Voice commands state
        self.voice_commands = [] # List of tuples: (text, filename)
        self.voice_commands_visible = False
        self.voice_panel = None
        
        # Text commands state
        self.text_commands_visible = True
        self.text_panel = None
        
        self.show_start_screen()

    def show_start_screen(self):
        # [AI-NOTE] Clears window and shows start screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # [AI-NOTE] Toggle buttons in top left
        toggle_container = tk.Frame(self.root, bg=self.bg_dark)
        toggle_container.place(x=10, y=10)
        
        # Create three toggle buttons vertically
        self.custom_anim_toggle = ToggleButton(
            toggle_container, self, 
            label="Custom Animations",
            file_path=os.path.join(get_base_path(), "files", "animations.txt"),
            off_text="OFF", on_text="ON"
        )
        self.custom_anim_toggle.pack(pady=5)
        
        self.custom_cmds_toggle = ToggleButton(
            toggle_container, self,
            label="Custom Commands",
            file_path=os.path.join(get_base_path(), "files", "custom-cmds.txt"),
            off_text="OFF", on_text="ON"
        )
        self.custom_cmds_toggle.pack(pady=5)
        
        self.anim_type_toggle = ToggleButton(
            toggle_container, self,
            label="Animation type",
            file_path=os.path.join(get_base_path(), "files", "animation-type.txt"),
            off_text="GIF", on_text="PNG",
            always_green=True,
            invert_display=True
        )
        self.anim_type_toggle.pack(pady=5)
            
        frame = tk.Frame(self.root, bg=self.bg_dark)
        frame.pack(expand=True)
        
        tk.Label(frame, text="Command Generator", font=("Arial", 20, "bold"), 
                bg=self.bg_dark, fg=self.fg_light).pack(pady=20)
        
        tk.Button(frame, text="New Animation/Text Command", command=self.new_file, width=25, height=2,
                 bg=self.bg_secondary, fg=self.fg_light, activebackground=self.accent).pack(pady=10)
        tk.Button(frame, text="Edit Animation/Text Command", command=self.edit_file, width=25, height=2,
                 bg=self.bg_secondary, fg=self.fg_light, activebackground=self.accent).pack(pady=10)
        tk.Button(frame, text="Edit Voice Commands", command=self.edit_voice_commands, width=25, height=2,
                 bg=self.bg_secondary, fg=self.fg_light, activebackground=self.accent).pack(pady=10)

    def new_file(self):
        self.commands = []
        self.filepath = None
        self.show_editor()

    def edit_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, "r") as f:
                    content = f.read().strip()
                    if content:
                        self.commands = content.split("\n")
                    else:
                        self.commands = []
                self.filepath = path
                self.show_editor()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def edit_voice_commands(self):
        """Open editor with voice commands shown and text commands hidden"""
        self.commands = []
        self.filepath = None
        self.show_editor()
        # After showing editor, hide text commands and show voice commands
        self.toggle_text_commands()  # Hide text commands
        self.toggle_voice_commands()  # Show voice commands

    def show_editor(self):
        # [AI-NOTE] Main Editor Interface
        for widget in self.root.winfo_children():
            widget.destroy()

        # [AI-NOTE] Top bar with toggle buttons
        top_bar = tk.Frame(self.root, bg=self.bg_dark, pady=5)
        top_bar.pack(fill=tk.X)
        
        self.text_toggle_btn = tk.Button(top_bar, text="Hide Text Commands", 
                                         command=self.toggle_text_commands,
                                         bg=self.bg_secondary, fg=self.fg_light, 
                                         activebackground=self.accent)
        self.text_toggle_btn.pack(side=tk.LEFT, padx=10)
        
        self.voice_toggle_btn = tk.Button(top_bar, text="Edit Voice Commands", 
                                          command=self.toggle_voice_commands,
                                          bg=self.bg_secondary, fg=self.fg_light, 
                                          activebackground=self.accent)
        self.voice_toggle_btn.pack(side=tk.RIGHT, padx=10)

        # [AI-NOTE] Container for left side (text commands panel)
        self.text_panel = tk.Frame(self.root, bg=self.bg_dark)
        self.text_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # [AI-NOTE] Top Section: Command Buttons
        top_frame = tk.Frame(self.text_panel, padx=10, pady=10, bg=self.bg_dark)
        top_frame.pack(fill=tk.X)

        # Helper to create button rows
        def create_cmd_row(parent, btn_text, label_text, cmd_func, needs_input=False, input_label=None, browse_dir=None, tooltip_text=None):
            row = tk.Frame(parent, bg=self.bg_dark)
            row.pack(fill=tk.X, pady=2)
            
            btn = tk.Button(row, text=btn_text, command=lambda: cmd_func(entry) if needs_input else cmd_func(), 
                          width=15, bg=self.bg_secondary, fg=self.fg_light, activebackground=self.accent)
            btn.pack(side=tk.LEFT)
            
            entry = None
            if needs_input:
                tk.Label(row, text=input_label or "Value:", bg=self.bg_dark, fg=self.fg_light).pack(side=tk.LEFT, padx=5)
                entry = tk.Entry(row, width=20, bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light)
                entry.pack(side=tk.LEFT, padx=5)
                
                # Bind Enter key to trigger the button command
                entry.bind("<Return>", lambda e: cmd_func(entry))
                
                if browse_dir:
                    browse_btn = tk.Button(row, text="Browse", command=lambda: self.browse_file(entry, browse_dir, cmd_func),
                                          bg=self.bg_secondary, fg=self.fg_light, activebackground=self.accent)
                    browse_btn.pack(side=tk.LEFT, padx=5)
            
            tk.Label(row, text=label_text, fg=self.fg_gray, bg=self.bg_dark).pack(side=tk.LEFT, padx=10)
            
            # Add tooltip if provided
            if tooltip_text:
                tooltip_label = tk.Label(row, text="?", bg=self.bg_dark, fg=self.fg_gray,
                                        font=("Arial", 9), cursor="hand2")
                tooltip_label.pack(side=tk.LEFT, padx=(3, 0))
                
                # Bind tooltip events
                tooltip_label.bind("<Enter>", lambda e: self.show_blank_line_tooltip(e, tooltip_text))
                tooltip_label.bind("<Leave>", lambda e: self.hide_blank_line_tooltip())
            
            return entry

        # 1. HIDE_ALL
        create_cmd_row(top_frame, "HIDE_ALL", "hides all images/frames", 
                      lambda: self.add_command("HIDE_ALL"))

        # 2. SHOW [val] (Browse animations)
        create_cmd_row(top_frame, "SHOW", "shows the image/frame entered", 
                      lambda e: self.add_command("SHOW", e), True, "Value:", "animations")

        # 3. HIDE [val] (Browse animations)
        create_cmd_row(top_frame, "HIDE", "hide the specified image/frame", 
                      lambda e: self.add_command("HIDE", e), True, "Value:", "animations")

        # 4. WAIT [int]
        create_cmd_row(top_frame, "WAIT", "wait time in ms before next command", 
                      lambda e: self.add_command("WAIT", e), True, "Integer:")

        # 5. PLAY_AUDIO [filename.wav] (Browse audio)
        create_cmd_row(top_frame, "PLAY_AUDIO", "plays audio from audio/ folder", 
                      lambda e: self.add_command("PLAY_AUDIO", e), True, "Filename:", "audio")

        # 6. OPEN_URL [url]
        create_cmd_row(top_frame, "OPEN_URL", "makes Paicom open the specified URL", 
                      lambda e: self.add_command("OPEN_URL", e), True, "URL:")
        
        # 7. Blank Line
        create_cmd_row(top_frame, "Blank Line", "inserts a blank line", 
                      lambda: self.add_command("BLANK"), tooltip_text="These lines will get skipped/ignored and are just for organizing but you dont have to use them or whatever idk im not your dad lolz")

        # [AI-NOTE] Filename Entry Section
        filename_frame = tk.Frame(self.text_panel, padx=10, pady=5, bg=self.bg_dark)
        filename_frame.pack(fill=tk.X)
        
        tk.Label(filename_frame, text="Output Filename (optional):", bg=self.bg_dark, fg=self.fg_light).pack(side=tk.LEFT, padx=5)
        self.filename_entry = tk.Entry(filename_frame, width=30, bg=self.bg_input, fg=self.fg_light, insertbackground=self.fg_light)
        self.filename_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(filename_frame, text=".txt", fg=self.fg_gray, bg=self.bg_dark).pack(side=tk.LEFT)
        tk.Button(filename_frame, text="Save", command=self.save_file, bg=self.accent, fg=self.fg_light).pack(side=tk.LEFT, padx=10)
        tk.Label(filename_frame, text="(leave empty to be prompted)", fg=self.fg_gray, bg=self.bg_dark, font=("Arial", 8)).pack(side=tk.LEFT, padx=10)

        # [AI-NOTE] Middle Section: Draggable List
        list_frame_container = tk.Frame(self.text_panel, bg=self.bg_dark)
        list_frame_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(list_frame_container, text="Command List (Drag to reorder):", bg=self.bg_dark, fg=self.fg_light).pack(anchor=tk.W)
        
        self.cmd_list_widget = DraggableListFrame(list_frame_container, self.commands, self.on_list_update, self)
        self.cmd_list_widget.pack(fill=tk.BOTH, expand=True)

        # [AI-NOTE] Bottom Section: Actions
        bottom_frame = tk.Frame(self.text_panel, pady=10, bg=self.bg_dark)
        bottom_frame.pack(fill=tk.X)
        
        tk.Button(bottom_frame, text="Back to Menu", command=self.show_start_screen, bg=self.bg_secondary, fg=self.fg_light).pack(side=tk.LEFT, padx=20)

    def browse_file(self, entry_widget, folder_name, cmd_callback=None):
        base_path = get_base_path()
        initial_dir = os.path.join(base_path, folder_name)
        
        # If directory doesn't exist, try creating it or fallback to current dir
        if not os.path.exists(initial_dir):
            try:
                os.makedirs(initial_dir)
            except:
                initial_dir = base_path

        filetypes = [("All Files", "*.*")]
        if folder_name == "audio":
            filetypes = [("WAV Files", "*.wav"), ("All Files", "*.*")]
        
        filepath = filedialog.askopenfilename(initialdir=initial_dir, filetypes=filetypes)
        if filepath:
            filename = os.path.basename(filepath)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
            
            # Automatically trigger the command addition after browsing
            if cmd_callback:
                cmd_callback(entry_widget)

    def add_command(self, cmd_type, entry_widget=None):
        if cmd_type == "BLANK":
            self.commands.append("") # Empty string for blank line
            self.cmd_list_widget.refresh(self.commands)
            return

        val = ""
        if entry_widget:
            val = entry_widget.get().strip()
            
            # Validation
            if cmd_type == "WAIT":
                if not val.isdigit():
                    messagebox.showerror("Error", "WAIT requires an integer value.")
                    return
            elif cmd_type == "OPEN_URL":
                if not val:
                    messagebox.showerror("Error", "URL cannot be empty.")
                    return
            elif cmd_type == "PLAY_AUDIO":
                if not val:
                    messagebox.showerror("Error", "Filename cannot be empty.")
                    return
                # Ensure .wav extension logic
                if not val.lower().endswith(".wav"):
                     val += ".wav"
                # Ensure audio/ prefix logic
                if not val.startswith("audio/"):
                     val = f"audio/{val}"
                
                # Check if user accidentally typed audio/audio/
                # (Simple safeguard, but trusting user input mostly)
            elif cmd_type in ["SHOW", "HIDE"]:
                # Remove .png extension if present (keep only base name)
                if val.lower().endswith(".png"):
                    val = val[:-4]
            
            # For SHOW and HIDE, relax validation to allow strings/filenames
            # as per new requirements.

            if cmd_type == "PLAY_AUDIO":
                 cmd_str = f"PLAY_AUDIO {val}"
            elif cmd_type in ["SHOW", "HIDE", "WAIT", "OPEN_URL"]:
                 cmd_str = f"{cmd_type} {val}"
            
            entry_widget.delete(0, tk.END)
        else:
            cmd_str = cmd_type

        self.commands.append(cmd_str)
        self.cmd_list_widget.refresh(self.commands)

    def on_list_update(self, new_commands):
        self.commands = new_commands

    def play_audio(self, audio_path, play_button):
        if not AUDIO_AVAILABLE:
            messagebox.showerror("Error", "Audio playback not available on this system.")
            return
        
        # If clicking the same button that's playing, stop it
        if self.currently_playing == play_button:
            self.stop_audio()
            return
        
        # Stop any currently playing audio
        if self.currently_playing:
            self.stop_audio()
        
        # Play new audio
        try:
            if not os.path.exists(audio_path):
                messagebox.showerror("Error", f"Audio file not found: {audio_path}")
                return
            
            # Get audio duration
            try:
                with wave.open(audio_path, 'r') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = frames / float(rate)
                    self.audio_duration = duration
            except:
                # If we can't get duration, estimate 5 seconds
                self.audio_duration = 5.0
            
            # Play audio asynchronously (non-blocking)
            winsound.PlaySound(audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            
            play_button.config(text="⏸")
            self.currently_playing = play_button
            self.audio_start_time = time.time()
            
            # Check periodically if audio is still playing
            self.check_audio_status(play_button)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {e}")
            play_button.config(text="▶")
            self.currently_playing = None
    
    def stop_audio(self):
        """Stop currently playing audio"""
        if self.currently_playing:
            # Stop any playing sound immediately
            winsound.PlaySound(None, winsound.SND_PURGE)
            self.currently_playing.config(text="▶")
            self.currently_playing = None
            self.audio_start_time = None
            self.audio_duration = None
    
    def check_audio_status(self, play_button):
        """Check if audio is still playing based on elapsed time"""
        if self.currently_playing != play_button:
            # Button was stopped or another audio started
            return
        
        # Check if button still exists (might have been destroyed by drag/reorder)
        try:
            play_button.winfo_exists()
        except:
            # Button was destroyed, stop tracking it
            self.currently_playing = None
            self.audio_start_time = None
            self.audio_duration = None
            return
        
        # Check if enough time has passed for audio to finish
        if self.audio_start_time and self.audio_duration:
            elapsed = time.time() - self.audio_start_time
            if elapsed >= self.audio_duration:
                # Audio should be finished
                if self.currently_playing == play_button:
                    try:
                        play_button.config(text="▶")
                    except:
                        pass  # Button was destroyed
                    self.currently_playing = None
                    self.audio_start_time = None
                    self.audio_duration = None
                return
        
        # Schedule next check in 100ms
        if self.currently_playing == play_button:
            self.root.after(100, lambda: self.check_audio_status(play_button))

    def save_file(self):
        if not self.commands:
            messagebox.showwarning("Warning", "Command list is empty.")
            return

        # Check if user provided a filename in the text field
        preset_filename = self.filename_entry.get().strip()
        
        # Set save directory to animations folder
        base_path = get_base_path()
        animations_dir = os.path.join(base_path, "animations")
        
        # Create animations folder if it doesn't exist
        if not os.path.exists(animations_dir):
            try:
                os.makedirs(animations_dir)
            except:
                animations_dir = base_path  # Fallback to base path if can't create
        
        if preset_filename:
            # User provided a filename - save to animations folder
            if not preset_filename.lower().endswith(".txt"):
                preset_filename += ".txt"
            
            path = os.path.join(animations_dir, preset_filename)
            
            # Check if file already exists and confirm overwrite
            if os.path.exists(path):
                response = messagebox.askyesno(
                    "Confirm Overwrite",
                    f"The file '{preset_filename}' already exists.\n\nDo you want to overwrite it?"
                )
                if not response:
                    return  # User chose not to overwrite
        else:
            # No filename provided - show the file dialog starting in animations folder
            path = filedialog.asksaveasfilename(
                initialdir=animations_dir,
                title="Save Text File",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
        
        if path:
            try:
                with open(path, "w") as f:
                    f.write("\n".join(self.commands))
                messagebox.showinfo("Success", "File saved successfully!")
                self.filepath = path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def toggle_text_commands(self):
        """Toggle the text commands panel visibility"""
        self.text_commands_visible = not self.text_commands_visible
        
        if self.text_commands_visible:
            self.text_toggle_btn.config(text="Hide Text Commands")
            self.text_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        else:
            self.text_toggle_btn.config(text="Show Text Commands")
            self.text_panel.pack_forget()
        
        # Adjust window size
        self.update_window_size()
    
    def toggle_voice_commands(self):
        """Toggle the voice commands panel visibility"""
        self.voice_commands_visible = not self.voice_commands_visible
        
        if self.voice_commands_visible:
            self.voice_toggle_btn.config(text="Hide Voice Commands")
            self.show_voice_panel()
        else:
            self.voice_toggle_btn.config(text="Edit Voice Commands")
            if self.voice_panel:
                self.voice_panel.destroy()
                self.voice_panel = None
        
        # Adjust window size
        self.update_window_size()
    
    def update_window_size(self):
        """Update window size based on visible panels"""
        if self.voice_commands_visible and self.text_commands_visible:
            self.root.geometry(f"{self.expanded_width}x750")
        elif self.voice_commands_visible and not self.text_commands_visible:
            self.root.geometry(f"{self.base_width}x750")
        elif not self.voice_commands_visible and self.text_commands_visible:
            self.root.geometry(f"{self.base_width}x750")
        else:
            # Both hidden, keep base width
            self.root.geometry(f"{self.base_width}x750")
    
    def load_voice_commands(self):
        """Load voice commands from /custom-commands/commands.txt"""
        base_path = get_base_path()
        custom_commands_dir = os.path.join(base_path, "custom-commands")
        commands_file = os.path.join(custom_commands_dir, "commands.txt")
        
        # Create directory and file if they don't exist
        if not os.path.exists(custom_commands_dir):
            try:
                os.makedirs(custom_commands_dir)
            except:
                pass
        
        if not os.path.exists(commands_file):
            try:
                with open(commands_file, "w") as f:
                    f.write("")  # Create empty file
            except:
                pass
        
        # Load commands
        self.voice_commands = []
        try:
            with open(commands_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Parse format: "text (filename.txt)"
                    if "(" in line and line.endswith(")"):
                        last_paren = line.rfind("(")
                        text_part = line[:last_paren].strip()
                        filename_part = line[last_paren+1:-1].strip()
                        self.voice_commands.append((text_part, filename_part))
                    else:
                        # Malformed line, add with empty filename
                        self.voice_commands.append((line, ""))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load voice commands: {e}")
    
    def save_voice_commands(self):
        """Save voice commands to /custom-commands/commands.txt"""
        base_path = get_base_path()
        custom_commands_dir = os.path.join(base_path, "custom-commands")
        commands_file = os.path.join(custom_commands_dir, "commands.txt")
        
        # Create directory if it doesn't exist
        if not os.path.exists(custom_commands_dir):
            try:
                os.makedirs(custom_commands_dir)
            except:
                messagebox.showerror("Error", "Failed to create custom-commands directory")
                return
        
        # Check if file exists and confirm overwrite
        if os.path.exists(commands_file):
            response = messagebox.askyesno(
                "Confirm Overwrite",
                "The commands.txt file already exists.\n\nDo you want to overwrite it?"
            )
            if not response:
                return
        
        # Save commands
        try:
            with open(commands_file, "w") as f:
                for text, filename in self.voice_commands:
                    if text or filename:  # Don't save completely empty lines
                        f.write(f"{text} ({filename})\n")
            messagebox.showinfo("Success", "Voice commands saved successfully!")
            # Warn user about PAIcom restart requirement
            messagebox.showwarning("Restart Required", 
                                  "If PAIcom is currently running, you'll need to restart it for the changes to take effect.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save voice commands: {e}")
    
    def show_voice_panel(self):
        """Create and show the voice commands panel"""
        self.load_voice_commands()
        
        # Create right panel
        self.voice_panel = tk.Frame(self.root, bg=self.bg_dark, width=700)
        self.voice_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section with Save and Add Line buttons
        voice_top_frame = tk.Frame(self.voice_panel, bg=self.bg_dark)
        voice_top_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(voice_top_frame, text="Save", command=self.save_voice_commands,
                 bg=self.accent, fg=self.fg_light).pack(side=tk.LEFT, padx=5)
        tk.Button(voice_top_frame, text="Add Line", command=self.add_voice_line,
                 bg=self.bg_secondary, fg=self.fg_light).pack(side=tk.LEFT, padx=5)
        
        # List container
        voice_list_container = tk.Frame(self.voice_panel, bg=self.bg_dark)
        voice_list_container.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(voice_list_container, text="Voice Commands:", bg=self.bg_dark, fg=self.fg_light).pack(anchor=tk.W)
        
        # Header row with tooltip using grid for perfect alignment
        header_frame = tk.Frame(voice_list_container, bg=self.bg_dark)
        header_frame.pack(fill=tk.X, pady=(5, 2))
        
        # Configure column weights for proper spacing
        header_frame.columnconfigure(0, weight=0, minsize=65)  # Delete button column
        header_frame.columnconfigure(1, weight=1)  # Phrase column (expands)
        header_frame.columnconfigure(2, weight=0)  # Filename column
        header_frame.columnconfigure(3, weight=0)  # Browse button column
        header_frame.columnconfigure(4, weight=0)  # Drag handle column
        
        # Empty space for delete button area
        tk.Label(header_frame, text="", bg=self.bg_dark).grid(row=0, column=0, sticky="w")
        
        # Phrase label with tooltip
        phrase_label_frame = tk.Frame(header_frame, bg=self.bg_dark)
        phrase_label_frame.grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        tk.Label(phrase_label_frame, text="Phrase", bg=self.bg_dark, fg=self.fg_gray, 
                font=("Arial", 9)).pack(side=tk.LEFT)
        
        # Phrase tooltip question mark
        phrase_tooltip_label = tk.Label(phrase_label_frame, text="?", bg=self.bg_dark, fg=self.fg_gray,
                                font=("Arial", 9), cursor="hand2")
        phrase_tooltip_label.pack(side=tk.LEFT, padx=(3, 0))
        
        # Bind phrase tooltip events
        phrase_tooltip_label.bind("<Enter>", lambda e: self.show_phrase_tooltip(e))
        phrase_tooltip_label.bind("<Leave>", lambda e: self.hide_phrase_tooltip())
        
        # Divider
        tk.Label(phrase_label_frame, text=" | ", bg=self.bg_dark, fg=self.fg_gray,
                font=("Arial", 9)).pack(side=tk.LEFT, padx=(3, 3))
        
        # File label with tooltip
        tk.Label(phrase_label_frame, text="File", bg=self.bg_dark, fg=self.fg_gray,
                font=("Arial", 9)).pack(side=tk.LEFT)
        
        # File tooltip question mark
        file_tooltip_label = tk.Label(phrase_label_frame, text="?", bg=self.bg_dark, fg=self.fg_gray,
                                font=("Arial", 9), cursor="hand2")
        file_tooltip_label.pack(side=tk.LEFT, padx=(3, 0))
        
        # Bind file tooltip events
        file_tooltip_label.bind("<Enter>", lambda e: self.show_file_tooltip(e))
        file_tooltip_label.bind("<Leave>", lambda e: self.hide_file_tooltip())
        
        self.voice_list_widget = VoiceCommandsListFrame(voice_list_container, self.voice_commands, self.on_voice_update, self)
        self.voice_list_widget.pack(fill=tk.BOTH, expand=True)
    
    def add_voice_line(self):
        """Add a blank voice command line at the top"""
        self.voice_commands.insert(0, ("", ""))
        self.voice_list_widget.refresh(self.voice_commands)
    
    def on_voice_update(self, new_voice_commands):
        """Called when voice commands are updated"""
        self.voice_commands = new_voice_commands
    
    def show_phrase_tooltip(self, event):
        """Show tooltip explaining the Phrase field"""
        self.phrase_tooltip = tk.Toplevel(self.root)
        self.phrase_tooltip.wm_overrideredirect(True)
        self.phrase_tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(self.phrase_tooltip,
                        text="This field is for the spoken words that\ntrigger the .txt file call in the field to the right.\n\nTIP: Use phonetic spelling for tricky words\n(e.g., GPT → gi bi ti).",
                        background="#ffffcc", foreground="#000000",
                        relief=tk.SOLID, borderwidth=1, padx=8, pady=5,
                        font=("Arial", 9), justify=tk.LEFT)
        label.pack()
    
    def hide_phrase_tooltip(self):
        """Hide the phrase tooltip"""
        if hasattr(self, 'phrase_tooltip'):
            self.phrase_tooltip.destroy()
            del self.phrase_tooltip
    
    def show_file_tooltip(self, event):
        """Show tooltip explaining the File field"""
        self.file_tooltip = tk.Toplevel(self.root)
        self.file_tooltip.wm_overrideredirect(True)
        self.file_tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(self.file_tooltip,
                        text="This field specifies which .txt file\ngets called when the phrase is spoken.",
                        background="#ffffcc", foreground="#000000",
                        relief=tk.SOLID, borderwidth=1, padx=8, pady=5,
                        font=("Arial", 9), justify=tk.LEFT)
        label.pack()
    
    def hide_file_tooltip(self):
        """Hide the file tooltip"""
        if hasattr(self, 'file_tooltip'):
            self.file_tooltip.destroy()
            del self.file_tooltip
    
    def show_blank_line_tooltip(self, event, tooltip_text):
        """Show tooltip for blank line"""
        self.blank_line_tooltip = tk.Toplevel(self.root)
        self.blank_line_tooltip.wm_overrideredirect(True)
        self.blank_line_tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(self.blank_line_tooltip,
                        text=tooltip_text,
                        background="#ffffcc", foreground="#000000",
                        relief=tk.SOLID, borderwidth=1, padx=8, pady=5,
                        font=("Arial", 9), justify=tk.LEFT)
        label.pack()
    
    def hide_blank_line_tooltip(self):
        """Hide the blank line tooltip"""
        if hasattr(self, 'blank_line_tooltip'):
            self.blank_line_tooltip.destroy()
            del self.blank_line_tooltip


# [AI-NOTE] Custom Widget for Drag-and-Drop List
class DraggableListFrame(tk.Frame):
    def __init__(self, parent, items, update_callback, app):
        super().__init__(parent, bg=app.bg_dark)
        self.items = items
        self.update_callback = update_callback
        self.app = app
        
        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self, bg=app.bg_dark, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bg=app.bg_secondary)
        self.scrollable_frame = tk.Frame(self.canvas, bg=app.bg_dark)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.refresh(self.items)

    def refresh(self, items):
        self.items = items
        
        # Stop any playing audio before destroying widgets
        if self.app.currently_playing:
            self.app.stop_audio()
        
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Rebuild
        for idx, item in enumerate(self.items):
            self.create_row(idx, item)
            
        self.update_callback(self.items)

    def create_row(self, idx, text):
        row = tk.Frame(self.scrollable_frame, bd=1, relief=tk.RAISED, bg=self.app.bg_secondary)
        row.pack(fill=tk.X, pady=1, anchor="n")
        
        display_text = text if text != "" else "_______________"
        
        # Delete Button (add first so it's on the right)
        del_btn = tk.Button(row, text="Delete", fg="#ff4444", bg=self.app.bg_input, 
                           activebackground="#cc0000", command=lambda i=idx: self.delete_item(i))
        del_btn.pack(side=tk.RIGHT)
        
        # Check if this is a SHOW/HIDE command for image preview
        if text.startswith("SHOW ") or text.startswith("HIDE "):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                image_name = parts[1].strip()
                self.add_image_preview(row, image_name)
        
        # Check if this is a PLAY_AUDIO command for play button
        elif text.startswith("PLAY_AUDIO "):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                audio_path_in_cmd = parts[1].strip()
                self.add_play_button(row, audio_path_in_cmd)
        
        # Drag Handle / Label
        lbl = tk.Label(row, text=f" {display_text}", anchor="w", cursor="hand2", width=40, 
                      bg=self.app.bg_secondary, fg=self.app.fg_light)
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Drag Events
        lbl.bind("<Button-1>", lambda e, i=idx: self.start_drag(e, i))
        lbl.bind("<B1-Motion>", self.do_drag)
        lbl.bind("<ButtonRelease-1>", self.stop_drag)

    def delete_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.refresh(self.items)
    
    def add_image_preview(self, row, image_name):
        if not PIL_AVAILABLE:
            return
        
        # Try to find the image file
        base_path = get_base_path()
        
        # Try with and without .png extension
        possible_paths = [
            os.path.join(base_path, "animations", image_name),
            os.path.join(base_path, "animations", f"{image_name}.png"),
        ]
        
        image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break
        
        if not image_path:
            return
        
        try:
            # Load and create thumbnail
            img = Image.open(image_path)
            
            # Calculate thumbnail size (height of ~20px to match button)
            thumb_height = 20
            aspect_ratio = img.width / img.height
            thumb_width = int(thumb_height * aspect_ratio)
            
            img_thumb = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            photo_thumb = ImageTk.PhotoImage(img_thumb)
            
            # Create thumbnail label
            thumb_label = tk.Label(row, image=photo_thumb, bg=self.app.bg_secondary, cursor="hand2")
            thumb_label.image = photo_thumb  # Keep reference
            thumb_label.pack(side=tk.LEFT, padx=5)
            
            # Bind hover events for larger preview
            thumb_label.bind("<Enter>", lambda e: self.show_large_preview(e, image_path))
            thumb_label.bind("<Leave>", lambda e: self.hide_large_preview())
            
        except Exception as e:
            pass  # Silently fail if image can't be loaded
    
    def show_large_preview(self, event, image_path):
        if not PIL_AVAILABLE or self.app.preview_window:
            return
        
        try:
            # Create toplevel window for preview
            preview = tk.Toplevel(self.app.root)
            preview.overrideredirect(True)  # No window decorations
            preview.attributes('-topmost', True)
            
            # Load image at larger size
            img = Image.open(image_path)
            
            # Scale to max 300px while maintaining aspect ratio
            max_size = 300
            aspect_ratio = img.width / img.height
            
            if img.width > img.height:
                new_width = min(max_size, img.width)
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = min(max_size, img.height)
                new_width = int(new_height * aspect_ratio)
            
            img_preview = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo_preview = ImageTk.PhotoImage(img_preview)
            
            label = tk.Label(preview, image=photo_preview, bg=self.app.bg_dark, bd=2, relief=tk.RAISED)
            label.image = photo_preview  # Keep reference
            label.pack()
            
            # Position to the right of cursor
            x = event.x_root + 20
            y = event.y_root - new_height // 2
            preview.geometry(f"+{x}+{y}")
            
            self.app.preview_window = preview
            
        except Exception as e:
            pass
    
    def hide_large_preview(self):
        if self.app.preview_window:
            self.app.preview_window.destroy()
            self.app.preview_window = None
    
    def add_play_button(self, row, audio_path_in_cmd):
        if not AUDIO_AVAILABLE:
            return
        
        # Build full audio path
        base_path = get_base_path()
        # audio_path_in_cmd is like "audio/sound.wav"
        audio_path = os.path.join(base_path, audio_path_in_cmd)
        
        # Create play button
        play_btn = tk.Button(row, text="▶", width=2, bg=self.app.bg_input, fg=self.app.fg_light,
                            command=lambda: self.app.play_audio(audio_path, play_btn))
        play_btn.pack(side=tk.LEFT, padx=5)

    # -- Drag and Drop Logic --
    def start_drag(self, event, index):
        self.drag_start_index = index
        self.drag_data = {"y": event.y_root, "item": self.items[index]}
        
    def do_drag(self, event):
        pass

    def stop_drag(self, event):
        x, y = self.canvas.winfo_pointerxy()
        widget_under_mouse = self.canvas.winfo_containing(x, y)
        
        if not widget_under_mouse:
            return

        target_index = -1
        rows = self.scrollable_frame.winfo_children()
        
        for i, row in enumerate(rows):
            row_y_root = row.winfo_rooty()
            row_h = row.winfo_height()
            
            if row_y_root <= y <= row_y_root + row_h:
                target_index = i
                break
        
        if target_index != -1 and target_index != self.drag_start_index:
            item = self.items.pop(self.drag_start_index)
            self.items.insert(target_index, item)
            self.refresh(self.items)


# [AI-NOTE] Voice Commands List Widget
class VoiceCommandsListFrame(tk.Frame):
    def __init__(self, parent, items, update_callback, app):
        super().__init__(parent, bg=app.bg_dark)
        self.items = items  # List of tuples: (text, filename)
        self.update_callback = update_callback
        self.app = app
        
        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self, bg=app.bg_dark, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bg=app.bg_secondary)
        self.scrollable_frame = tk.Frame(self.canvas, bg=app.bg_dark)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.refresh(self.items)

    def refresh(self, items):
        self.items = items
        
        # Stop any playing audio before destroying widgets
        if self.app.currently_playing:
            self.app.stop_audio()
        
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Rebuild
        for idx, item in enumerate(self.items):
            self.create_row(idx, item)
            
        self.update_callback(self.items)

    def create_row(self, idx, item):
        text_val, filename_val = item
        
        row = tk.Frame(self.scrollable_frame, bd=1, relief=tk.RAISED, bg=self.app.bg_secondary)
        row.pack(fill=tk.X, pady=1, anchor="n")
        
        # Configure column weights to match header
        row.columnconfigure(0, weight=0, minsize=65)  # Delete button column
        row.columnconfigure(1, weight=1)  # Phrase column (expands)
        row.columnconfigure(2, weight=0)  # Filename column
        row.columnconfigure(3, weight=0)  # Browse button column
        row.columnconfigure(4, weight=0)  # Drag handle column
        
        # Delete Button (column 0)
        del_btn = tk.Button(row, text="Delete", fg="#ff4444", bg=self.app.bg_input, 
                           activebackground="#cc0000", command=lambda i=idx: self.delete_item(i))
        del_btn.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        
        # Text field (column 1) - wider for longer text
        text_entry = tk.Entry(row, width=50, bg=self.app.bg_input, fg=self.app.fg_light, insertbackground=self.app.fg_light)
        text_entry.insert(0, text_val)
        text_entry.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        text_entry.bind("<FocusOut>", lambda e, i=idx, entry=text_entry: self.update_text(i, entry))
        
        # Filename field (column 2) - wider for longer filenames
        filename_entry = tk.Entry(row, width=25, bg=self.app.bg_input, fg=self.app.fg_light, insertbackground=self.app.fg_light)
        filename_entry.insert(0, filename_val)
        filename_entry.grid(row=0, column=2, sticky="w", padx=2, pady=2)
        filename_entry.bind("<FocusOut>", lambda e, i=idx, entry=filename_entry: self.update_filename(i, entry))
        
        # Browse button (column 3)
        browse_btn = tk.Button(row, text="Browse", command=lambda i=idx, entry=filename_entry: self.browse_animation(i, entry),
                              bg=self.app.bg_secondary, fg=self.app.fg_light, activebackground=self.app.accent)
        browse_btn.grid(row=0, column=3, sticky="w", padx=2, pady=2)
        
        # Drag Handle (column 4)
        drag_label = tk.Label(row, text="☰", cursor="hand2", bg=self.app.bg_secondary, fg=self.app.fg_gray)
        drag_label.grid(row=0, column=4, sticky="w", padx=2, pady=2)
        
        # Drag Events
        drag_label.bind("<Button-1>", lambda e, i=idx: self.start_drag(e, i))
        drag_label.bind("<B1-Motion>", self.do_drag)
        drag_label.bind("<ButtonRelease-1>", self.stop_drag)

    def update_text(self, index, entry):
        """Update text when entry loses focus"""
        if 0 <= index < len(self.items):
            new_text = entry.get()
            old_text, filename = self.items[index]
            self.items[index] = (new_text, filename)
            self.update_callback(self.items)

    def update_filename(self, index, entry):
        """Update filename when entry loses focus"""
        if 0 <= index < len(self.items):
            new_filename = entry.get()
            text, old_filename = self.items[index]
            self.items[index] = (text, new_filename)
            self.update_callback(self.items)

    def browse_animation(self, index, entry_widget):
        """Browse for .txt file in animations folder"""
        base_path = get_base_path()
        animations_dir = os.path.join(base_path, "animations")
        
        if not os.path.exists(animations_dir):
            try:
                os.makedirs(animations_dir)
            except:
                animations_dir = base_path
        
        filepath = filedialog.askopenfilename(
            initialdir=animations_dir, 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if filepath:
            filename = os.path.basename(filepath)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
            
            # Update the item
            if 0 <= index < len(self.items):
                text, _ = self.items[index]
                self.items[index] = (text, filename)
                self.update_callback(self.items)

    def delete_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.refresh(self.items)

    # -- Drag and Drop Logic --
    def start_drag(self, event, index):
        self.drag_start_index = index
        self.drag_data = {"y": event.y_root, "item": self.items[index]}
        
    def do_drag(self, event):
        pass

    def stop_drag(self, event):
        x, y = self.canvas.winfo_pointerxy()
        widget_under_mouse = self.canvas.winfo_containing(x, y)
        
        if not widget_under_mouse:
            return

        target_index = -1
        rows = self.scrollable_frame.winfo_children()
        
        for i, row in enumerate(rows):
            row_y_root = row.winfo_rooty()
            row_h = row.winfo_height()
            
            if row_y_root <= y <= row_y_root + row_h:
                target_index = i
                break
        
        if target_index != -1 and target_index != self.drag_start_index:
            item = self.items.pop(self.drag_start_index)
            self.items.insert(target_index, item)
            self.refresh(self.items)


# [AI-NOTE] Phone-style Toggle Button Widget
class ToggleButton(tk.Frame):
    def __init__(self, parent, app, label, file_path, off_text="OFF", on_text="ON", always_green=False, invert_display=False):
        super().__init__(parent, bg=app.bg_dark)
        self.app = app
        self.label_text = label
        self.file_path = file_path
        self.off_text = off_text
        self.on_text = on_text
        self.always_green = always_green
        self.invert_display = invert_display  # Invert visual display but keep file values
        self.state = None  # Will be 0 (on) or 1 (off) or None (error)
        
        # Create label
        tk.Label(self, text=label, bg=app.bg_dark, fg=app.fg_light, 
                font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        # Create canvas for toggle switch
        self.canvas = tk.Canvas(self, width=50, height=24, bg=app.bg_dark, 
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=5)
        
        # Create state label (ON/OFF/GIF/PNG)
        self.state_label = tk.Label(self, text="", bg=app.bg_dark, fg=app.fg_light,
                                   font=("Arial", 9))
        self.state_label.pack(side=tk.LEFT, padx=5)
        
        # Load state and draw
        self.load_state()
        self.draw_toggle()
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.toggle_click)
    
    def load_state(self):
        """Load state from file"""
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(self.file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # Check if file exists
            if not os.path.exists(self.file_path):
                # Create file with default value 1 (OFF)
                with open(self.file_path, "w") as f:
                    f.write("1")
                self.state = 1
            else:
                # Read file
                with open(self.file_path, "r") as f:
                    content = f.read().strip()
                    if content == "0":
                        self.state = 0  # ON
                    elif content == "1":
                        self.state = 1  # OFF
                    else:
                        self.state = None  # ERROR
        except Exception as e:
            self.state = None
    
    def save_state(self):
        """Save state to file"""
        try:
            with open(self.file_path, "w") as f:
                f.write(str(self.state))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save toggle state: {e}")
    
    def draw_toggle(self):
        """Draw the toggle switch"""
        self.canvas.delete("all")
        
        if self.state is None:
            # Error state - show question mark
            self.canvas.create_text(25, 12, text="?", font=("Arial", 16, "bold"),
                                   fill="#ff4444")
            # Add hover tooltip
            self.canvas.bind("<Enter>", lambda e: self.show_error_tooltip())
            self.canvas.bind("<Leave>", lambda e: self.hide_tooltip())
        else:
            # Remove error tooltip bindings
            self.canvas.unbind("<Enter>")
            self.canvas.unbind("<Leave>")
            
            # Get display state (inverted if needed)
            display_state = (1 - self.state) if self.invert_display else self.state
            
            # Determine colors
            if self.always_green:
                bg_color = "#4CAF50"  # Always green
            elif display_state == 0:
                bg_color = "#4CAF50"  # Green when ON (0)
            else:
                bg_color = "#666666"  # Grey when OFF (1)
            
            # Draw rectangle background
            self.canvas.create_rectangle(2, 2, 48, 22, fill=bg_color, outline="")
            
            # Draw rectangle (slider)
            if display_state == 0:
                # ON position (right)
                slider_x = 28
            else:
                # OFF position (left)
                slider_x = 4
            
            self.canvas.create_rectangle(slider_x, 4, slider_x+18, 20, 
                                        fill="#ffffff", outline="")
        
        # Update state label next to toggle
        self.update_state_label()
    
    def toggle_click(self, event):
        """Handle toggle click"""
        if self.state is None:
            # Error state - don't allow clicking
            return
        
        # Toggle state
        self.state = 0 if self.state == 1 else 1
        
        # Save and redraw
        self.save_state()
        self.draw_toggle()
    
    def update_state_label(self):
        """Update the text label next to the toggle"""
        if self.state is None:
            self.state_label.config(text="ERROR")
        else:
            # Get display state (inverted if needed)
            display_state = (1 - self.state) if self.invert_display else self.state
            
            if display_state == 0:
                self.state_label.config(text=self.on_text)
            else:
                self.state_label.config(text=self.off_text)
    
    def show_error_tooltip(self):
        """Show tooltip explaining the error"""
        self.tooltip = tk.Toplevel(self.app.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{self.winfo_pointerx()+10}+{self.winfo_pointery()+10}")
        
        # Show full path relative to base or full path
        relative_path = os.path.relpath(self.file_path, get_base_path())
        
        label = tk.Label(self.tooltip, 
                        text=f"Error: Invalid value in\n{relative_path}\nExpected 0 or 1",
                        background="#ffcccc", foreground="#000000",
                        relief=tk.SOLID, borderwidth=1, padx=5, pady=5,
                        font=("Arial", 9))
        label.pack()
    
    def hide_tooltip(self):
        """Hide tooltip"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
