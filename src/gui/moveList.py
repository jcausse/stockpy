"""
Custom widgets for StockPy.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

class MoveList(QWidget):
    """Widget that displays the list of moves in the game."""
    
    # Signal emitted when a move is selected
    moveSelected = pyqtSignal(int)  # Emits the move index (0-based)
    
    def __init__(self, parent=None, dark_theme=True):
        """Initialize the move list widget."""
        super().__init__(parent)
        
        # Theme colors (matching chess board colors)
        self.dark_square = "#B58863"
        self.light_square = "#F0D9B5"
        
        # Set theme
        self.dark_theme = dark_theme
        bg_color = self.dark_square if dark_theme else self.light_square
        text_color = "white" if dark_theme else "black"
        
        # Set widget style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
            }}
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Add title
        title = QLabel("Move List")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: {'#8B6B4F' if dark_theme else '#E6C9A3'};
                border: 1px solid {'#6B4F33' if dark_theme else '#D4B894'};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(title)
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                color: {text_color};
                background-color: {'#8B6B4F' if dark_theme else '#E6C9A3'};
                font-size: 14px;
                border: 1px solid {'#6B4F33' if dark_theme else '#D4B894'};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {'#6B4F33' if dark_theme else '#D4B894'};
            }}
            QListWidget::item:selected {{
                background-color: {'#6B4F33' if dark_theme else '#D4B894'};
                color: {text_color};
            }}
        """)
        layout.addWidget(self.list_widget)

        # Create move counter
        self.move_counter = 1
        
        # Connect item click signal
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        
        # Set size policy
        self.setMinimumWidth(200)

    def add_move(self, move_san: str):
        """
        Add a move to the list.
        Args:
            move_san (str): The move in Standard Algebraic Notation
        """
        if self.move_counter % 2 == 1:
            # White's move - create new item
            item_text = f"{(self.move_counter + 1) // 2}. {move_san}"
            self.list_widget.addItem(item_text)
        else:
            # Black's move - append to previous item
            prev_item = self.list_widget.item(self.list_widget.count() - 1)
            if prev_item:
                item_text = prev_item.text() + f"  {move_san}"
                prev_item.setText(item_text)
            else:
                # Handle case where black moves first (shouldn't happen in normal chess)
                item_text = f"{self.move_counter // 2}... {move_san}"
                self.list_widget.addItem(item_text)
        
        self.list_widget.scrollToBottom()
        self.move_counter += 1
     
    def _on_item_clicked(self, item):
        """Handle item click events."""
        # Calculate which move was clicked based on the item's row
        row = self.list_widget.row(item)
        text = item.text()
        
        # Extract move number from the text (e.g., "1. e4" or "1. e4  e5")
        move_number = int(text.split('.')[0])
        
        # Calculate move index based on whether it's a white or black move
        if "..." in text:  # Black's move only
            move_index = (move_number * 2) - 1
        elif "  " in text:  # Contains both moves
            # If clicked after the space, it's black's move
            clicked_pos = self.list_widget.visualItemRect(item).x()
            if clicked_pos > self.list_widget.visualItemRect(item).width() / 2:
                move_index = (move_number * 2) - 1
            else:
                move_index = (move_number * 2) - 2
        else:  # White's move only
            move_index = (move_number * 2) - 2
        
        self.moveSelected.emit(move_index)

    def reset(self):
        """Reset the move list."""
        self.list_widget.clear()
        self.move_counter = 1
