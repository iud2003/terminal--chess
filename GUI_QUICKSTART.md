# Chess Bot - GUI Edition Quick Start

## Installation

### Option A: Install from Installer (Recommended)

1. Download `ChessBotSetup.exe`
2. Run the installer
3. Follow the setup wizard
4. Launch from Start Menu → Chess Bot

### Option B: Run Portable Executable

1. Download `ChessBot.exe`
2. Double-click to run (no installation needed)

## How to Play

1. **Start Game** - Click to begin
2. **Choose Your Side** - Select White or Black
3. **Enter Opponent Moves** - Type UCI notation (e.g., `e2e4`)
4. **Bot Plays** - Automatically calculates and shows its move
5. **Edit Bot** - Click "Undo Bot Move" if you want to change the bot's move

## Controls

| Button | Action |
|--------|--------|
| Start Game | Begin a new game |
| Play Move | Submit your opponent's move |
| Undo Bot Move | Remove bot's last move and re-play |
| Restart | Start over |

## Settings

- **Engine Depth** - Higher = stronger bot, slower moves (1-8, default 4)
- **Your Side** - Choose White or Black

## UCI Move Format

- Format: `<from><to>` (e.g., `e2e4`)
- Squares: `a1` (bottom-left) to `h8` (top-right)
- For promotion: add piece (e.g., `e7e8q` for queen promotion)

## Examples

```
Move pawn from e2 to e4: e2e4
Move knight from g1 to f3: g1f3
Promote pawn to queen: e7e8q
```

## Troubleshooting

- **"Invalid UCI format"** - Check move format (e.g., `e2e4`)
- **"That move is not legal"** - The move violates chess rules
- **Bot takes long** - Increase depth or wait; higher depth = stronger analysis
- **Slow first startup** - Windows is unpacking the Python runtime

## System Requirements

- Windows 7 or later
- ~300 MB disk space
- No internet required (fully offline)
