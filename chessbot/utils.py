from __future__ import annotations

import math
import os
from typing import Optional

import chess

MATE_SCORE = 100000


def material_evaluation(board: chess.Board) -> int:
    """Evaluate material from White's perspective (centipawns)."""
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0,
    }
    score = 0
    for piece_type in piece_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
    return score


def termination_score(board: chess.Board, ply: int) -> int:
    """Return a large score for checkmate and zero for draws."""
    if board.is_checkmate():
        return -MATE_SCORE + ply if board.turn == chess.WHITE else MATE_SCORE - ply
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves():
        return 0
    return 0


def format_eval(score_cp: int) -> str:
    """Format centipawn score as a human-readable string."""
    score_pawns = score_cp / 100.0
    sign = "+" if score_pawns >= 0 else ""
    return f"{sign}{score_pawns:.2f}"


def find_stockfish(path: Optional[str]) -> Optional[str]:
    """Return a usable Stockfish path if available."""
    if path and os.path.isfile(path):
        return path
    for candidate in ("stockfish", "/usr/bin/stockfish", "/usr/local/bin/stockfish"):
        if os.path.isfile(candidate):
            return candidate
    return None
