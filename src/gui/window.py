"""
Main window implementation for StockPy.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt6.QtGui import QAction, QIcon
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

        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'pieces', 'white_pawn.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
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

        ########################
        ### MENU BAR ACTIONS ###
        ########################

        # Import / Export PGN
        self.import_action = QAction("Import PGN", self)
        self.import_action.triggered.connect(self.import_pgn)
        self.export_action = QAction("Export PGN", self)
        self.export_action.triggered.connect(self.export_pgn)

        # Clear board
        self.reset_board_action = QAction("Reset", self)
        self.reset_board_action.triggered.connect(self.reset_board)

        # Toggle engine suggestions
        self.toggle_engine_suggestions_action = QAction("Disable suggestions", self)
        self.toggle_engine_suggestions_action.triggered.connect(self.toggle_engine_suggestions)

        # Add actions to the menu
        self.board_menu = self.menuBar().addMenu("Board")
        self.board_menu.addAction(self.import_action)
        self.board_menu.addAction(self.export_action)
        self.board_menu.addSeparator()
        self.board_menu.addAction(self.reset_board_action)

        self.engine_menu = self.menuBar().addMenu("Engine")
        self.engine_menu.addAction(self.toggle_engine_suggestions_action)

    def import_pgn(self):
        """Open a file dialog to import a PGN file."""
        pgn_path, _ = QFileDialog.getOpenFileName(self, "Open PGN", "", "PGN Files (*.pgn)")
        if pgn_path:
            self.board.import_pgn(pgn_path)

    def export_pgn(self):
        """Open a file dialog to export the current position as a PGN file."""
        pgn_path, _ = QFileDialog.getSaveFileName(self, "Save PGN", "", "PGN Files (*.pgn)")
        if pgn_path:
            self.board.export_pgn(pgn_path)

    def reset_board(self):
        self.move_list.reset()
        self.board.reset()

    def toggle_engine_suggestions(self):
        """Toggle engine suggestions and update menu text."""
        self.board.toggle_engine_suggestions()
        is_enabled = self.board.engine_suggestions_enabled
        self.toggle_engine_suggestions_action.setText(
            "Disable suggestions" if is_enabled else "Enable suggestions"
        )

    def closeEvent(self, event):
        """Handle the window close event."""
        if self.board and self.board.engine:
            self.board.engine.quit()
            self.board.engine = None
        super().closeEvent(event)
