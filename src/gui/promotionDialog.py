"""
Promotion dialog for StockPy.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton

class PromotionDialog(QDialog):
    """Dialog for selecting pawn promotion piece."""
    
    def __init__(self, parent=None):
        """Initialize the promotion dialog."""
        super().__init__(parent)
        self.setWindowTitle("Choose Promotion Piece")
        self.setMinimumSize(200, 150)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Create buttons for each piece type
        self.pieces = {
            'q': 'Queen',
            'r': 'Rook',
            'b': 'Bishop',
            'n': 'Knight'
        }
        
        self.selected_piece = None
        
        for piece_type, piece_name in self.pieces.items():
            button = QPushButton(piece_name)
            button.clicked.connect(lambda checked, p=piece_type: self.piece_selected(p))
            layout.addWidget(button)
            
        self.setLayout(layout)
        
    def piece_selected(self, piece_type: str):
        """Handle piece selection."""
        self.selected_piece = piece_type
        self.accept()
