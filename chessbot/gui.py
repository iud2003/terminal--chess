"""PyQt6 GUI for Chess Bot."""
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import chess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QBrush, QPen

from .engine import ChessEngine, EngineConfig
from .model import load_model
from .utils import find_stockfish, format_eval


class ChessBoardWidget(QWidget):
    """Custom widget to draw the chess board with click-to-move support."""
    
    move_made = pyqtSignal(chess.Move)  # Signal emitted when a move is made
    
    SQUARE_SIZE = 60
    PIECE_UNICODE = {
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

    def __init__(self, board: chess.Board, player_color: chess.Color):
        super().__init__()
        self.board = board
        self.player_color = player_color
        self.view_color = player_color
        self.selected_square = None
        self.valid_moves = []
        self.last_move = None
        self.edit_mode = False
        self.drag_from = None
        self.light_square = QColor(200, 200, 200)
        self.dark_square = QColor(100, 100, 100)
        self.white_piece = QColor(245, 245, 245)
        self.black_piece = QColor(30, 30, 30)
        self.setMinimumSize(QSize(480, 480))
        self.setStyleSheet("background-color: #333333;")

    def apply_theme(self, theme: str):
        if theme == "Wood":
            self.light_square = QColor(222, 184, 135)
            self.dark_square = QColor(139, 90, 43)
            self.white_piece = QColor(255, 248, 220)
            self.black_piece = QColor(66, 35, 8)
        elif theme == "Marble":
            self.light_square = QColor(230, 230, 235)
            self.dark_square = QColor(90, 95, 110)
            self.white_piece = QColor(245, 245, 250)
            self.black_piece = QColor(20, 20, 30)
        else:
            self.light_square = QColor(200, 200, 200)
            self.dark_square = QColor(100, 100, 100)
            self.white_piece = QColor(245, 245, 245)
            self.black_piece = QColor(30, 30, 30)
        self.update()

    def get_valid_moves_for_square(self, square: int) -> list:
        """Get all valid moves from a given square."""
        moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                moves.append(move.to_square)
        return moves

    def _square_from_pos(self, pos) -> int:
        x = pos.x() // self.SQUARE_SIZE
        y = pos.y() // self.SQUARE_SIZE

        if self.view_color == chess.BLACK:
            file = 7 - x
            rank = y
        else:
            file = x
            rank = 7 - y

        return chess.square(file, rank)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw squares
        for rank in range(8):
            for file in range(8):
                if self.view_color == chess.BLACK:
                    x = (7 - file) * self.SQUARE_SIZE
                    y = rank * self.SQUARE_SIZE
                else:
                    x = file * self.SQUARE_SIZE
                    y = (7 - rank) * self.SQUARE_SIZE
                
                is_light = (rank + file) % 2 == 0
                color = self.light_square if is_light else self.dark_square
                
                painter.fillRect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE, QBrush(color))
                
                # Highlight selected square
                square = chess.square(file, rank)
                if self.last_move and square in (self.last_move.from_square, self.last_move.to_square):
                    color = QColor(120, 180, 255)  # Last move highlight
                    painter.fillRect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE, QBrush(color))
                if square == self.selected_square:
                    color = QColor(255, 200, 0)  # Gold highlight
                    painter.fillRect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE, QBrush(color))
                
                # Highlight valid moves
                if square in self.valid_moves:
                    painter.fillRect(x + 20, y + 20, 20, 20, QBrush(QColor(0, 255, 0)))  # Green dot
                
                # Draw border
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.drawRect(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE)
        
        # Draw pieces
        painter.setFont(QFont("Segoe UI Symbol", 36))
        for rank in range(8):
            for file in range(8):
                if self.view_color == chess.BLACK:
                    x = (7 - file) * self.SQUARE_SIZE
                    y = rank * self.SQUARE_SIZE
                    square = chess.square(file, rank)
                else:
                    x = file * self.SQUARE_SIZE
                    y = (7 - rank) * self.SQUARE_SIZE
                    square = chess.square(file, rank)
                
                piece = self.board.piece_at(square)
                if piece:
                    symbol = self.PIECE_UNICODE.get((piece.piece_type, piece.color), "?")
                    painter.setPen(self.white_piece if piece.color == chess.WHITE else self.black_piece)
                    painter.drawText(x, y, self.SQUARE_SIZE, self.SQUARE_SIZE,
                                   Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, symbol)

    def mousePressEvent(self, event):
        square = self._square_from_pos(event.pos())

        if self.edit_mode:
            piece = self.board.piece_at(square)
            if piece:
                self.drag_from = square
            else:
                self.drag_from = None
            return
        
        # If no square selected, select one
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.valid_moves = self.get_valid_moves_for_square(square)
        # If square already selected
        else:
            # If clicking the same square, deselect
            if square == self.selected_square:
                self.selected_square = None
                self.valid_moves = []
            # If clicking a valid destination, make the move
            elif square in self.valid_moves:
                move = None
                for m in self.board.legal_moves:
                    if m.from_square == self.selected_square and m.to_square == square:
                        move = m
                        break
                if move:
                    self.move_made.emit(move)
                self.selected_square = None
                self.valid_moves = []
            # If clicking a different piece, select it
            else:
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                    self.valid_moves = self.get_valid_moves_for_square(square)
                else:
                    self.selected_square = None
                    self.valid_moves = []
        
        self.update()

    def mouseReleaseEvent(self, event):
        if not self.edit_mode:
            return
        if self.drag_from is None:
            return
        target = self._square_from_pos(event.pos())
        if target == self.drag_from:
            self.drag_from = None
            return
        piece = self.board.piece_at(self.drag_from)
        if piece is None:
            self.drag_from = None
            return
        # Move piece ignoring rules
        self.board.remove_piece_at(self.drag_from)
        self.board.set_piece_at(target, piece)
        self.last_move = chess.Move(self.drag_from, target)
        self.drag_from = None
        self.selected_square = None
        self.valid_moves = []
        self.update()


