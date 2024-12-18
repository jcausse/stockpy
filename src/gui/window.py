"""
Main window implementation for StockPy.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt6.QtGui import QAction, QIcon
from .board import ChessBoard
from .moveList import MoveList
from .evaluationBar import EvaluationBar
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
        
        # Create left panel for board and evaluation
        left_panel = QWidget(central_widget)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(left_panel, stretch=2)

        # Create right panel for analysis
        right_panel = QWidget(central_widget)
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
        # Add move list to right panel
        self.move_list = MoveList()
        right_layout.addWidget(self.move_list)
        
        # Add evaluation bar to left panel
        self.eval_bar = EvaluationBar()
        left_layout.addWidget(self.eval_bar)


        # Create resource getters
        resource_getters = {
            'eval_bar': self.get_evaluation_bar,
            'move_list': self.get_move_list
        }
        
        # Create and add chess board to left panel
        self.board = ChessBoard(
            stockfish_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "stockfish", "stockfish-ubuntu-x86-64-avx2")),
            resource_getters=resource_getters
        )
        left_layout.addWidget(self.board)
        
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

        # Toggle engine suggestions and evaluation bar
        self.toggle_engine_suggestions_action = QAction("Disable suggestions", self)
        self.toggle_engine_suggestions_action.triggered.connect(self.toggle_engine_suggestions)
        self.toggle_evaluation_bar_action = QAction("Disable evaluation", self)
        self.toggle_evaluation_bar_action.triggered.connect(self.toggle_evaluation_bar)

        # Add actions to the menu
        self.board_menu = self.menuBar().addMenu("Board")
        self.board_menu.addAction(self.import_action)
        self.board_menu.addAction(self.export_action)
        self.board_menu.addSeparator()
        self.board_menu.addAction(self.reset_board_action)

        self.engine_menu = self.menuBar().addMenu("Engine")
        self.engine_menu.addAction(self.toggle_engine_suggestions_action)
        self.engine_menu.addAction(self.toggle_evaluation_bar_action)

    ##########################
    ### MENU BAR CALLBACKS ###
    ##########################

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
        self.eval_bar.reset()
        self.board.reset()

    def toggle_engine_suggestions(self):
        """Toggle engine suggestions and update menu text."""
        self.board.toggle_engine_suggestions()
        is_enabled = self.board.engine_suggestions_enabled
        self.toggle_engine_suggestions_action.setText(
            "Disable suggestions" if is_enabled else "Enable suggestions"
        )

    def toggle_evaluation_bar(self):
        """Toggle the evaluation bar."""
        self.board.toggle_evaluation_bar()
        is_enabled = self.board.engine_evaluation_enabled
        self.toggle_evaluation_bar_action.setText(
            "Disable evaluation" if is_enabled else "Enable evaluation"
        )

    def closeEvent(self, event):
        """Handle the window close event."""
        if self.board and self.board.engine:
            self.board.engine.quit()
            self.board.engine = None
        super().closeEvent(event)

    ########################
    ### RESOURCE GETTERS ###
    ########################

    def get_evaluation_bar(self) -> EvaluationBar:
        """Get the evaluation bar."""
        return self.eval_bar

    def get_move_list(self) -> MoveList:
        """Get the move list."""
        return self.move_list
