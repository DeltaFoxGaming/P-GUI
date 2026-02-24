# PAIpal

A GUI tool for creating animation command files and voice commands for PAIcom. Features drag-and-drop functionality, image previews, and audio playback testing.

## NOTICE

Place PAIpal.exe or PAIpal.py in the root folder for PAIcom
"/PAIcom (furry computer assistant)" for best results

Otherwise this will create its own "animations, audio, file" folders to reference.

## Features

### Animation/Text Command Editor
- **Command buttons** for HIDE_ALL, SHOW, HIDE, WAIT, PLAY_AUDIO, OPEN_URL
- **Image previews** - Thumbnail previews with hover zoom for SHOW/HIDE commands
- **Audio playback** - Play/pause buttons to test audio files before adding
- **Drag-and-drop reordering** - Reorder commands by dragging
- **Auto file extensions** - Automatically manages .wav extensions (strips .png from images)
- **Quick save** - Pre-fill filename for instant saving to animations folder

### Voice Command Editor
- **Phrase-to-file mapping** - Link voice phrases to command files
- **Dual text fields** - Edit both phrase and target filename
- **Browse animations** - Select .txt files from animations folder
- **Drag-and-drop** - Reorder voice commands easily
- **Side-by-side editing** - Work on both command types simultaneously

### Toggle Settings (Main Menu)
- **Custom Animations** - Toggle custom animation support (ON/OFF)
- **Custom Commands** - Toggle custom command support (ON/OFF)
- **Animation Type** - Switch between PNG/GIF format preference

## Installation & Usage

### Option 1: Pre-built Executable (Recommended)

1. Download `PAIpal.exe` from [Releases](../../releases)
2. Run the .exe - no installation needed!
3. The app will create necessary folders (`animations/`, `audio/`, `custom-commands/`, `files/`)

**System Requirements:**
- Windows 10/11
- No Python or dependencies needed

### Option 2: Run from Source

**Requirements:**
- Python 3.6 or newer
- Pillow library for image support

**Setup:**
```bash
# Clone or download this repository
cd GUI

# Install dependencies
pip install -r requirements.txt

# Run the application
python PAIpal.py
```

### Option 3: Build Your Own Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build the .exe
pyinstaller PAIpal.spec

# Find your executable in the dist/ folder
```

## How to Use

### Creating Animation Commands

1. Click **"New Animation/Text Command"** from the main menu
2. Use command buttons to add:
   - `HIDE_ALL` - Hides all images/frames
   - `SHOW [name]` - Shows specific image (omit .png extension)
   - `HIDE [name]` - Hides specific image
   - `WAIT [milliseconds]` - Pause between commands
   - `PLAY_AUDIO [filename]` - Play audio file (auto-adds .wav)
   - `OPEN_URL [url]` - Open a URL
3. **Drag to reorder** commands in the list
4. **Enter filename** in the "Output Filename" field (optional)
5. Click **"Save"** to save to `animations/` folder

### Creating Voice Commands

1. Click **"Edit Voice Commands"** from main menu, or
2. Click **"Edit Voice Commands"** button in top-right while editing
3. Click **"Add Line"** to add a new voice command
4. Enter the **phrase** (e.g., "hey paicom play music")
5. Enter the **filename** of the command file to execute (e.g., "music.txt")
6. Click **"Save"** when done
7. **Important:** Restart PAIcom for voice command changes to take effect

### Folder Structure

The application creates and uses these folders:

```
GUI/
├── animations/          # Animation command .txt files and images
├── audio/              # .wav audio files for PLAY_AUDIO commands
├── custom-commands/    # Voice commands (commands.txt)
└── files/              # Toggle settings (.txt files)
```

## Tips & Tricks

- **Enter key shortcut** - Press Enter after typing in any input field to add the command
- **Browse auto-adds** - Selecting a file in Browse dialog automatically adds the command
- **Image previews** - Hover over thumbnails for larger preview
- **Test audio** - Click play buttons to preview audio before saving
- **Hide panels** - Toggle visibility of Text or Voice commands for focused editing

## Configuration Files

Toggle settings are stored in `/files/`:
- `animations.txt` - Custom Animations (1=OFF, 0=ON)
- `custom-cmds.txt` - Custom Commands (1=OFF, 0=ON)
- `animation-type.txt` - Animation Type (1=PNG, 0=GIF)

## Building from Source

If you want to modify and rebuild:

1. Edit `gui_generator_v3.py`
2. Test with `python gui_generator_v3.py`
3. Rebuild: `pyinstaller gui_generator_v3.spec --clean`
4. New .exe appears in `dist/` folder

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Credits

Created by DeltaFoxGaming for the PAIcom community.

## Support

For issues or questions, please open an issue on GitHub.
