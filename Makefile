PYTHONPATH=.

.PHONY: run train

run:
	PYTHONPATH=$(PYTHONPATH) python3 -m chessbot.main

train:
	PYTHONPATH=$(PYTHONPATH) python3 -m chessbot.train --pgn data/games.pgn --out models/eval_mlp.pt
