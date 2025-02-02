import numpy as np
from copy import deepcopy
from heapq import heappush, heappop
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class SearchNode:
    f_score: float
    g_score: int
    state: 'OthelloState'
    path: List[Tuple[int, int]]
    
    def __lt__(self, other):
        return self.f_score < other.f_score

class OthelloState:
    def __init__(self, board=None):
        if board is None:
            # 8x8の盤面を初期化
            self.board = np.zeros((8, 8), dtype=int)
            # 初期配置
            self.board[3:5, 3:5] = [[1, -1], [-1, 1]]
        else:
            self.board = board
        
    def get_valid_moves(self, player):
        valid_moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j, player):
                    valid_moves.append((i, j))
        return valid_moves
    
    def is_valid_move(self, row, col, player):
        if self.board[row, col] != 0:
            return False
            
        directions = [(0,1), (1,0), (0,-1), (-1,0), 
                     (1,1), (-1,-1), (1,-1), (-1,1)]
                     
        for dx, dy in directions:
            if self._would_flip(row, col, dx, dy, player):
                return True
        return False
    
    def _would_flip(self, row, col, dx, dy, player):
        x, y = row + dx, col + dy
        to_flip = []
        
        while 0 <= x < 8 and 0 <= y < 8:
            if self.board[x, y] == 0:
                return False
            if self.board[x, y] == player:
                return len(to_flip) > 0
            to_flip.append((x, y))
            x, y = x + dx, y + dy
            
        return False
    
    def make_move(self, row, col, player):
        if not self.is_valid_move(row, col, player):
            return None
            
        new_state = OthelloState(self.board.copy())
        new_state.board[row, col] = player
        
        directions = [(0,1), (1,0), (0,-1), (-1,0), 
                     (1,1), (-1,-1), (1,-1), (-1,1)]
                     
        for dx, dy in directions:
            new_state._flip_direction(row, col, dx, dy, player)
            
        return new_state
    
    def _flip_direction(self, row, col, dx, dy, player):
        x, y = row + dx, col + dy
        to_flip = []
        
        while 0 <= x < 8 and 0 <= y < 8:
            if self.board[x, y] == 0:
                return
            if self.board[x, y] == player:
                for flip_x, flip_y in to_flip:
                    self.board[flip_x, flip_y] = player
                return
            to_flip.append((x, y))
            x, y = x + dx, y + dy
    
    def evaluate(self):
        # 評価関数
        corner_weight = 4
        edge_weight = 2
        
        value = 0
        for i in range(8):
            for j in range(8):
                mult = 1
                if (i in [0, 7] and j in [0, 7]):
                    mult = corner_weight
                elif (i in [0, 7] or j in [0, 7]):
                    mult = edge_weight
                value += self.board[i, j] * mult
                
        return value

class OthelloAI:
    def __init__(self, player):
        self.player = player
    
    def get_move(self, state):
        return self.a_star_search(state)
    
    def a_star_search(self, initial_state, max_depth=4):
        start_node = SearchNode(0, 0, initial_state, [])
        frontier = []
        heappush(frontier, start_node)
        explored = set()
        
        while frontier:
            current_node = heappop(frontier)
            current_state = current_node.state
            g_score = current_node.g_score
            path = current_node.path
            
            if g_score >= max_depth:
                if path:
                    return path[0]
                return None
            
            state_hash = str(current_state.board.tobytes())
            if state_hash in explored:
                continue
                
            explored.add(state_hash)
            
            moves = current_state.get_valid_moves(self.player if g_score % 2 == 0 else -self.player)
            
            for move in moves:
                next_state = current_state.make_move(move[0], move[1], 
                                                   self.player if g_score % 2 == 0 else -self.player)
                if next_state is None:
                    continue
                    
                new_path = path + [move] if not path else path
                h_score = -next_state.evaluate() if self.player == -1 else next_state.evaluate()
                new_f_score = g_score + 1 + h_score
                
                heappush(frontier, SearchNode(new_f_score, g_score + 1, next_state, new_path))
        
        return None

def print_board(state):
    symbols = {0: ".", 1: "●", -1: "○"}
    for i in range(8):
        for j in range(8):
            print(symbols[state.board[i, j]], end=" ")
        print()

def play_game():
    state = OthelloState()
    ai = OthelloAI(player=1)
    
    while True:
        print_board(state)
        print("\n黒の番です（AI）")
        
        move = ai.get_move(state)
        if move is None:
            print("パスします")
        else:
            state = state.make_move(move[0], move[1], 1)
            print(f"AIは ({move[0]}, {move[1]}) に置きました")
        
        print("\n白の番です（プレイヤー）")
        valid_moves = state.get_valid_moves(-1)
        if not valid_moves:
            print("パスします")
            continue
            
        print("有効な手:", valid_moves)
        row = int(input("行を入力してください (0-7): "))
        col = int(input("列を入力してください (0-7): "))
        
        if (row, col) in valid_moves:
            state = state.make_move(row, col, -1)
        else:
            print("無効な手です")
            continue

if __name__ == "__main__":
    play_game()