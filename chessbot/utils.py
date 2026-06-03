from __future__ import annotations

import math
import os
from typing import Optional

import chess

MATE_SCORE = 100000

PAWN_PST = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0,
]

KNIGHT_PST = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_PST = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_PST = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0,
]

QUEEN_PST = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20,
]

KING_PST = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20,
]


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


def _pst_value(piece_type: int, square: int, color: chess.Color) -> int:
    tables = {
        chess.PAWN: PAWN_PST,
        chess.KNIGHT: KNIGHT_PST,
        chess.BISHOP: BISHOP_PST,
        chess.ROOK: ROOK_PST,
        chess.QUEEN: QUEEN_PST,
        chess.KING: KING_PST,
    }
    table = tables[piece_type]
    index = square if color == chess.WHITE else chess.square_mirror(square)
    return table[index]


def positional_evaluation(board: chess.Board) -> int:
    score = 0
    for piece_type in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING):
        for square in board.pieces(piece_type, chess.WHITE):
            score += _pst_value(piece_type, square, chess.WHITE)
        for square in board.pieces(piece_type, chess.BLACK):
            score -= _pst_value(piece_type, square, chess.BLACK)
    return score


def _mobility(board: chess.Board, color: chess.Color) -> int:
    temp = board.copy(stack=False)
    temp.turn = color
    return temp.legal_moves.count()


def mobility_evaluation(board: chess.Board) -> int:
    white_moves = _mobility(board, chess.WHITE)
    black_moves = _mobility(board, chess.BLACK)
    return (white_moves - black_moves) * 2


def king_safety_evaluation(board: chess.Board) -> int:
    score = 0
    for color in (chess.WHITE, chess.BLACK):
        king_square = board.king(color)
        if king_square is None:
            continue
        king_file = chess.square_file(king_square)
        pawn_rank = 1 if color == chess.WHITE else 6
        shield_files = [f for f in (king_file - 1, king_file, king_file + 1) if 0 <= f <= 7]
        shield = 0
        for file in shield_files:
            square = chess.square(file, pawn_rank)
            if board.piece_at(square) == chess.Piece(chess.PAWN, color):
                shield += 1
        missing = 3 - shield
        delta = missing * 15
        if color == chess.WHITE:
            score -= delta
        else:
            score += delta
    return score


def classic_evaluation(board: chess.Board) -> int:
    return (
        material_evaluation(board)
        + positional_evaluation(board)
        + mobility_evaluation(board)
        + king_safety_evaluation(board)
    )


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
    for candidate in (
        "stockfish",
        "stockfish.exe",
        os.path.join(os.getcwd(), "stockfish.exe"),
        "/usr/bin/stockfish",
        "/usr/local/bin/stockfish",
    ):
        if os.path.isfile(candidate):
            return candidate
    return None
