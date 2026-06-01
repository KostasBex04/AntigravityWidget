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

### 1. Running from source
1. Clone this repository to your local machine.
2. Install the necessary dependencies:
   ```bash
   pip install PyQt6 psutil
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### 2. Building the standalone App (.exe)
If you want to package the app into a standalone executable that runs without installing Python, use PyInstaller:
```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --name "AntigravityWidget" "main.py"
```
The final standalone app will be generated inside the `dist/AntigravityWidget` folder. You can zip this folder and share it directly with friends.

## Important Note
This application reads the internal logs (`%APPDATA%\Antigravity IDE\logs`) to dynamically find the correct process ID and authorization tokens. **Do not share your authorization tokens**. By sharing only the application, the app securely uses the tokens of whoever is running it on their local machine.
