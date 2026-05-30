from __future__ import annotations

import argparse
import os
from typing import List, Tuple

import chess
import chess.pgn
import chess.engine
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from .model import EvalMLP, ModelConfig, board_to_tensor
from .utils import find_stockfish, material_evaluation


def parse_games(pgn_path: str, max_positions: int) -> List[chess.Board]:
    boards: List[chess.Board] = []
    with open(pgn_path, "r", encoding="utf-8") as handle:
        while True:
            game = chess.pgn.read_game(handle)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                boards.append(board.copy(stack=False))
                if len(boards) >= max_positions:
                    return boards
    return boards


def label_board(board: chess.Board, engine: chess.engine.SimpleEngine | None, depth: int) -> int:
    if engine is None:
        return material_evaluation(board)
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    score = info["score"].pov(chess.WHITE).score(mate_score=100000)
    return 0 if score is None else int(score)


def build_dataset(boards: List[chess.Board], engine: chess.engine.SimpleEngine | None, depth: int) -> Tuple[torch.Tensor, torch.Tensor]:
    features = []
    labels = []
    for board in boards:
        tensor = board_to_tensor(board).squeeze(0)
        features.append(tensor.numpy())
        labels.append(label_board(board, engine, depth))

    x = torch.tensor(np.array(features), dtype=torch.float32)
    y = torch.tensor(np.array(labels), dtype=torch.float32).unsqueeze(1)
    return x, y


def train_model(x: torch.Tensor, y: torch.Tensor, epochs: int, batch_size: int, lr: float) -> EvalMLP:
    input_dim = x.shape[1]
    model = EvalMLP(input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()

    dataset = TensorDataset(x, y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = loss_fn(preds, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / max(len(loader), 1)
        print(f"Epoch {epoch}: loss={avg_loss:.4f}")

    return model


def save_model(model: EvalMLP, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
        "config": {"input_dim": model.net[0].in_features},
        "state_dict": model.state_dict(),
    }
    torch.save(payload, out_path)


def main():
    parser = argparse.ArgumentParser(description="Train the chess evaluation model.")
    parser.add_argument("--pgn", required=True, help="Path to PGN file")
    parser.add_argument("--out", required=True, help="Output model path")
    parser.add_argument("--max-positions", type=int, default=10000)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--stockfish-path", default=None)
    parser.add_argument("--stockfish-depth", type=int, default=12)
    args = parser.parse_args()

    engine_path = find_stockfish(args.stockfish_path)
    engine = None
    if engine_path:
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        print(f"Using Stockfish at {engine_path}")
    else:
        print("Stockfish not found. Using material eval labels.")

    boards = parse_games(args.pgn, args.max_positions)
    print(f"Loaded {len(boards)} positions")

    x, y = build_dataset(boards, engine, args.stockfish_depth)
    model = train_model(x, y, args.epochs, args.batch_size, args.lr)
    save_model(model, args.out)

    if engine:
        engine.quit()


if __name__ == "__main__":
    main()
