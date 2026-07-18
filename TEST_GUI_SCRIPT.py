import chess
from Chess_GUI import ChessGUI

def main():
    gui = ChessGUI()
    gui.start()

    board = chess.Board()

    while not board.is_game_over():
        # Wait for a user move from the GUI
        user_move = gui.wait_for_user_move()

        # Handle promotion auto-queen if needed
        if len(user_move) == 4:  # might be missing promotion piece
            move = chess.Move.from_uci(user_move)
            piece = board.piece_at(move.from_square)
            if piece and piece.piece_type == chess.PAWN:
                rank = chess.square_rank(move.to_square)
                if rank == 0 or rank == 7:
                    user_move = user_move + "q"  # auto queen

        board.push_uci(user_move)
        gui.update_fen(board.fen())

    print("Game over:", board.result())

if __name__ == "__main__":
    main()
