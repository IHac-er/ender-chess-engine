#Importing necessary python libraries
import chess 

piece_value = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

#Function -> To order moves from good to bad to improve alpha-beta pruning
def order_moves(board):
    captures = []
    promotions = []
    checks = []
    quiet_moves = []

    for move in board.legal_moves:
        # Promotions
        if move.promotion is not None:
            promotions.append(move)
            continue

        # Captures (MVV-LVA style)
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            if victim and attacker:
                score = piece_value[victim.piece_type] * 10 - piece_value[attacker.piece_type]
            else:
                score = 0
            captures.append((score, move))
            continue

        # Checks
        if board.gives_check(move):
            checks.append(move)
        else:
            quiet_moves.append(move)

    # Sort captures by MVV-LVA (descending)
    captures.sort(key=lambda x: x[0], reverse=True)
    captures = [m for _, m in captures]

    # Sort promotions
    promotions.sort(key=lambda m: piece_value[m.promotion], reverse=True)

    # Build final move list
    ordered = []
    ordered.extend(captures)
    ordered.extend(promotions)
    ordered.extend(checks)
    ordered.extend(quiet_moves)

    return ordered