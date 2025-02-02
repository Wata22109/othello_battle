import numpy as np
import random

# Constants for the game
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

class OthelloGame:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)  # 8x8のボードを作成（0: EMPTY）
        self.board[3, 3] = WHITE                 # 初期配置の白石
        self.board[3, 4] = BLACK                 # 初期配置の黒石
        self.board[4, 3] = BLACK                 # 初期配置の黒石
        self.board[4, 4] = WHITE                 # 初期配置の白石
        self.current_player = BLACK              # 最初のプレイヤーを黒に設定

    def is_on_board(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def get_valid_moves(self):
        valid_moves = []
        for x in range(8):
            for y in range(8):
                if self.board[x, y] == EMPTY and self.is_valid_move(x, y):
                    valid_moves.append((x, y))
        return valid_moves

    def is_valid_move(self, x, y):
        if self.board[x, y] != EMPTY:
            return False
        opponent = WHITE if self.current_player == BLACK else BLACK
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if self.is_on_board(nx, ny) and self.board[nx, ny] == opponent:
                while self.is_on_board(nx, ny) and self.board[nx, ny] == opponent:
                    nx += dx
                    ny += dy
                if self.is_on_board(nx, ny) and self.board[nx, ny] == self.current_player:
                    return True
        return False

    def make_move(self, x, y):
        if not self.is_valid_move(x, y):
            return False
        self.board[x, y] = self.current_player
        opponent = WHITE if self.current_player == BLACK else BLACK
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            cells_to_flip = []
            while self.is_on_board(nx, ny) and self.board[nx, ny] == opponent:
                cells_to_flip.append((nx, ny))
                nx += dx
                ny += dy
            if self.is_on_board(nx, ny) and self.board[nx, ny] == self.current_player:
                for fx, fy in cells_to_flip:
                    self.board[fx, fy] = self.current_player
        return True

    def switch_player(self):
        self.current_player = WHITE if self.current_player == BLACK else BLACK

    def is_game_over(self):
        return not self.get_valid_moves() and not self.has_valid_moves(WHITE) and not self.has_valid_moves(BLACK)

    def has_valid_moves(self, player):
        temp_player = self.current_player
        self.current_player = player
        valid_moves = self.get_valid_moves()
        self.current_player = temp_player
        return len(valid_moves) > 0

    def display_board(self):
        """ボードを表示する"""
        symbols = {EMPTY: '.', BLACK: '○', WHITE: '●'}
        print("  " + " ".join(map(str, range(8))))
        for i, row in enumerate(self.board):
            print(f"{i} " + " ".join(symbols[cell] for cell in row))
        print()

class MinimaxAI:
    def __init__(self, depth):
        self.depth = depth

    def choose_move(self, valid_moves, game):
        best_move = None
        best_score = float('-inf') if game.current_player == BLACK else float('inf')

        for move in valid_moves:
            temp_game = OthelloGame()
            temp_game.board = game.board.copy()
            temp_game.current_player = game.current_player
            temp_game.make_move(*move)

            score = self.minimax(temp_game, self.depth - 1, float('-inf'), float('inf'), False if game.current_player == BLACK else True)

            if game.current_player == BLACK and score > best_score:
                best_score = score
                best_move = move
            elif game.current_player == WHITE and score < best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, game, depth, alpha, beta, is_maximizing):
        if depth == 0 or game.is_game_over():
            return np.sum(game.board == BLACK) - np.sum(game.board == WHITE)

        valid_moves = game.get_valid_moves()
        if not valid_moves:
            temp_game = OthelloGame()
            temp_game.board = game.board.copy()
            temp_game.current_player = game.current_player
            temp_game.switch_player()
            return self.minimax(temp_game, depth, alpha, beta, not is_maximizing)

        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                temp_game = OthelloGame()
                temp_game.board = game.board.copy()
                temp_game.current_player = game.current_player
                temp_game.make_move(*move)
                eval = self.minimax(temp_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                temp_game = OthelloGame()
                temp_game.board = game.board.copy()
                temp_game.current_player = game.current_player
                temp_game.make_move(*move)
                eval = self.minimax(temp_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

class RandomAI:
    def choose_move(self, valid_moves, game):
        return random.choice(valid_moves) if valid_moves else None

class GreedyAI:
    def choose_move(self, valid_moves, game):
        max_flips = -1
        best_move = None
        for move in valid_moves:
            temp_game = OthelloGame()
            temp_game.board = game.board.copy()
            temp_game.current_player = game.current_player
            temp_game.make_move(*move)
            flips = np.sum(temp_game.board == game.current_player) - np.sum(game.board == game.current_player)
            if flips > max_flips:
                max_flips = flips
                best_move = move
        return best_move

def play_game(black_ai, white_ai):
    game = OthelloGame()
    while not game.is_game_over():
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            game.switch_player()
            continue

        if game.current_player == BLACK:
            move = black_ai.choose_move(valid_moves, game)
        else:
            move = white_ai.choose_move(valid_moves, game)

        if move:
            game.make_move(*move)
            game.switch_player()

        game.display_board()

    print("Game Over")
    print("Black:", np.sum(game.board == BLACK))
    print("White:", np.sum(game.board == WHITE))

if __name__ == "__main__":
    print("MinimaxAI vs RandomAI")
    minimax_ai = MinimaxAI(depth=3)
    random_ai = RandomAI()
    play_game(minimax_ai, random_ai)