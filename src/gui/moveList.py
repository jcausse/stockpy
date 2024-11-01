"""
Custom widgets for StockPy.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class MoveList(QWidget):
    """Widget that displays the list of moves in the game."""
    
    def __init__(self, parent=None):
        """
        Initialize the move list widget.
        
        Args:
            parent (QWidget, optional): Parent widget
            dark_theme (bool, optional): Whether to use dark theme. Defaults to True.
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Add title
        title = QLabel("Move List")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                border: 1px solid white;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(title)
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                color: white;
                font-size: 12px;
                border: 1px solid white;
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid white;
            }}
            QListWidget::item:selected {{
                background-color: white;
                color: white;
            }}
        """)
        layout.addWidget(self.list_widget)
        
        # Set size policy
        self.setMinimumWidth(200)
        
    def add_move(self, move_number: int, move_san: str):
        """
        Add a move to the list.
        
        Args:
            move_number (int): The move number
            move_san (str): The move in Standard Algebraic Notation
        """
        if move_number % 2 == 1:
            # White's move
            item_text = f"{(move_number + 1) // 2}. {move_san}"
        else:
            # Black's move - append to previous item
            prev_item = self.list_widget.item(self.list_widget.count() - 1)
            if prev_item:
                item_text = prev_item.text() + f"  {move_san}"
                prev_item.setText(item_text)
                return
            else:
                item_text = f"{move_number // 2}... {move_san}"

        self.list_widget.addItem(item_text)
        self.list_widget.scrollToBottom()
        
    def clear(self):
        """Clear the move list."""
        self.list_widget.clear()
