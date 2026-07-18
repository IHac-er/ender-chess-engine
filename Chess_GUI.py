import tkinter as tk
import chess
import queue

class ChessGUI:
    def __init__(self):
        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Ender v1 Chess Engine")
        self.root.resizable(False, False)
        self.last_move = None
        self.legal_targets = []   # <- fix the name

        # Chess board state
        self.board = chess.Board()
        self.flip = True
        self.selected_square = None

        # Move queue (to communicate with main.py)
        self.move_queue = queue.Queue()

        # Canvas setup
        self.canvas_size = 720
        self.square_size = self.canvas_size // 8
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        # Load piece images
        self.images = {}
        self.piece_files = {
            "P": "wP.png", "N": "wN.png", "B": "wB.png",
            "R": "wR.png", "Q": "wQ.png", "K": "wK.png",
            "p": "bP.png", "n": "bN.png", "b": "bB.png",
            "r": "bR.png", "q": "bQ.png", "k": "bK.png",
        }
        for symbol, filename in self.piece_files.items():
            img = tk.PhotoImage(file=f"chess_pieces/{filename}")
            img = img.subsample(22, 22)
            self.images[symbol] = img

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")

        # Draw checkerboard
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = "#EEEED2" if (row + col) % 2 == 0 else "#769656"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
        
        # ✅ Highlight last move
        if self.last_move:
            for square in self.last_move:
                if self.flip:
                    row = square // 8
                    col = 7 - (square % 8)
                else:
                    row = 7 - (square // 8)
                    col = square % 8
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="yellow", stipple="gray25", outline=""
                )

        # Draw pieces
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                symbol = piece.symbol()
                if self.flip:
                    row = square // 8
                    col = 7 - (square % 8)
                else:
                    row = 7 - (square // 8)
                    col = square % 8
                x = col * self.square_size + self.square_size // 2
                y = row * self.square_size + self.square_size // 2
                self.canvas.create_image(x, y, image=self.images[symbol])
        
        # highlight legal moves (small circle on target squares)
        for sq in getattr(self, "legal_targets", []):
            if self.flip:
                row = sq // 8
                col = 7 - (sq % 8)
            else:
                row = 7 - (sq // 8)
                col = sq % 8

            cx = col * self.square_size + self.square_size // 2
            cy = row * self.square_size + self.square_size // 2
            r = self.square_size // 10
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#BBBBBB", stipple="gray12", outline="")

    def on_click(self, event):
        col = event.x // self.square_size
        row = event.y // self.square_size

        if self.flip:
            square = row * 8 + (7 - col)
        else:
            square = (7 - row) * 8 + col

        square_name = chess.square_name(square)
        piece = self.board.piece_at(square)

        # --- Case 1: No piece selected yet ---
        if self.selected_square is None:
            if piece and piece.color == self.board.turn:  # must be player's piece
                self.selected_square = square_name
                # store all legal targets for highlighting
                self.legal_targets = [
                    move.to_square for move in self.board.legal_moves if move.from_square == square
                ]
                self.draw_board()
            return

        # --- Case 2: Selecting another of my own pieces instead of moving ---
        if piece and piece.color == self.board.turn:
            self.selected_square = square_name
            self.legal_targets = [
                move.to_square for move in self.board.legal_moves if move.from_square == square
            ]
            self.draw_board()
            return

        # --- Case 3: Trying to make a move ---
        move_uci = self.selected_square + square_name
        move = chess.Move.from_uci(move_uci)

        # ✅ If it's a pawn promotion, append "q"
        piece = self.board.piece_at(move.from_square)
        if piece and piece.piece_type == chess.PAWN:
            rank = chess.square_rank(move.to_square)
            if rank == 0 or rank == 7:  # last rank
                move = chess.Move.from_uci(move_uci + "q")

        # Now check if the (possibly updated) move is legal
        if move in self.board.legal_moves:
            self.board.push(move)
            self.last_move = (move.from_square, move.to_square)
            self.selected_square = None
            self.legal_targets = []
            self.draw_board()
            self.check_game_over()

            # ✅ Send correct move string
            self.move_queue.put(move.uci())
        else:
            # cancel selection
            self.selected_square = None
            self.legal_targets = []
            self.draw_board()

    def update_fen(self, fen, last_move=None):
        self.board.set_fen(fen)

        # ✅ record last move if given
        if last_move:
            move = last_move
            self.last_move = (move.from_square, move.to_square)

        self.draw_board()
        self.check_game_over()


    def wait_for_user_move(self):
        """Block until user makes a move, then return it as UCI string."""
        self.root.update()  # refresh GUI
        while self.move_queue.empty():
            self.root.update()  # process Tkinter events
        return self.move_queue.get()
    
    def check_game_over(self):
        """Check if the game is over and display result."""
        if self.board.is_game_over(claim_draw=True):
            result = self.board.result(claim_draw=True)

            if self.board.is_checkmate():
                winner = "White" if not self.board.turn else "Black"
                msg = f"Checkmate! {winner} wins!"
            elif self.board.is_stalemate():
                msg = "Draw by stalemate."
            elif self.board.is_insufficient_material():
                msg = "Draw by insufficient material."
            elif self.board.is_fivefold_repetition():
                msg = "Draw by fivefold repetition."
            elif self.board.is_seventyfive_moves():
                msg = "Draw by 75-move rule."
            else:
                msg = f"Game over: {result}"

            # Overlay text on board
            self.canvas.create_rectangle(0, self.canvas_size//2 - 40,
                                        self.canvas_size, self.canvas_size//2 + 40,
                                        fill="black", stipple="gray50")
            self.canvas.create_text(self.canvas_size//2, self.canvas_size//2,
                                    text=msg, fill="white", font=("Arial", 24, "bold"))
            print(msg)
            return True
        return False

    def start(self):
        """Call once at the beginning to open window without blocking main loop."""
        self.root.update()
    