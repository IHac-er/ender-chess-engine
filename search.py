#Importing necessary python libraries
import chess 

#Importing necessary engine files 
from evaluation import evaluate 
from move_ordering import order_moves

def quiescence(board, alpha, beta, max_player):
    """
    Simple quiescence: explore captures & promotions to avoid horizon effect.
    `max_player` is True if we are maximizing at this node (root side), False otherwise.
    This mirrors your minimax sign (not negamax).
    """
    stand = evaluate(board)

    # Quick cutoff on the stand-pat
    if max_player:
        if stand >= beta:
            return stand
        if stand > alpha:
            alpha = stand
    else:
        if stand <= alpha:
            return stand
        if stand < beta:
            beta = stand

    # Consider only captures and promotions (ordered by your order_moves)
    for move in order_moves(board):
        if not (board.is_capture(move) or move.promotion is not None):
            continue
        board.push(move)
        score = quiescence(board, alpha, beta, not max_player)
        board.pop()

        if max_player:
            if score > alpha:
                alpha = score
            if alpha >= beta:
                return alpha
        else:
            if score < beta:
                beta = score
            if beta <= alpha:
                return beta

    return alpha if max_player else beta

#Function -> From a given board state play moves for both the side until checkmate, draw or reaches the maximum specified depth 
#and returns the best move based on score of each move
def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf')):
    if board.is_game_over(claim_draw=True): 
        return evaluate(board)
    
    if depth <= 0: 
        return quiescence(board, alpha, beta, max_player)
    
    if max_player:
        best_score = float('-inf')
        for move in order_moves(board):
            board.push(move)
            score = minimax(board, depth - 1, False, alpha, beta)
            board.pop()
            if score > best_score: 
                best_score = score
            alpha = max(alpha, score)
            if beta <= alpha: 
               break 
        return best_score
    
    else: 
        best_score = float('inf')
        for move in order_moves(board):
            board.push(move)
            score = minimax(board, depth - 1, True, alpha, beta)
            board.pop() 
            if score < best_score:
                best_score = score
            beta = min(beta, score)
            if beta <= alpha: 
                break  
        return best_score 

#Function -> Takes a board position and generates all legal moves and then passes each legal move to minimax() to get its score 
#and then finds the best score (best move)
def best_move(board, depth=2):
    best_move = None 
    max_player = board.turn
    best_score = float('-inf') if max_player else float('inf')
    for move in order_moves(board):
        board.push(move)
        score = minimax(board, depth - 1, not max_player)
        board.pop()
        print(move, score)
        if (score >= 100000 and board.turn == chess.WHITE) or (score <= -100000 and board.turn == chess.BLACK): 
            return move
        if max_player and score > best_score: 
            best_score = score 
            best_move = move
        elif not max_player and score < best_score: 
            best_score = score 
            best_move = move
    return best_move 