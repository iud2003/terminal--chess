from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import chess

from .model import EvalMLP, evaluate_board
from .utils import MATE_SCORE, material_evaluation, termination_score


@dataclass
class EngineConfig:
    depth: int = 4
    use_ml: bool = False
    model: Optional[EvalMLP] = None


class ChessEngine:
    def __init__(self, config: EngineConfig):
        self.config = config

    def evaluate(self, board: chess.Board) -> int:
        if board.is_game_over():
            return termination_score(board, ply=0)
        if self.config.use_ml and self.config.model is not None:
            return evaluate_board(self.config.model, board)
        return material_evaluation(board)

    def best_move(self, board: chess.Board) -> chess.Move:
        best = None
        maximizing = board.turn == chess.WHITE
        best_score = -float("inf") if maximizing else float("inf")

        for move in self._ordered_moves(board):
            board.push(move)
            score = self._minimax(board, self.config.depth - 1, -float("inf"), float("inf"), not maximizing, ply=1)
            board.pop()

            if maximizing:
                if score > best_score:
                    best_score = score
                    best = move
            else:
                if score < best_score:
                    best_score = score
                    best = move

        if best is None:
            best = next(iter(board.legal_moves))
        return best

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool, ply: int) -> int:
        if depth == 0 or board.is_game_over():
            if board.is_game_over():
                return termination_score(board, ply)
            return self.evaluate(board)

        if maximizing:
            value = -float("inf")
            for move in self._ordered_moves(board):
                board.push(move)
                value = max(value, self._minimax(board, depth - 1, alpha, beta, False, ply + 1))
                board.pop()
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return int(value)
        value = float("inf")
        for move in self._ordered_moves(board):
            board.push(move)
            value = min(value, self._minimax(board, depth - 1, alpha, beta, True, ply + 1))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return int(value)

    def _ordered_moves(self, board: chess.Board):
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        return moves
