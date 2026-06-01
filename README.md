# Antigravity Widget

A floating, translucent, and interactive widget for Windows that automatically displays real-time AI model limits, status, and reset times straight from your local Antigravity IDE instance.

## Features
- **Auto-Discovery**: Instantly locates the local Antigravity IDE Language Server to securely fetch your personal limits.
- **Auto-Reconnect**: Seamlessly reconnects if the IDE restarts or changes ports.
- **Flicker-Free UI**: Smooth data updates without interface flickering.
- **Reset Timers**: Shows exactly how many minutes are left until your model limits reset.
- **Always on Top**: Acts as an unobtrusive Heads-Up Display (HUD) in the corner of your screen.

## Prerequisites
- Windows OS
- Python 3.10+ (if running from source)
- The [Antigravity IDE](https://antigravity.dev) must be running on your system for the widget to extract the API token and port from its local logs.

## Setup Instructions

### 1. Download & Run (Ready-made App)
If you don't want to deal with Python and just want to run the application directly:
1. Navigate to the `releases` folder in this repository.
2. Download the `AntigravityWidget.exe` file.
3. Double-click the file to run it. No installation is required!

### 2. Running from source
If you want to run the python code directly:
1. Clone this repository to your local machine.
2. Install the necessary dependencies:
   ```bash
   pip install PyQt6 psutil
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### 3. Building your own App (.exe)
If you made changes to the code and want to package it into a single `.exe` file, use PyInstaller:
```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "AntigravityWidget" "main.py"
```
The final standalone app will be generated inside the `dist/` folder as a single `AntigravityWidget.exe` file.

## Important Note
This application reads the internal logs (`%APPDATA%\Antigravity IDE\logs`) to dynamically find the correct process ID and authorization tokens. **Do not share your authorization tokens**. By sharing only the application, the app securely uses the tokens of whoever is running it on their local machine.
