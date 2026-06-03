from __future__ import annotations

import random
from typing import Dict, List, Optional

import chess


def _book_key(board: chess.Board) -> str:
    """Return a compact FEN key without move clocks."""
    parts = board.fen().split(" ")
    return " ".join(parts[:4])


BOOK: Dict[str, List[str]] = {
    # Starting position
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": ["e2e4", "d2d4", "c2c4", "g1f3"],
    # After 1. e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -": ["c7c5", "e7e5", "e7e6", "c7c6"],
    # After 1. d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq -": ["d7d5", "g8f6", "e7e6"],
    # After 1. c4
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq -": ["g8f6", "e7e5", "c7c5"],
    # After 1. Nf3
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -": ["d7d5", "g8f6", "c7c5"],
    # After 1. e4 c5
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -": ["g1f3", "b1c3", "d2d4"],
    # After 1. e4 e5
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -": ["g1f3", "f1c4", "b1c3"],
}


def get_book_move(board: chess.Board) -> Optional[chess.Move]:
    """Return a book move if available."""
    key = _book_key(board)
    moves = BOOK.get(key)
    if not moves:
        return None
    choices = [chess.Move.from_uci(m) for m in moves if chess.Move.from_uci(m) in board.legal_moves]
    if not choices:
        return None
    return random.choice(choices)
