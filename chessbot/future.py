"""Stubs for future enhancements (opening books, tablebases, self-play, RL)."""


class OpeningBook:
    def find_move(self, fen: str):
        raise NotImplementedError


class EndgameTablebase:
    def probe(self, fen: str):
        raise NotImplementedError


class SelfPlayTrainer:
    def run(self):
        raise NotImplementedError


class ReinforcementLearner:
    def run(self):
        raise NotImplementedError
