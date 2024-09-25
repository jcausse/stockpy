import chess
import chess.engine
import chess.pgn

# Path to the Stockfish executable
stockfish_path = './stockfish/stockfish-windows-x86-64-avx2'

# Initialize the Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

def analyze_pgn(pgn_file_path):
    # Open and parse the PGN file
    with open(pgn_file_path, "r") as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    
    board = game.board()
    
    print("Game Analysis:")
    
    # Iterate through each move in the game
    for move_number, move in enumerate(game.mainline_moves()):
        board.push(move)
        
        # Analyze the position after the move
        result = engine.play(board, chess.engine.Limit(time=2.0))
        best_move = result.move
        evaluation = engine.analyse(board, chess.engine.Limit(time=2.0))
        
        # Determine the color of the player to move
        color = "White" if board.turn == chess.WHITE else "Black"
        
        # Print the best move and evaluation
        print(f"Move {move_number + 1}:")
        print(f"Position: {board.fen()}")
        print(f"Best Move for {color}: {best_move}")
        print(f"Evaluation: {evaluation['score'].relative.score(mate_score=10000)}")
        print()
    
    # Close the Stockfish engine
    engine.quit()

if __name__ == "__main__":
    pgn_file_path = "game.pgn"  # Replace with your PGN file path
    analyze_pgn(pgn_file_path)
