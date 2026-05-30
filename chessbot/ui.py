from __future__ import annotations

import chess

RESET = "\033[0m"
FG_WHITE = "\033[97m"
FG_BLACK = "\033[30m"
BG_LIGHT = "\033[47m"
BG_DARK = "\033[100m"


def _piece_symbol(piece: chess.Piece) -> str:
    """Return Unicode chess symbol for the piece."""
    unicode_map = {
        (chess.KING, chess.WHITE): "♔",
        (chess.QUEEN, chess.WHITE): "♕",
        (chess.ROOK, chess.WHITE): "♖",
        (chess.BISHOP, chess.WHITE): "♗",
        (chess.KNIGHT, chess.WHITE): "♘",
        (chess.PAWN, chess.WHITE): "♙",
        (chess.KING, chess.BLACK): "♚",
        (chess.QUEEN, chess.BLACK): "♛",
        (chess.ROOK, chess.BLACK): "♜",
        (chess.BISHOP, chess.BLACK): "♝",
        (chess.KNIGHT, chess.BLACK): "♞",
        (chess.PAWN, chess.BLACK): "♟",
    }
    return unicode_map.get((piece.piece_type, piece.color), "?")


def render_board(board: chess.Board, use_color: bool = True, perspective: chess.Color = chess.WHITE) -> str:
    """Return an ASCII board with optional ANSI colors and player perspective."""
    lines = []
    if perspective == chess.WHITE:
        rank_iter = range(7, -1, -1)
        file_iter = range(8)
        files_line = "   a  b  c  d  e  f  g  h"
    else:
        rank_iter = range(0, 8)
        file_iter = range(7, -1, -1)
        files_line = "   h  g  f  e  d  c  b  a"

    for rank in rank_iter:
        row = [str(rank + 1), " "]
        for file in file_iter:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            light_square = (file + rank) % 2 == 0
            bg = BG_LIGHT if light_square else BG_DARK
            fg = FG_WHITE if piece and piece.color == chess.WHITE else FG_BLACK

            if piece is None:
                cell = "."
            else:
                cell = _piece_symbol(piece)

            if use_color:
                row.append(f"{bg}{fg} {cell} {RESET}")
            else:
                row.append(f" {cell} ")
        lines.append("".join(row))

    return "\n".join(lines + [files_line])


def game_status(board: chess.Board) -> str:
    if board.is_checkmate():
        return "Checkmate"
    if board.is_stalemate():
        return "Stalemate"
    if board.is_check():
        return "Check"
    return "In play"
