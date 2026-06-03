# Terminal Chess Bot (Offline)

A fully offline terminal chess application with a minimax + alpha-beta engine, optional PyTorch evaluation model, and a training pipeline. Now also includes a **PyQt6 GUI version** with Windows installer!

## Versions

### 1. Terminal CLI Version (Original)

Run entirely in the terminal/Linux environment.

```bash
./run.sh --side b
```

**Features:**
- ASCII board with Unicode pieces
- Terminal-based UI with colors
- Perfect for Linux/WSL
- Lightweight and fast

### 2. GUI Version (NEW)

Full graphical interface with Windows installer.

```bash
python gui_launcher.py
```

**Features:**
- Interactive chess board
- Click-to-play interface
- Windows installer
- Professional GUI

---

## Features

- Fully offline (no internet required)
- Choose White or Black at startup
- UCI move input (example: e2e4)
- Undo moves, restart, and move history
- Minimax with alpha-beta pruning (configurable depth)
- ML-based evaluation using PyTorch (optional)
- Check, checkmate, and stalemate detection
- Board evaluation display after each move

---

## Installation (Linux/WSL)

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
PIP_DEFAULT_TIMEOUT=1000 pip install --index-url https://download.pytorch.org/whl/cpu torch
pip install -r requirements.txt
chmod +x run.sh
```

## Run the Terminal Game

```bash
./run.sh --side b
```

Or:

```bash
PYTHONPATH=. python3 -m chessbot.main --depth 4 --side b
```

---

## Installation (Windows GUI)

### Quick Start

1. **Double-click `ChessBotSetup.exe`** (recommended)
   - Runs installer with setup wizard
   - Creates Start Menu shortcuts
   - Standard installation

2. **Or run `ChessBot.exe` directly**
   - Portable executable
   - No installation needed

### Build from Source

1. Install Python 3.8+
2. Run the build script:

```bash
build_windows.bat
```

This creates:
- `dist/ChessBot.exe` - Portable executable
- `ChessBotSetup.exe` - Windows installer

---

## GUI Quick Start

See [GUI_QUICKSTART.md](GUI_QUICKSTART.md) for full instructions.

**Basic flow:**
1. Click "Start Game"
2. Choose your side (White/Black)
3. Enter opponent moves in UCI notation (e.g., `e2e4`)
4. Bot plays automatically
5. Edit bot moves if needed with "Undo Bot Move"

---

## Training Workflow

Train from PGN files (optional Stockfish evals):

```bash
PYTHONPATH=. python3 -m chessbot.train \
  --pgn data/games.pgn \
  --out models/eval_mlp.pt \
  --max-positions 20000 \
  --epochs 4 \
  --batch-size 256 \
  --lr 1e-3
```

With Stockfish for stronger labels:

```bash
PYTHONPATH=. python3 -m chessbot.train \
  --pgn data/games.pgn \
  --out models/eval_mlp.pt \
  --stockfish-path /usr/bin/stockfish \
  --stockfish-depth 12
```

Then run with ML evaluation:

```bash
PYTHONPATH=. python3 -m chessbot.main --use-ml --model-path models/eval_mlp.pt
```

---

## Project Structure

```
terminal-chess/
├── chessbot/
│   ├── main.py           # Terminal CLI game loop
│   ├── gui.py            # PyQt6 GUI application
│   ├── engine.py         # Minimax + alpha-beta engine
│   ├── model.py          # PyTorch evaluation model
│   ├── train.py          # Training pipeline
│   ├── ui.py             # Terminal UI rendering
│   ├── utils.py          # Utilities and evaluation
│   └── future.py         # Future feature stubs
├── gui_launcher.py       # Entry point for GUI
├── build_exe.py          # PyInstaller build script
├── build_windows.bat     # Windows build helper
├── requirements.txt      # CLI dependencies
├── requirements-gui.txt  # GUI dependencies
├── chess_bot_installer.nsi # NSIS installer script
├── run.sh                # CLI launcher
└── README.md             # This file
```

---

## Optional Future-Ready Features

- Opening book integration (stubbed)
- Endgame tablebase support (stubbed)
- Self-play training pipeline (stubbed)
- Reinforcement learning hooks (stubbed)

## Notes

- The ML model is optional; the engine works with classic evaluation by default
- The app is fully offline and uses no network resources
- GUI version includes all terminal features accessible through the interface

