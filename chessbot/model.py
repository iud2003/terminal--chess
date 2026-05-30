from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import chess


PIECE_PLANES = [
    chess.PAWN,
    chess.KNIGHT,
    chess.BISHOP,
    chess.ROOK,
    chess.QUEEN,
    chess.KING,
]


def board_to_tensor(board: chess.Board) -> torch.Tensor:
    """Encode a board to a flat tensor for the MLP."""
    planes = np.zeros((12, 8, 8), dtype=np.float32)
    for color in (chess.WHITE, chess.BLACK):
        for i, piece_type in enumerate(PIECE_PLANES):
            plane_index = i if color == chess.WHITE else i + 6
            for square in board.pieces(piece_type, color):
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                planes[plane_index, rank, file] = 1.0

    extras = np.array(
        [
            1.0 if board.turn == chess.WHITE else 0.0,
            1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0,
            1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0,
            1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0,
            1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0,
        ],
        dtype=np.float32,
    )

    flat = planes.reshape(-1)
    features = np.concatenate([flat, extras])
    return torch.from_numpy(features).unsqueeze(0)


class EvalMLP(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass
class ModelConfig:
    input_dim: int


def load_model(path: str) -> EvalMLP:
    payload = torch.load(path, map_location="cpu")
    config = ModelConfig(**payload["config"])
    model = EvalMLP(config.input_dim)
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model


def evaluate_board(model: EvalMLP, board: chess.Board) -> int:
    """Return centipawn-like score from White's perspective."""
    model.eval()
    with torch.no_grad():
        x = board_to_tensor(board)
        score = model(x).squeeze().item()
    return int(score)
