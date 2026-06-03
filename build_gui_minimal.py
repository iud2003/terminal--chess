"""
Optimized PyInstaller build script for Chess Bot GUI
Excludes PyTorch to speed up build time (model not active in GUI yet)
"""

import os
import subprocess
import shutil
import sys

def build_exe():
    """Build executable using PyInstaller with minimal dependencies."""
    print("🏗️  Building Chess Bot GUI Executable (Optimized)...")
    print("Note: PyTorch excluded (not required for GUI gameplay)\n")
    
    # Clean up old builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("✓ Cleaned old dist folder\n")
    
    # PyInstaller command with excluded modules
    # Use python -m to ensure pyinstaller runs from activated venv
    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=ChessBot",
        "--add-data=chessbot:chessbot",
        "--exclude-module=torch",
        "--exclude-module=numpy.lib.mixins",
        "--optimize=2",
        "gui_launcher.py"
    ]
    
    print(f"Running: {' '.join(cmd[2:])}\n")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        exe_path = "dist/ChessBot.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024*1024)
            print(f"\n✅ SUCCESS! Executable built!")
            print(f"📦 Location: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            print(f"\n🎮 To run: Double-click dist/ChessBot.exe")
        else:
            print("❌ Build completed but exe not found")
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = build_exe()
    exit(0 if success else 1)
