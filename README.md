# Terminal Chess Bot (Offline)

A Linux-friendly, fully offline terminal chess application with a minimax + alpha-beta engine, optional PyTorch evaluation model, and a training pipeline. The UI runs entirely in the terminal and supports UCI move input.

## Features

- Fully offline CLI gameplay on Linux
- Choose White or Black at startup
- UCI move input (example: e2e4)
- Undo moves, restart, and move history
- Minimax with alpha-beta pruning (configurable depth)
- ML-based evaluation using PyTorch (optional)
- ASCII board rendering with ANSI colors
- Check, checkmate, and stalemate detection
- Board evaluation display after each move

## Project Structure

- chessbot/main.py: main game loop and CLI
- chessbot/engine.py: minimax engine and move selection
- chessbot/model.py: PyTorch evaluation model and board encoding
- chessbot/train.py: training pipeline
- chessbot/utils.py: evaluation helpers and utilities
- chessbot/ui.py: ASCII board rendering and UI helpers
- chessbot/future.py: optional feature stubs for future work

## Installation (Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Game

```bash
./run.sh
```

Or:

```bash
PYTHONPATH=. python3 -m chessbot.main --depth 4
```

## Training Workflow

Train from PGN files (optional Stockfish evals if you install Stockfish):

```bash
PYTHONPATH=. python3 -m chessbot.train \
  --pgn data/games.pgn \
  --out models/eval_mlp.pt \
  --max-positions 20000 \
  --epochs 4 \
  --batch-size 256 \
  --lr 1e-3
```

To use Stockfish for stronger labels:

```bash
PYTHONPATH=. python3 -m chessbot.train \
  --pgn data/games.pgn \
  --out models/eval_mlp.pt \
  --stockfish-path /usr/bin/stockfish \
  --stockfish-depth 12
```

Then run the game with ML evaluation:

```bash
PYTHONPATH=. python3 -m chessbot.main --use-ml --model-path models/eval_mlp.pt
```

## Example Gameplay

```
$ ./run.sh
Choose side (w/b): w

8  r n b q k b n r
7  p p p p p p p p
6  . . . . . . . .
5  . . . . . . . .
4  . . . . . . . .
3  . . . . . . . .
2  P P P P P P P P
1  R N B Q K B N R
   a b c d e f g h

Eval: +0.00 | Turn: White
Your move (uci or command): e2e4
Bot thinking at depth 4...
Bot move: e7e5
```

## Optional Future-Ready Features

- Opening book integration (stubbed)
- Endgame tablebase support (stubbed)
- Self-play training pipeline (stubbed)
- Reinforcement learning hooks (stubbed)

## Notes

- The ML model is optional; the engine works with classic evaluation by default.
- The app is fully offline and uses no network resources.
