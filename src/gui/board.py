"""
Chess board widget implementation for StockPy.
"""

from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QApplication, QDialog
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QPainter, QColor, QPixmap, QDrag, QMouseEvent
from .promotionDialog import PromotionDialog
import chess
import os

class ChessSquare(QWidget):
    """A single square on the chess board."""
    
    def __init__(self, is_dark: bool, square: chess.Square, label: str = '', parent=None):
        """
        Initialize a chess square.
        
        Args:
            is_dark (bool): Whether this is a dark square
            square (chess.Square): The chess square this widget represents
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        self.is_dark = is_dark
        self.square = square
        self.label = label
        self.setMinimumSize(50, 50)
        self.setAcceptDrops(True)
        
        # Create and configure the piece label
        self.piece_label = QLabel(self)
        self.piece_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.piece_label.setGeometry(0, 0, self.width(), self.height())
        
        # Track drag state
        self.drag_start_position = None
        
    def paintEvent(self, event) -> None:
        """Paint the square background."""
        painter = QPainter(self)
        color = QColor("#B58863") if self.is_dark else QColor("#F0D9B5")
        painter.fillRect(event.rect(), color)
        if self.label != '':
            font = painter.font()
            font.setPointSize(12)
            painter.setFont(font)
            painter.setPen(QColor("black"))
            painter.drawText(event.rect(), (
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft
                ), self.label)
        
    def setPiece(self, pixmap: QPixmap = None):
        """
        Set or remove a piece on this square.
        
        Args:
            pixmap (QPixmap, optional): Piece image to display, or None to remove piece
        """
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.size() * 0.8,  # Make piece slightly smaller than square
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.piece_label.setPixmap(scaled_pixmap)
        else:
            self.piece_label.clear()
            
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events to start drag operations."""
        if event.button() == Qt.MouseButton.LeftButton and self.piece_label.pixmap():
            self.drag_start_position = event.pos()
            
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events for drag operations."""
        if not (event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_position):
            return
            
        # Check if the drag threshold has been met
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        # Start the drag operation
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.square))  # Store the source square
        drag.setMimeData(mime_data)
        
        # Create a pixmap for the drag cursor
        pixmap = self.piece_label.pixmap()
        if pixmap:
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(pixmap.width()//2, pixmap.height()//2))
        
        # Execute the drag
        drag.exec(Qt.DropAction.MoveAction)
        
    def dragEnterEvent(self, event) -> None:
        """Handle drag enter events."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dropEvent(self, event) -> None:
        """Handle drop events."""
        source_square = int(event.mimeData().text())
        if self.parent():
            # Notify the board of the move
            self.parent().try_move(source_square, self.square)
        event.acceptProposedAction()
            
    def resizeEvent(self, event) -> None:
        """Handle square resizing."""
        super().resizeEvent(event)
        self.piece_label.setGeometry(0, 0, self.width(), self.height())
        if self.piece_label.pixmap() and not self.piece_label.pixmap().isNull():
            current_pixmap = self.piece_label.pixmap().copy()
            self.setPiece(current_pixmap)

class ChessBoard(QWidget):
    """Chess board widget that displays pieces and handles moves."""
    
    def __init__(self, parent=None):
        """Initialize the chess board."""
        super().__init__(parent)
        
        # Initialize python-chess board
        self.board = chess.Board()
        
        # Store game history (list of moves)
        self.moves = []
        self.current_position = 0
        
        # Set up the grid layout
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create squares
        self.squares = {}
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
        
        self.setLayout(self.layout)
        self.piece_images = self._load_piece_images()
        self.setMinimumSize(400, 400)
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
            main_window = self.window()
            if main_window and hasattr(main_window, 'move_list'):
                main_window.move_list.add_move(len(self.moves), san)
        else:
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
        
    def update_display(self):
        """Update the board display to match the current position."""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            square_widget = self.squares[square]
            
            if piece:
                pixmap = self.piece_images.get(piece.symbol())
                square_widget.setPiece(pixmap)
            else:
                square_widget.setPiece(None)
                
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
        
        self.current_position = move_index + 1
        self.update_display()
