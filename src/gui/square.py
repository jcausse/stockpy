from PyQt6.QtGui import QPainter, QColor, QPixmap, QDrag, QMouseEvent, QBrush
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
import chess

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
        
        self.suggested = False
        self.in_check = False
        
    def paintEvent(self, event) -> None:
        """Paint the square background."""
        painter = QPainter(self)
        
        # Base square color
        if self.is_dark:
            base_color = QColor("#B58863")  # Dark squares
        else:
            base_color = QColor("#F0D9B5")  # Light squares
            
        # Draw base square
        painter.fillRect(0, 0, self.width(), self.height(), base_color)
        
        # Draw check highlight
        if self.in_check:
            check_color = QColor("#FF0000")  # Red for check
            check_color.setAlpha(100)  # Make it semi-transparent
            painter.fillRect(0, 0, self.width(), self.height(), check_color)
            
        # Draw suggestion highlight
        if self.suggested:
            suggest_color = QColor("#00FF00")  # Green for suggestions
            suggest_color.setAlpha(100)  # Make it semi-transparent
            painter.fillRect(0, 0, self.width(), self.height(), suggest_color)
            
        # Draw square label if present
        if self.label:
            painter.setPen(QColor("#000000"))
            painter.drawText(5, self.height() - 5, self.label)
        
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

    def setSuggested(self, suggested: bool):
        """Set whether this square is part of the suggested move."""
        if self.suggested != suggested:
            self.suggested = suggested
            self.update()

    def setCheck(self, in_check: bool):
        """Set whether this square contains a king in check."""
        if self.in_check != in_check:
            self.in_check = in_check
            self.update()