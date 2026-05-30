from __future__ import annotations

import argparse
import sys
from typing import List

import chess

from .engine import ChessEngine, EngineConfig
from .model import load_model
from .ui import game_status, render_board
from .utils import format_eval


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline terminal chess bot.")
    parser.add_argument("--depth", type=int, default=4, help="Search depth (default: 4)")
    parser.add_argument("--use-ml", action="store_true", help="Use the ML evaluation model")
    parser.add_argument("--model-path", default="models/eval_mlp.pt", help="Path to model file")
    parser.add_argument("--side", choices=["w", "b"], default=None, help="Play as white or black")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--human-plays", action="store_true", help="You play your side; bot plays opponent")
    return parser.parse_args()


def prompt_side(default_side: str | None) -> chess.Color:
    if default_side == "w":
        return chess.WHITE
    if default_side == "b":
        return chess.BLACK
    while True:
        print("\n=== CHESS BOT ===")
        print("Choose your side (the bot will play for you):")
        choice = input("Enter your side (w=White, b=Black): ").strip().lower()
        if choice in ("w", "white"):
            print("You chose WHITE. Bot will play White. You enter Black's moves.\n")
            return chess.WHITE
        if choice in ("b", "black"):
            print("You chose BLACK. Bot will play Black. You enter White's moves.\n")
            return chess.BLACK
        print("Please enter w or b.")


def print_help():
    print("\nCommands:")
    print("  <uci move> : Enter move in UCI notation (e.g., e2e4, g1f3)")
    print("  undo       : Undo last move (if bot just moved, undo only bot's move)")
    print("  undo2      : Undo last 2 moves (full turn)")
    print("  editbot    : Edit bot's last move")
    print("  restart    : Restart the game")
    print("  history    : Show move history")
    print("  depth N    : Set engine search depth (default 4)")
    print("  help       : Show this help")
    print("  quit       : Exit\n")


def show_board(board: chess.Board, engine: ChessEngine, use_color: bool, perspective: chess.Color):
    print(render_board(board, use_color=use_color, perspective=perspective))
    status = game_status(board)
    eval_score = engine.evaluate(board)
    turn = "White" if board.turn == chess.WHITE else "Black"
    print(f"Eval: {format_eval(eval_score)} | Turn: {turn} | Status: {status}")


def undo_last_move(board: chess.Board):
    if not board.move_stack:
        print("Nothing to undo.")
        return
    board.pop()


def undo_full_turn(board: chess.Board):
    if not board.move_stack:
        print("Nothing to undo.")
        return
    board.pop()
    if board.move_stack:
        board.pop()


def main():
    args = parse_args()

    model = None
    if args.use_ml:
        try:
            model = load_model(args.model_path)
        except FileNotFoundError:
            print(f"Model not found at {args.model_path}. Using classic evaluation.")

    player_color = prompt_side(args.side)
    config = EngineConfig(depth=args.depth, use_ml=args.use_ml, model=model)
    engine = ChessEngine(config)

    board = chess.Board()
    history: List[str] = []
    use_color = not args.no_color
    manual_opponent = not args.human_plays
    if manual_opponent:
        bot_color = player_color
        human_color = not player_color
    else:
        human_color = player_color
        bot_color = not player_color

    print_help()
    
    if manual_opponent:
        opponent_side = "Black" if player_color == chess.WHITE else "White"
        print(f"Bot is playing as {chess.COLOR_NAMES[player_color]}.")
        print(f"You will enter {opponent_side}'s moves.\n")
    
    show_board(board, engine, use_color, player_color)

    while True:
        if board.is_game_over():
            print("Game over. Type 'restart' or 'quit'.")

        if not board.is_game_over() and board.turn == human_color:
            prompt = "Your move (uci or command): " if not manual_opponent else "Opponent move (uci or command): "
            command = input(prompt).strip().lower()
            if command in ("quit", "exit"):
                break
            if command == "help":
                print_help()
                continue
            if command == "undo":
                # Undo just the last move (which should be bot's move)
                undo_last_move(board)
                if history:
                    history.pop()
                show_board(board, engine, use_color, player_color)
                continue
            if command == "undo2":
                # Undo last 2 moves (opponent + bot)
                undo_full_turn(board)
                if history:
                    history.pop()
                if history:
                    history.pop()
                show_board(board, engine, use_color, player_color)
                continue
            if command == "editbot":
                if not board.move_stack:
                    print("No bot move to edit.")
                    continue
                # Remove bot's last move
                undo_last_move(board)
                if history:
                    history.pop()
                print("Bot's last move removed. Enter a new move for the bot:")
                while True:
                    new_move_str = input("Enter bot's move (uci): ").strip().lower()
                    try:
                        new_move = chess.Move.from_uci(new_move_str)
                    except ValueError:
                        print("Invalid UCI move.")
                        continue
                    if new_move not in board.legal_moves:
                        print("Illegal move.")
                        continue
                    board.push(new_move)
                    history.append(new_move_str)
                    print(f"Bot move updated: {new_move_str}")
                    show_board(board, engine, use_color, player_color)
                    break
                continue
            if command == "restart":
                board.reset()
                history.clear()
                show_board(board, engine, use_color, player_color)
                continue
            if command == "history":
                print("Moves:", " ".join(history) if history else "<empty>")
                continue
            if command.startswith("depth "):
                parts = command.split()
                if len(parts) == 2 and parts[1].isdigit():
                    engine.config.depth = int(parts[1])
                    print(f"Depth set to {engine.config.depth}")
                else:
                    print("Usage: depth N")
                continue
            if command in ("manual on", "manual off"):
                manual_opponent = command.endswith("on")
                if manual_opponent:
                    bot_color = player_color
                    human_color = not player_color
                else:
                    human_color = player_color
                    bot_color = not player_color
                state = "on" if manual_opponent else "off"
                print(f"Manual opponent moves {state}.")
                continue

            try:
                move = chess.Move.from_uci(command)
            except ValueError:
                print("Invalid UCI move.")
                continue

            if move not in board.legal_moves:
                print("Illegal move.")
                continue

            board.push(move)
            history.append(move.uci())
            show_board(board, engine, use_color, player_color)
        else:
            if board.is_game_over():
                command = input("Command: ").strip().lower()
                if command == "restart":
                    board.reset()
                    history.clear()
                    show_board(board, engine, use_color, player_color)
                elif command in ("quit", "exit"):
                    break
                continue

            if board.turn == bot_color:
                print(f"Bot thinking at depth {engine.config.depth}...")
                move = engine.best_move(board)
                board.push(move)
                history.append(move.uci())
                print(f"Bot move: {move.uci()}")
                show_board(board, engine, use_color, player_color)


if __name__ == "__main__":
    main()
