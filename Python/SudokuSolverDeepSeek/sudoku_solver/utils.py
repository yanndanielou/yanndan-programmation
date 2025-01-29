def is_valid_board(board):
    for row in board:
        if len(row) != 9:
            return False
    return len(board) == 9
