"""
Main window implementation for StockPy.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from .board import ChessBoard
from .moveList import MoveList
import os

class MainWindow(QMainWindow):
    """
    Main window class for the StockPy application.
    
    This window serves as the container for all other widgets and handles
    the main application layout.
    """
    
    def __init__(self):
        """Initialize the main window and set up the UI."""
        super().__init__(None)
        
        # Set window properties
        self.setWindowTitle('StockPy')
        self.setMinimumSize(1000, 800)
        
        # Create central widget and layout
        central_widget = QWidget(None)
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create and add chess board
        self.board = ChessBoard(stockfish_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "stockfish", "stockfish-ubuntu-x86-64-avx2")))
        main_layout.addWidget(self.board, stretch=2)
        
        # Create right panel for analysis
        right_panel = QWidget(central_widget)
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
        # Add move list to right panel
        self.move_list = MoveList()
        right_layout.addWidget(self.move_list)
        
        # Connect move list signals
        self.move_list.moveSelected.connect(self.board.jump_to_move)
        
        # TODO: Add engine control widgets
        # TODO: Add analysis widget