class ChessBotGUI(QMainWindow):
    bot_move_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Bot - GUI (Click to Move)")
        self.setGeometry(100, 100, 1000, 700)
        
        # State
        self.board = chess.Board()
        self.player_color = chess.WHITE
        self.engine = None
        self.model = None
        self.manual_mode = True
        self.history = []
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.pending_future = None
        
        # Layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left side: Board
        board_layout = QVBoxLayout()
        self.board_widget = ChessBoardWidget(self.board, self.player_color)
        self.board_widget.move_made.connect(self.on_move_made)
        board_layout.addWidget(self.board_widget)
        main_layout.addLayout(board_layout, 2)
        
        # Right side: Controls
        control_layout = QVBoxLayout()
        
        # Side selector
        control_layout.addWidget(QLabel("Select Your Side:"))
        self.side_combo = QComboBox()
        self.side_combo.addItems(["White", "Black"])
        self.side_combo.currentTextChanged.connect(self.on_side_changed)
        control_layout.addWidget(self.side_combo)
        
        # Depth
        control_layout.addWidget(QLabel("Engine Depth (1-8):"))
        self.depth_spin = QSpinBox()
        self.depth_spin.setMinimum(1)
        self.depth_spin.setMaximum(8)
        self.depth_spin.setValue(4)
        control_layout.addWidget(self.depth_spin)

        # Move time
        control_layout.addWidget(QLabel("Max move time (ms):"))
        self.time_spin = QSpinBox()
        self.time_spin.setMinimum(200)
        self.time_spin.setMaximum(10000)
        self.time_spin.setValue(1500)
        self.time_spin.setSingleStep(200)
        control_layout.addWidget(self.time_spin)

        # Engine options
        control_layout.addWidget(QLabel("Engine Options:"))
        self.book_check = QCheckBox("Use opening book")
        self.book_check.setChecked(True)
        control_layout.addWidget(self.book_check)

        self.random_check = QCheckBox("Add randomness")
        self.random_check.setChecked(True)
        control_layout.addWidget(self.random_check)

        self.stockfish_check = QCheckBox("Use Stockfish (strong)")
        self.stockfish_check.setChecked(False)
        control_layout.addWidget(self.stockfish_check)

        self.stockfish_path = QLineEdit()
        self.stockfish_path.setText(
            "C:\\Users\\isumd\\Downloads\\stockfish-windows-x86-64-avx2\\stockfish\\stockfish-windows-x86-64-avx2.exe"
        )
        self.stockfish_path.setPlaceholderText("Stockfish path (optional)")
        control_layout.addWidget(self.stockfish_path)

        self.stockfish_status = QLabel("Stockfish: not checked")
        control_layout.addWidget(self.stockfish_status)

        self.human_check = QCheckBox("Human-like play")
        self.human_check.setChecked(True)
        control_layout.addWidget(self.human_check)

        control_layout.addWidget(QLabel("Human strength (Elo):"))
        self.human_elo_spin = QSpinBox()
        self.human_elo_spin.setMinimum(800)
        self.human_elo_spin.setMaximum(3000)
        self.human_elo_spin.setValue(2000)
        self.human_elo_spin.setSingleStep(100)
        control_layout.addWidget(self.human_elo_spin)

        # Theme
        control_layout.addWidget(QLabel("Board Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Classic", "Wood", "Marble"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        control_layout.addWidget(self.theme_combo)

        self.edit_check = QCheckBox("Edit mode (drag pieces)")
        self.edit_check.setChecked(False)
        self.edit_check.stateChanged.connect(self.on_edit_changed)
        control_layout.addWidget(self.edit_check)

        self.flip_check = QCheckBox("Flip board (rotate)")
        self.flip_check.setChecked(False)
        self.flip_check.stateChanged.connect(self.on_flip_changed)
        control_layout.addWidget(self.flip_check)
        
        # Status
        control_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Click 'Start Game' to begin.\n\nGameplay:\n1. Click a piece\n2. Click destination square\n3. Bot plays automatically")
        self.status_label.setWordWrap(True)
        control_layout.addWidget(self.status_label)
        
        # Evaluation
        self.eval_label = QLabel("Eval: +0.00")
        control_layout.addWidget(self.eval_label)
        
        # Buttons
        self.start_btn = QPushButton("Start Game")
        self.start_btn.clicked.connect(self.start_game)
        control_layout.addWidget(self.start_btn)
        
        self.undo_btn = QPushButton("Undo Last 2 Moves")
        self.undo_btn.clicked.connect(self.undo_last)
        control_layout.addWidget(self.undo_btn)
        
        self.restart_btn = QPushButton("Restart")
        self.restart_btn.clicked.connect(self.restart_game)
        control_layout.addWidget(self.restart_btn)
        
        # Move history
        control_layout.addWidget(QLabel("Move History:"))
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(150)
        control_layout.addWidget(self.history_text)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.bot_move_ready.connect(self._apply_bot_move)
        self.init_engine()
    
    def init_engine(self):
        """Initialize the chess engine."""
        config = EngineConfig(
            depth=self.depth_spin.value(),
            use_ml=False,
            model=self.model,
            use_book=self.book_check.isChecked(),
            randomness=self.random_check.isChecked(),
            use_stockfish=self.stockfish_check.isChecked(),
            stockfish_path=self.stockfish_path.text().strip() or None,
            max_time_ms=self.time_spin.value(),
            humanize=self.human_check.isChecked(),
            human_elo=self.human_elo_spin.value(),
        )
        self.engine = ChessEngine(config)
        self.update_stockfish_status()
        self.update_status()

    def update_engine_config(self):
        if not self.engine:
            return
        self.engine.config.depth = self.depth_spin.value()
        self.engine.config.max_time_ms = self.time_spin.value()
        self.engine.config.use_book = self.book_check.isChecked()
        self.engine.config.randomness = self.random_check.isChecked()
        self.engine.config.use_stockfish = self.stockfish_check.isChecked()
        self.engine.config.stockfish_path = self.stockfish_path.text().strip() or None
        self.engine.config.humanize = self.human_check.isChecked()
        self.engine.config.human_elo = self.human_elo_spin.value()
        self.update_stockfish_status()

    def update_stockfish_status(self):
        if not self.stockfish_check.isChecked():
            self.stockfish_status.setText("Stockfish: disabled")
            return
        path = self.stockfish_path.text().strip() or None
        resolved = find_stockfish(path)
        if resolved:
            mode = "Human" if self.human_check.isChecked() else "Full"
            self.stockfish_status.setText(f"Stockfish: OK ({mode})")
        else:
            self.stockfish_status.setText("Stockfish: NOT FOUND")
    
    def on_side_changed(self):
        """Handle side selection change."""
        self.player_color = chess.WHITE if self.side_combo.currentText() == "White" else chess.BLACK
        self.board_widget.player_color = self.player_color
        if not self.flip_check.isChecked():
            self.board_widget.view_color = self.player_color
        self.board_widget.selected_square = None
        self.board_widget.valid_moves = []
        self.board_widget.update()

    def on_theme_changed(self):
        self.board_widget.apply_theme(self.theme_combo.currentText())

    def on_edit_changed(self):
        self.board_widget.edit_mode = self.edit_check.isChecked()
        self.board_widget.selected_square = None
        self.board_widget.valid_moves = []
        if self.board_widget.edit_mode:
            self.status_label.setText("Edit mode: drag pieces to any square")
        else:
            self.update_status()
        self.board_widget.update()

    def on_flip_changed(self):
        if self.flip_check.isChecked():
            self.board_widget.view_color = not self.player_color
        else:
            self.board_widget.view_color = self.player_color
        self.board_widget.selected_square = None
        self.board_widget.valid_moves = []
        self.board_widget.update()
    
    def start_game(self):
        """Start a new game."""
        self.board.reset()
        self.history.clear()
        self.init_engine()
        self.board_widget.selected_square = None
        self.board_widget.valid_moves = []
        self.update_status()
        self.history_text.setText("")
        self.board_widget.update()
        
        if self.board.turn != self.player_color:
            self.status_label.setText(f"Game started! Bot is playing {chess.COLOR_NAMES[not self.player_color]}.\n\nYour turn: {chess.COLOR_NAMES[self.player_color]}")
            QTimer.singleShot(1000, self.play_bot_move)
    
    def on_move_made(self, move: chess.Move):
        """Handle a move made by clicking on the board."""
        if not self.board.is_game_over() and self.board.turn == self.player_color:
            self.board.push(move)
            self.history.append(move.uci())
            self.update_history()
            self.board_widget.last_move = move
            self.board_widget.update()
            
            # Check if game is over
            if self.board.is_game_over():
                self.update_status()
                return
            
            # Bot's turn
            self.status_label.setText("Bot thinking...")
            self.update()
            QTimer.singleShot(500, self.play_bot_move)
    
    def play_bot_move(self):
        """Play the bot's move."""
        if self.engine is None or self.board.is_game_over():
            return
        
        self.status_label.setText("Bot thinking...")
        self.update()
        
        self.update_engine_config()
        if self.pending_future and not self.pending_future.done():
            return
        board_copy = self.board.copy(stack=False)
        self.pending_future = self.executor.submit(self.engine.best_move, board_copy)
        self.pending_future.add_done_callback(self._on_bot_move_ready)

    def _on_bot_move_ready(self, future):
        try:
            move = future.result()
            payload = ("ok", move)
        except Exception as exc:
            payload = ("error", exc)
        self.bot_move_ready.emit(payload)

    def _apply_bot_move(self, payload):
        self.pending_future = None
        status, data = payload
        if status == "error":
            self.status_label.setText(f"Bot error: {data}")
            return
        move = data
        if self.board.is_game_over():
            self.update_status()
            return
        if move not in self.board.legal_moves:
            self.status_label.setText("Bot returned an illegal move. Try again.")
            return
        self.board.push(move)
        self.history.append(move.uci())
        self.update_history()
        self.board_widget.last_move = move
        self.board_widget.selected_square = None
        self.board_widget.valid_moves = []
        self.board_widget.update()

        if self.board.is_game_over():
            self.update_status()
        else:
            self.status_label.setText(f"Bot played: {move.uci()}\n\nYour turn: Click a piece to move")
    
    def undo_last(self):
        """Undo the last 2 moves (bot move + player move)."""
        if len(self.board.move_stack) >= 1:
            # Undo bot move
            if self.board.move_stack:
                self.board.pop()
                if self.history:
                    self.history.pop()
            # Undo player move
            if self.board.move_stack:
                self.board.pop()
                if self.history:
                    self.history.pop()
            
            self.update_history()
            self.board_widget.selected_square = None
            self.board_widget.valid_moves = []
            self.board_widget.update()
            self.update_status()
    
    def restart_game(self):
        """Restart the game."""
        self.start_game()
    
    def update_history(self):
        """Update the move history display."""
        if self.history:
            history_str = " ".join([f"{i//2+1}. {self.history[i]}" if i % 2 == 0 else self.history[i] 
                                   for i in range(len(self.history))])
        else:
            history_str = "No moves yet"
        self.history_text.setText(history_str)
    
    def update_status(self):
        """Update status and evaluation."""
        if self.engine:
            eval_score = self.engine.evaluate(self.board)
            self.eval_label.setText(f"Eval: {format_eval(eval_score)}")
        
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            self.status_label.setText(f"🎉 Checkmate! {winner} wins!")
        elif self.board.is_stalemate():
            self.status_label.setText("Stalemate! Draw.")
        elif self.board.is_check():
            turn = chess.COLOR_NAMES[self.board.turn]
            self.status_label.setText(f"⚠️ {turn} is in check!")
        else:
            turn = chess.COLOR_NAMES[self.board.turn]
            self.status_label.setText(f"{turn}'s turn: Click a piece to move")

    def closeEvent(self, event):
        if self.engine:
            self.engine.close()
        if self.executor:
            self.executor.shutdown(wait=False)
        super().closeEvent(event)


def run_gui():
    """Run the GUI application."""
    app = QApplication(sys.argv)
    window = ChessBotGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
