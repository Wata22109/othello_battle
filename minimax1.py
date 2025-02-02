import copy
import time
from typing import List, Tuple, Optional

class OthelloBoard:
    def __init__(self):
        self.EMPTY = 0
        self.BLACK = 1
        self.WHITE = 2
        self.BOARD_SIZE = 8
        self.board = [[self.EMPTY] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        # 初期配置
        self.board[3][3] = self.WHITE
        self.board[3][4] = self.BLACK
        self.board[4][3] = self.BLACK
        self.board[4][4] = self.WHITE
        
    def print_board(self):
        print("  0 1 2 3 4 5 6 7")
        for i in range(self.BOARD_SIZE):
            print(f"{i}", end=" ")
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == self.EMPTY:
                    print(".", end=" ")
                elif self.board[i][j] == self.BLACK:
                    print("B", end=" ")
                else:
                    print("W", end=" ")
            print()

    def is_valid_move(self, row: int, col: int, player: int) -> bool:
        if row < 0 or row >= self.BOARD_SIZE or col < 0 or col >= self.BOARD_SIZE:
            return False
        if self.board[row][col] != self.EMPTY:
            return False
        
        opponent = self.WHITE if player == self.BLACK else self.BLACK
        directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]
        
        for dx, dy in directions:
            x, y = row + dx, col + dy
            if not (0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE):
                continue
            if self.board[x][y] != opponent:
                continue
                
            x, y = x + dx, y + dy
            while 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
                if self.board[x][y] == self.EMPTY:
                    break
                if self.board[x][y] == player:
                    return True
                x, y = x + dx, y + dy
        return False

    def get_valid_moves(self, player: int) -> List[Tuple[int, int]]:
        valid_moves = []
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.is_valid_move(i, j, player):
                    valid_moves.append((i, j))
        return valid_moves

    def make_move(self, row: int, col: int, player: int) -> None:
        if not self.is_valid_move(row, col, player):
            return
            
        self.board[row][col] = player
        opponent = self.WHITE if player == self.BLACK else self.BLACK
        directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]
        
        for dx, dy in directions:
            to_flip = []
            x, y = row + dx, col + dy
            
            while 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
                if self.board[x][y] == self.EMPTY:
                    break
                if self.board[x][y] == opponent:
                    to_flip.append((x, y))
                elif self.board[x][y] == player:
                    for flip_x, flip_y in to_flip:
                        self.board[flip_x][flip_y] = player
                    break
                x, y = x + dx, y + dy

    def get_score(self) -> Tuple[int, int]:
        black_count = sum(row.count(self.BLACK) for row in self.board)
        white_count = sum(row.count(self.WHITE) for row in self.board)
        return black_count, white_count

class OthelloAI:
    def __init__(self, max_depth: int = 5, max_time: float = 5.0):
        self.max_depth = max_depth
        self.max_time = max_time
        self.start_time = 0
        
    def evaluate_board(self, board: OthelloBoard, player: int) -> int:
        # 評価関数
        # コーナーの重み付けを高くする
        weights = [
            [100, -20, 10, 5, 5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10, 5, 5, 10, -20, 100]
        ]
        
        score = 0
        opponent = board.WHITE if player == board.BLACK else board.BLACK
        
        for i in range(board.BOARD_SIZE):
            for j in range(board.BOARD_SIZE):
                if board.board[i][j] == player:
                    score += weights[i][j]
                elif board.board[i][j] == opponent:
                    score -= weights[i][j]
                    
        return score

    def is_timeout(self) -> bool:
        return time.time() - self.start_time > self.max_time

    def minimax(self, board: OthelloBoard, depth: int, alpha: int, beta: int, 
                maximizing_player: bool, player: int) -> Tuple[int, Optional[Tuple[int, int]]]:
        if depth == 0 or self.is_timeout():
            return self.evaluate_board(board, player), None
            
        valid_moves = board.get_valid_moves(player if maximizing_player else 
                                          (board.WHITE if player == board.BLACK else board.BLACK))
        
        if not valid_moves:
            return self.evaluate_board(board, player), None
            
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                new_board = copy.deepcopy(board)
                new_board.make_move(move[0], move[1], player)
                eval_score, _ = self.minimax(new_board, depth-1, alpha, beta, False, player)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                    
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            opponent = board.WHITE if player == board.BLACK else board.BLACK
            for move in valid_moves:
                new_board = copy.deepcopy(board)
                new_board.make_move(move[0], move[1], opponent)
                eval_score, _ = self.minimax(new_board, depth-1, alpha, beta, True, player)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                    
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_move(self, board: OthelloBoard, player: int) -> Optional[Tuple[int, int]]:
        self.start_time = time.time()
        best_move = None
        
        # 反復深化
        for depth in range(1, self.max_depth + 1):
            if self.is_timeout():
                break
            _, move = self.minimax(board, depth, float('-inf'), float('inf'), True, player)
            if move is not None:
                best_move = move
                
        return best_move

def play_game():
    board = OthelloBoard()
    ai = OthelloAI()
    current_player = board.BLACK  # 黒から開始
    
    while True:
        board.print_board()
        black_score, white_score = board.get_score()
        print(f"Black: {black_score}, White: {white_score}")
        
        valid_moves = board.get_valid_moves(current_player)
        if not valid_moves:
            if not board.get_valid_moves(board.WHITE if current_player == board.BLACK else board.BLACK):
                print("Game Over!")
                if black_score > white_score:
                    print("Black wins!")
                elif white_score > black_score:
                    print("White wins!")
                else:
                    print("Draw!")
                break
            print(f"No valid moves for {'Black' if current_player == board.BLACK else 'White'}")
            current_player = board.WHITE if current_player == board.BLACK else board.BLACK
            continue
            
        if current_player == board.BLACK:
            print("Your turn (Black)")
            while True:
                try:
                    row = int(input("Enter row (0-7): "))
                    col = int(input("Enter column (0-7): "))
                    if (row, col) in valid_moves:
                        break
                    print("Invalid move!")
                except ValueError:
                    print("Please enter numbers!")
        else:
            print("AI's turn (White)")
            row, col = ai.get_move(board, current_player)
            print(f"AI plays: {row}, {col}")
            
        board.make_move(row, col, current_player)
        current_player = board.WHITE if current_player == board.BLACK else board.BLACK

if __name__ == "__main__":
    play_game()