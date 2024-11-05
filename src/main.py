"""
StockPy - A multi-platform Python3 frontend for Stockfish.

This module serves as the entry point for the StockPy application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.window import MainWindow

def main():
    """
    Main entry point of the application.
    
    Creates the QApplication instance, sets up the main window,
    and starts the event loop.
    """
    # Initialize the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("StockPy")
    app.setApplicationDisplayName("StockPy")
    app.setDesktopFileName("StockPy")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
