# PyInstaller build script for Windows
# Usage: python build_exe.py

import os
import subprocess
import shutil

def build_exe():
    """Build executable using PyInstaller."""
    print("Building Chess Bot GUI Executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--icon=chess_icon.ico",  # Optional: add icon
        "--add-data=chessbot:chessbot",
        "--name=ChessBot",
        "gui_launcher.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Executable built successfully!")
        print(f"Location: dist/ChessBot.exe")
    else:
        print("✗ Build failed!")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    build_exe()
