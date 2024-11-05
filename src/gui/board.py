"""
Chess board widget implementation for StockPy.
"""

from typing import Callable, Any
from PyQt6.QtWidgets import QWidget, QGridLayout, QDialog
from PyQt6.QtGui import QPixmap
from .promotionDialog import PromotionDialog
import chess
from chess import pgn as PGN
import os
from core.stockfish import StockfishEngine
from .square import ChessSquare
from .evaluationBar import EvaluationBar
from .moveList import MoveList


class ChessBoard(QWidget):
    """Chess board widget that displays pieces and handles moves."""
    
    def __init__(self, stockfish_path: str, resource_getters: dict[str, Callable[[], Any]], parent=None):
        """Initialize the chess board."""
        super().__init__(parent)

        # Save resource getters
        self.resource_getters = resource_getters
        
        # Initialize python-chess board
        self.board = chess.Board()
        
        # Initialize Stockfish engine (if path provided)
        self.engine = None
        if stockfish_path is not None:
            try:
                self.engine = StockfishEngine(stockfish_path)
                self.engine.start()
            except FileNotFoundError as e:
                print(f"Error initializing Stockfish engine: {e}")
                self.engine.quit()
                self.engine = None
        
        # Store suggested move squares for highlighting
        self.suggested_from = None
        self.suggested_to = None
        
        # Set up the grid layout
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Store moves
        self.moves = []
        self.current_position = 0

        # Create squares
        self.squares: dict[chess.Square, ChessSquare] = {}
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, rank)
                is_dark = (rank + file) % 2 == 0
                square_label = ''
                if rank == 0:
                    square_label += chr(ord('a') + file)
                if file == 0:
                    square_label += str(rank + 1)
                square_widget = ChessSquare(is_dark, square, square_label)
                self.layout.addWidget(square_widget, 7 - rank, file)
                self.squares[square] = square_widget


        # Enable or disable evaluation Bar
        self.engine_evaluation_enabled = True

        # Enable or disable engine suggestions
        self.engine_suggestions_enabled = True
        
        self.setLayout(self.layout)
        self.piece_images = self._load_piece_images()
        self.setMinimumSize(400, 400)
        self.update_engine_suggestion()
        self.update_display()
        
    def try_move(self, from_square: chess.Square, to_square: chess.Square):
        """
        Try to make a move on the board.
        
        Args:
            from_square (chess.Square): Source square
            to_square (chess.Square): Target square
        """
        # Check if this is a potential promotion move
        piece = self.board.piece_at(from_square)
        is_promotion = (
            piece 
            and piece.piece_type == chess.PAWN 
            and ((piece.color == chess.WHITE and chess.square_rank(to_square) == 7)
                 or (piece.color == chess.BLACK and chess.square_rank(to_square) == 0))
        )
        
        if is_promotion:
            # Show promotion dialog
            dialog = PromotionDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                promotion_piece = dialog.selected_piece
                # Create promotion move
                move = chess.Move(from_square, to_square, promotion=chess.Piece.from_symbol(promotion_piece).piece_type)
            else:
                # Dialog cancelled
                self.update_display()
                return
        else:
            # Regular move
            move = chess.Move(from_square, to_square)
        
        # Check if move is legal
        if move in self.board.legal_moves:
            # Get SAN before pushing the move
            san = self.board.san(move)
            
            # Store the move
            self.moves.append(move)
            self.current_position = len(self.moves)
            
            # Make the move
            self.board.push(move)
            self.update_display()
            
            # Update move list
            self.resource_getters['move_list']().add_move(san)

            # Update engine suggestion
            self.update_engine_suggestion()

            # Update evaluation bar
            self.update_evaluation_bar()

        # Update display to show changes
        self.update_display()
            
    def _load_piece_images(self) -> dict:
        """Load all piece PNG images."""
        piece_images = {}
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'pieces')

        # Mapping of piece symbols to filenames
        pieces = {
            'P': 'white_pawn.png',
            'N': 'white_knight.png',
            'B': 'white_bishop.png',
            'R': 'white_rook.png',
            'Q': 'white_queen.png',
            'K': 'white_king.png',
            'p': 'black_pawn.png',
            'n': 'black_knight.png',
            'b': 'black_bishop.png',
            'r': 'black_rook.png',
            'q': 'black_queen.png',
            'k': 'black_king.png'
        }
        
        for symbol, filename in pieces.items():
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    piece_images[symbol] = pixmap
                else:
                    print(f"Error loading piece image: {path}")
            else:
                print(f"Piece image not found: {path}")
                
        return piece_images
        
    def update_display(self) -> None:
        """Update the board display to match the current position."""
        # Find king in check (if any)
        king_square_in_check = None
        if self.board.is_check():
            king_color = self.board.turn
            king_square_in_check = self.board.king(king_color)

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            square_widget = self.squares[square]
            
            # Update piece
            if piece and piece.symbol() in self.piece_images:
                square_widget.setPiece(self.piece_images[piece.symbol()])
            else:
                square_widget.setPiece(None)

            # Update suggestion highlight
            square_widget.setSuggested(
                square == self.suggested_from or square == self.suggested_to
            )
            
            # Update check highlight
            square_widget.setCheck(square == king_square_in_check)
        
    def resizeEvent(self, event):
        """Handle board resizing to maintain square proportions."""
        super().resizeEvent(event)
        
        # Calculate the size that maintains square proportions
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        # Calculate margins to center the board
        h_margin = (width - size) // 2
        v_margin = (height - size) // 2
        
        # Update layout margins
        self.layout.setContentsMargins(h_margin, v_margin, h_margin, v_margin)
        
        # Update each square's size
        square_size = size // 8
        for square in self.squares.values():
            square.setFixedSize(square_size, square_size)
        
    def jump_to_move(self, move_index: int):
        """
        Jump to the position after the specified move.
        
        Args:
            move_index (int): 0-based index of the move to jump to
        """
        # Reset board to initial position
        self.board.reset()
        
        # Replay moves up to the selected position
        for i in range(move_index + 1):
            if i < len(self.moves):
                self.board.push(self.moves[i])
        
        self.moves = self.moves[:move_index + 1]

        self.current_position = move_index + 1
        self.update_display()

    def update_engine_suggestion(self, time_limit: float = 3.0):
        """
        Get the move suggested by the engine and store it for later highlighting.
        """
        # Reset suggested move
        self.suggested_from = None
        self.suggested_to = None

        # Return if engine is not enabled
        if self.engine is None or not self.engine_suggestions_enabled:
            return
        
        # Get the suggested move
        best_move = self.engine.get_best_move(self.board, time_limit)
        print(f"DEBUG: Suggested move: {best_move}")
        if best_move:
            self.suggested_from = best_move.from_square
            self.suggested_to = best_move.to_square
    
    def update_evaluation_bar(self, time_limit: float = 0.1) -> None:
        """Evaluate the current position."""
        if self.engine is not None and self.engine_evaluation_enabled:
            evaluation = self.engine.get_evaluation(self.board, time_limit)
            self.resource_getters['eval_bar']().setEvaluation(evaluation)
            print(f"DEBUG: Evaluation set: {evaluation}")

    def closeEvent(self, event):
        """Handle the window close event."""
        if self.engine is not None:
            self.engine.quit()
            self.engine = None
        super().closeEvent(event)

    ##########################
    ### Board Menu Actions ###
    ##########################

    def import_pgn(self, pgn_path: str) -> None:
        """Import a PGN file and update the board."""

        # Read the PGN file
        print(f'DEBUG: Importing PGN file: {pgn_path}')
        with open(pgn_path, 'r') as pgn_file:
            game = PGN.read_game(pgn_file)

        # Update the board and move list
        self.board = None           # Garbage collect the current board
        self.board = game.board()
        
        self.resource_getters['move_list']().reset()

        for move in game.mainline_moves():
            self.resource_getters['move_list']().add_move(self.board.san(move))       # Add moves to move list
            self.board.push(move)                                                   # Add moves to board

        # Update the engine suggestion and display
        self.update_engine_suggestion()
        self.update_display()

    def export_pgn(self, pgn_path: str) -> None:
        """Export the current position as a PGN file."""
        print(f'DEBUG: Exporting PGN file: {pgn_path}')
        game = chess.pgn.Game.from_board(self.board)
        with open(pgn_path, 'w') as pgn_file:
            exporter = PGN.FileExporter(pgn_file)
            game.accept(exporter)
    
    def reset(self) -> None:
        self.board.reset()
        self.update_engine_suggestion()
        self.update_display()

    ###########################
    ### Engine Menu Actions ###
    ###########################

    def toggle_engine_suggestions(self) -> None:
        """Toggle engine suggestions on or off."""
        self.engine_suggestions_enabled = not self.engine_suggestions_enabled
        self.update_engine_suggestion()
        self.update_display()

    def toggle_evaluation_bar(self) -> None:
        """Toggle the evaluation bar on or off."""
        self.engine_evaluation_enabled = not self.engine_evaluation_enabled
        if self.engine_evaluation_enabled:
            self.update_evaluation_bar()
        else:
            self.resource_getters['eval_bar']().setDisabled()
