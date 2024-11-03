import chess.engine
import os

class StockfishEngine:
    def __init__(self, stockfish_path):
        """Initialize the Stockfish engine."""
        self.stockfish_path = stockfish_path
        self.engine = None

    def start(self):
        """Start the Stockfish engine."""
        self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

    def get_best_move(self, board, time_limit=1.0):
        """
        Get the best move for the current board position.
        
        Args:
            board (chess.Board): The current board position
            time_limit (float): Time to think in seconds
            
        Returns:
            chess.Move: The best move suggested by Stockfish
        """
        with self.engine.analysis(board, chess.engine.Limit(time=time_limit)) as analysis:
            for info in analysis:
                if "pv" in info:
                    return info["pv"][0]
        return None

    def quit(self):
        """Quit the Stockfish engine."""
        if self.engine:
            self.engine.quit()