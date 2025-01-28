import logging

# Configuration des logs avec le nom du fichier et le numéro de ligne
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)


def is_valid(board, row, col, num):
    logging.debug(f"Checking if {num} is valid at ({row}, {col})")
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            logging.debug(f"Number {num} is invalid at ({row}, {col})")
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                logging.debug(f"Number {num} is invalid in subgrid at ({row}, {col})")
                return False
    logging.debug(f"Number {num} is valid at ({row}, {col})")
    return True


def solve_sudoku(board):
    logging.info("Starting to solve Sudoku")
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        logging.info(f"Placed {num} at ({row}, {col})")
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                        logging.info(f"Backtracking at ({row}, {col})")
                return False
    logging.info("Sudoku solved successfully")
    return True
