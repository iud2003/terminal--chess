from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple
import random
import time

import chess
import chess.engine

from .model import EvalMLP, evaluate_board
from .opening_book import get_book_move
from .utils import classic_evaluation, find_stockfish, termination_score


@dataclass
class EngineConfig:
    depth: int = 4
    use_ml: bool = False
    model: Optional[EvalMLP] = None
    use_stockfish: bool = False
    stockfish_path: Optional[str] = None
    stockfish_depth: int = 12
    use_book: bool = True
    book_max_ply: int = 8
    randomness: bool = True
    randomness_margin: int = 30
    max_time_ms: int = 1500


class ChessEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self._stockfish: Optional[chess.engine.SimpleEngine] = None

    def evaluate(self, board: chess.Board) -> int:
        if board.is_game_over():
            return termination_score(board, ply=0)
        if self.config.use_ml and self.config.model is not None:
            return evaluate_board(self.config.model, board)
        return classic_evaluation(board)

    def _stockfish_move(self, board: chess.Board) -> Optional[chess.Move]:
        if not self.config.use_stockfish:
            return None
        path = find_stockfish(self.config.stockfish_path)
        if not path:
            return None
        if self._stockfish is None:
            self._stockfish = chess.engine.SimpleEngine.popen_uci(path)
        if self.config.max_time_ms > 0:
            result = self._stockfish.play(board, chess.engine.Limit(time=self.config.max_time_ms / 1000.0))
        else:
            result = self._stockfish.play(board, chess.engine.Limit(depth=self.config.stockfish_depth))
        return result.move

    def best_move(self, board: chess.Board) -> chess.Move:
        if self.config.use_book and board.fullmove_number <= (self.config.book_max_ply // 2 + 1):
            book_move = get_book_move(board)
            if book_move:
                return book_move

        stockfish_move = self._stockfish_move(board)
        if stockfish_move:
            return stockfish_move

        best = None
        maximizing = board.turn == chess.WHITE
        best_score = -float("inf") if maximizing else float("inf")
        scored_moves = []

        deadline = None
        if self.config.max_time_ms > 0:
            deadline = time.monotonic() + (self.config.max_time_ms / 1000.0)

        for move in self._ordered_moves(board):
            board.push(move)
            score = self._minimax(
                board,
                self.config.depth - 1,
                -float("inf"),
                float("inf"),
                not maximizing,
                ply=1,
                deadline=deadline,
            )
            if board.is_repetition(2) or board.can_claim_threefold_repetition():
                score += -50 if maximizing else 50
            board.pop()

            scored_moves.append((score, move))

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

        if self.config.randomness and scored_moves:
            scored_moves.sort(key=lambda sm: sm[0], reverse=maximizing)
            top_score = scored_moves[0][0]
            candidates = [m for s, m in scored_moves if (top_score - s if maximizing else s - top_score) <= self.config.randomness_margin]
            if candidates:
                return random.choice(candidates)
        return best

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool, ply: int, deadline: Optional[float]) -> int:
        if deadline is not None and time.monotonic() >= deadline:
            return self.evaluate(board)
        if depth == 0 or board.is_game_over():
            if board.is_game_over():
                return termination_score(board, ply)
            return self.evaluate(board)

        if maximizing:
            value = -float("inf")
            for move in self._ordered_moves(board):
                board.push(move)
                value = max(value, self._minimax(board, depth - 1, alpha, beta, False, ply + 1, deadline))
                board.pop()
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return int(value)
        value = float("inf")
        for move in self._ordered_moves(board):
            board.push(move)
            value = min(value, self._minimax(board, depth - 1, alpha, beta, True, ply + 1, deadline))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return int(value)

    def _ordered_moves(self, board: chess.Board):
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        return moves

    def close(self):
        if self._stockfish is not None:
            self._stockfish.quit()
            self._stockfish = None
