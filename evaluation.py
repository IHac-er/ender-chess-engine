import chess

PIECE_VALUE = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   20000,
}

MOBILITY_WEIGHT = 4
BISHOP_PAIR_BONUS = 50
MATE_SCORE = 100_000

# ---- Helpers ----
def material_score(board):
    score = 0
    for piece_type, value in PIECE_VALUE.items():
        score += value * (len(board.pieces(piece_type, chess.WHITE)) -
                          len(board.pieces(piece_type, chess.BLACK)))
    # bishop pair bonus
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += BISHOP_PAIR_BONUS
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= BISHOP_PAIR_BONUS
    return score

def mobility_score(board):
    # Faster and simpler: use number of legal moves per side
    wb = board.copy(stack=False); wb.turn = chess.WHITE
    bb = board.copy(stack=False); bb.turn = chess.BLACK
    white_moves = sum(1 for _ in wb.legal_moves)
    black_moves = sum(1 for _ in bb.legal_moves)
    return (white_moves - black_moves) * MOBILITY_WEIGHT

# ---- Main evaluate ----
def evaluate(board):
    # Terminal positions
    if board.is_checkmate():
        # side to move is checkmated -> very bad for that side
        return -MATE_SCORE if board.turn else MATE_SCORE

    # Typical draws
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    # threefold or 50-move claims are draws; prefer can_claim_* variants
    if board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
        return 0

    # Non-terminal: sum heuristics
    score = material_score(board)
    score += mobility_score(board)

    # (Optional) add other heuristics later: pawn-structure, king-safety, PST, passed pawns, etc.
    return score