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

    def get_best_move(self, board, time_limit=1.0) -> chess.Move:
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
    
    def get_evaluation(self, board, time_limit=1.0) -> float:
        """
        Get the evaluation of the current position.
        
        Args:
            board (chess.Board): The current board position
            time_limit (float): Time to think in seconds
            
        Returns:
            float: Evaluation in pawns (positive = white advantage)
        """
        try:
            info = self.engine.analyse(board, chess.engine.Limit(time=time_limit))
            if 'score' in info:
                score = info['score'].white()
                # Convert mate scores to high numerical values
                if score.is_mate():
                    # Use ±100 for mate scores, with sign indicating which side has mate
                    return 100.0 if score.mate() > 0 else -100.0
                # Convert centipawns to pawns
                return float(score.score()) / 100.0
        except Exception as e:
            print(f"Error getting evaluation: {e}")
        return 0.0

    def quit(self):
        """Quit the Stockfish engine."""
        if self.engine:
            self.engine.quit()