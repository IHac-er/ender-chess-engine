#Importing necessary python libraries 
import chess 
import time 

#Importing necessary engine files 
from search import best_move 
from openings import openings
from Chess_GUI import ChessGUI

#Function -> To set the board according to the user input fen and then return the best move for that board position
def get_best_move_position():
    while True: 
        fen = input("Enter a FEN (type init for default position, quit to exit): ")
        if fen.lower() == "quit":
            break 
        if fen.lower() == "init":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        try:
            board = chess.Board(fen)
        except ValueError: 
            print("Invalid FEN! Enter a VALID FEN")
            continue
        start = time.time()
        move = best_move(board)
        print(f"Best move: {move}, Time Taken: {time.time() - start:.2f}")

class ChessApp:
    def __init__(self):
        self.gui = ChessGUI()
        self.board = chess.Board()

    def start(self):
        """Start the GUI and run the game loop in background."""
        self.gui.start()
        self.gui.root.after(100, self.game_loop)  # Schedule loop
        self.gui.root.mainloop()

    def game_loop(self):
        """One cycle of the game loop. Reschedules itself until game ends."""
        if self.board.is_game_over():
            self.gui.update_fen(self.board.fen())
            return  # stop loop if game over

        # Engine move
        if self.board.fen() in openings and False:
            engine_move = openings[self.board.fen()]
            self.board.push_uci(engine_move)
            self.gui.update_fen(self.board.fen(), last_move=engine_move)
        else:
            engine_move = best_move(self.board)
            try:
                if engine_move in self.board.legal_moves:
                    self.board.push(engine_move)
                else:
                    print(f"Engine suggested illegal move: {engine_move}")
            except ValueError:
                print(f"Engine returned invalid move string: {engine_move}")
            print(f"Best move: {engine_move}")
            self.gui.update_fen(self.board.fen(), last_move=engine_move)

        # Wait for human move
        move = self.gui.wait_for_user_move()
        self.board.push_uci(move)
        self.gui.update_fen(self.board.fen())

        # Schedule next cycle
        self.gui.root.after(100, self.game_loop)


#This gets executed when this script is ran directly (meaning it could also be called from a different script using another funciton) 
if __name__ == "__main__":
    get_best_move_position()

