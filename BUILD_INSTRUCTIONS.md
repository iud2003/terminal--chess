# Build Instructions for Chess Bot GUI

## Prerequisites

1. **Install Python packages** (GUI + build tools):
   ```bash
   pip install -r requirements-gui.txt
   pip install pyinstaller
   ```

2. **Install NSIS** (for installer):
   - Download: https://nsis.sourceforge.io/download
   - Add to PATH or use full path

## Build Steps

### Step 1: Build Executable with PyInstaller

```bash
python build_exe.py
```

This creates `dist/ChessBot.exe` (standalone executable).

### Step 2: Create Windows Installer

```bash
makensis chess_bot_installer.nsi
```

This creates `ChessBotSetup.exe` (installer with setup wizard).

## Result

- **ChessBot.exe** - Portable executable (can run without installation)
- **ChessBotSetup.exe** - Installer (recommended for end users)

## Testing

```bash
# Test PyInstaller executable
dist\ChessBot.exe

# After running installer, find in:
# C:\Program Files\ChessBot\ChessBot.exe
```

## Notes

- The `.exe` files require the Python runtime dependencies (torch, PyQt6, etc.) to be bundled
- First run may take a few seconds as Python unpacks
- For icon, add a `chess_icon.ico` file before building
