import tkinter as tk
from tkinter import ttk, messagebox
import time
import copy
import random
from typing import List, Tuple, Optional
import numpy as np
from collections import defaultdict

# 各アルゴリズムのクラスをインポート
from minimax1 import OthelloBoard as Board1, OthelloAI as AI1
from minimax2 import OthelloGame as Board2, MinimaxAI as AI2
from minimax3 import Othello as Board3
from A_star import OthelloState as Board4, OthelloAI as AI4
from monte_carlo import Othello as Board5

class TimeoutException(Exception):
    pass

# AIアダプタークラス
class AI1Adapter:
    def __init__(self, time_limit):
        self.ai = AI1(max_depth=4, max_time=float(time_limit))
        
    def get_move(self, board, player):
        board_copy = Board1()
        board_copy.board = copy.deepcopy(board)
        return self.ai.get_move(board_copy, player)

class AI2Adapter:
    def __init__(self, time_limit):
        self.ai = AI2(3)  # depth=3
        
    def get_move(self, board, player):
        game = Board2()
        game.board = np.array(board)
        game.current_player = player
        moves = game.get_valid_moves()
        if not moves:
            return None
        try:
            move = self.ai.choose_move(moves, game)
            print(f"AI2 selected move: {move}")
            return move
        except Exception as e:
            print(f"AI2 error: {e}")
            if moves:
                print("Falling back to first available move")
                return moves[0]
            return None

class AI3Adapter:
    def __init__(self, time_limit):
        self.game = Board3()
        self.time_limit = float(time_limit)
        
    def get_move(self, board, player):
        self.game.board = copy.deepcopy(board)
        self.game.current_player = player
        _, move = self.game.negamax(4, float('-inf'), float('inf'), player)
        return move

class AI4Adapter:
    def __init__(self, time_limit):
        self.time_limit = float(time_limit)
        
    def get_move(self, board, player):
        try:
            # ボードをnumpy配列に変換
            numpy_board = np.array(board)
            # プレイヤーの値を1/-1に変換（A*の期待する形式）
            numpy_board = np.where(numpy_board == 2, -1, numpy_board)
            
            # A*アルゴリズムのインスタンスを作成
            ai = AI4(player=1 if player == 1 else -1)
            state = Board4(numpy_board)
            
            # 有効な手があるか確認
            valid_moves = state.get_valid_moves(1 if player == 1 else -1)
            if not valid_moves:
                print("A* reports no valid moves")
                return None
                
            # 手を取得
            move = ai.get_move(state)
            print(f"A* suggested move: {move}")
            
            if move and len(move) == 2:
                return move
            else:
                print("A* returned invalid move format")
                return valid_moves[0] if valid_moves else None
                
        except Exception as e:
            print(f"Error in A* adapter: {e}")
            import traceback
            traceback.print_exc()
            return None

class AI5Adapter:
    def __init__(self, time_limit):
        self.game = Board5()
        
    def get_move(self, board, player):
        self.game.board = copy.deepcopy(board)
        legal_moves = self.game.get_legal_moves(player)
        if not legal_moves:
            return None
        x, y = random.choice(legal_moves)
        return (x, y)

class TournamentSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("オセロトーナメントシステム")
        self.setup_gui()
        self.match_results = []
        self.current_match = 0
        self.total_matches = 0
        
    def setup_gui(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # アルゴリズム選択部分
        ttk.Label(main_frame, text="アルゴリズム1:").grid(row=0, column=0, sticky=tk.W)
        self.algo1 = ttk.Combobox(main_frame, values=[
            "Minimax1",
            "Minimax2",
            "Minimax3",
            "A*探索",
            "モンテカルロ"
        ])
        self.algo1.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.algo1.set("Minimax1")
        
        ttk.Label(main_frame, text="アルゴリズム2:").grid(row=1, column=0, sticky=tk.W)
        self.algo2 = ttk.Combobox(main_frame, values=[
            "Minimax1",
            "Minimax2",
            "Minimax3",
            "A*探索",
            "モンテカルロ"
        ])
        self.algo2.grid(row=1, column=1, sticky=(tk.W, tk.E))
        self.algo2.set("Minimax2")
        
        # 思考時間制限設定
        ttk.Label(main_frame, text="思考時間制限 (秒):").grid(row=2, column=0, sticky=tk.W)
        self.time_limit = ttk.Entry(main_frame)
        self.time_limit.insert(0, "5")
        self.time_limit.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        # 対戦回数設定
        ttk.Label(main_frame, text="対戦回数:").grid(row=3, column=0, sticky=tk.W)
        self.match_count = ttk.Entry(main_frame)
        self.match_count.insert(0, "10")
        self.match_count.grid(row=3, column=1, sticky=(tk.W, tk.E))
        
        # 開始ボタン
        ttk.Button(main_frame, text="トーナメント開始", command=self.start_tournament).grid(row=4, column=0, columnspan=2)
        
        # 盤面表示用キャンバス
        self.canvas = tk.Canvas(main_frame, width=400, height=400, bg='green')
        self.canvas.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 情報表示用ラベル
        self.info_label = ttk.Label(main_frame, text="")
        self.info_label.grid(row=6, column=0, columnspan=2)
        
        # 統計情報表示用
        self.stats_label = ttk.Label(main_frame, text="")
        self.stats_label.grid(row=7, column=0, columnspan=2)

    def create_ai(self, algo_name: str) -> object:
        time_limit = self.time_limit.get()
        if algo_name == "Minimax1":
            return AI1Adapter(time_limit)
        elif algo_name == "Minimax2":
            return AI2Adapter(time_limit)
        elif algo_name == "Minimax3":
            return AI3Adapter(time_limit)
        elif algo_name == "A*探索":
            return AI4Adapter(time_limit)
        else:  # Monte Carlo
            return AI5Adapter(time_limit)

    def draw_board(self, board: list):
        self.canvas.delete("all")
        cell_size = 50
        
        # 盤面の罫線を描画
        for i in range(9):
            self.canvas.create_line(i * cell_size, 0, i * cell_size, 400, fill='black')
            self.canvas.create_line(0, i * cell_size, 400, i * cell_size, fill='black')
            
        # 石を描画
        for i in range(8):
            for j in range(8):
                x = j * cell_size + cell_size // 2
                y = i * cell_size + cell_size // 2
                if board[i][j] == 1:  # 黒
                    self.canvas.create_oval(x-20, y-20, x+20, y+20, fill='black')
                elif board[i][j] == 2:  # 白
                    self.canvas.create_oval(x-20, y-20, x+20, y+20, fill='white')

    def play_single_game(self, black_ai: object, white_ai: object) -> dict:
        board = [[0] * 8 for _ in range(8)]
        # 初期配置
        board[3][3] = board[4][4] = 2  # 白
        board[3][4] = board[4][3] = 1  # 黒
        
        moves_history = []
        times_history = []
        
        def is_valid_move(row: int, col: int, player: int) -> bool:
            if board[row][col] != 0:
                return False
            
            directions = [(0,1), (1,0), (0,-1), (-1,0), 
                         (1,1), (-1,-1), (1,-1), (-1,1)]
            
            opponent = 3 - player
            for dx, dy in directions:
                x, y = row + dx, col + dy
                has_opponent = False
                
                while 0 <= x < 8 and 0 <= y < 8 and board[x][y] == opponent:
                    has_opponent = True
                    x, y = x + dx, y + dy
                    
                if has_opponent and 0 <= x < 8 and 0 <= y < 8 and board[x][y] == player:
                    return True
            return False
        
        def make_move(row: int, col: int, player: int) -> None:
            if not is_valid_move(row, col, player):
                return
                
            board[row][col] = player
            directions = [(0,1), (1,0), (0,-1), (-1,0), 
                         (1,1), (-1,-1), (1,-1), (-1,1)]
            
            opponent = 3 - player
            for dx, dy in directions:
                x, y = row + dx, col + dy
                to_flip = []
                
                while 0 <= x < 8 and 0 <= y < 8 and board[x][y] == opponent:
                    to_flip.append((x, y))
                    x, y = x + dx, y + dy
                    
                if 0 <= x < 8 and 0 <= y < 8 and board[x][y] == player:
                    for flip_x, flip_y in to_flip:
                        board[flip_x][flip_y] = player
        
        def has_valid_moves(player: int) -> bool:
            for i in range(8):
                for j in range(8):
                    if is_valid_move(i, j, player):
                        return True
            return False
        
        consecutive_passes = 0
        while True:
            current_ai = black_ai if len(moves_history) % 2 == 0 else white_ai
            player = 1 if len(moves_history) % 2 == 0 else 2
            
            if not has_valid_moves(player):
                print(f"Player {player} has no valid moves (pass)")
                consecutive_passes += 1
                if consecutive_passes >= 2:
                    print("Game over - two consecutive passes")
                    break
                if not has_valid_moves(3 - player):
                    print("Game over - no valid moves for both players")
                    break
                continue
            consecutive_passes = 0  # リセット
            
            start_time = time.time()
            try:
                print(f"Player {player} thinking...")
                move = current_ai.get_move(board, player)
                end_time = time.time()
                print(f"Move received: {move}")
                
                if move is None:
                    print(f"Player {player} has no valid moves")
                    continue
                
                # 手の検証
                if not is_valid_move(move[0], move[1], player):
                    print(f"Invalid move suggested by AI: {move}")
                    continue
                
                # 手を適用
                print(f"Applying move {move} for player {player}")
                make_move(move[0], move[1], player)
                moves_history.append(move)
                times_history.append(end_time - start_time)
                
                # 盤面の状態を出力
                black_count = sum(row.count(1) for row in board)
                white_count = sum(row.count(2) for row in board)
                print(f"Current score - Black: {black_count}, White: {white_count}")
                
                # GUI更新
                self.draw_board(board)
                self.root.update()
                time.sleep(0.1)  # 動きを見やすくするため
                
            except Exception as e:
                print(f"Error occurred: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # ゲーム終了時の最終スコア計算
        black_score = sum(row.count(1) for row in board)
        white_score = sum(row.count(2) for row in board)
        print(f"Game finished - Final score - Black: {black_score}, White: {white_score}")
        
        # 結果を辞書にまとめて返す
        result = {
            'black_score': black_score,
            'white_score': white_score,
            'moves': moves_history,
            'times': times_history
        }
        
        # GUI更新を最後に一度行う
        self.draw_board(board)
        self.root.update()
        
        return result

    def start_tournament(self):
        algo1_name = self.algo1.get()
        algo2_name = self.algo2.get()
        match_count = int(self.match_count.get())
        self.total_matches = match_count
        
        results = defaultdict(int)
        total_times = defaultdict(list)
        
        for i in range(match_count):
            # 1回おきに先手後手を入れ替え
            if i % 2 == 0:
                black_ai = self.create_ai(algo1_name)
                white_ai = self.create_ai(algo2_name)
            else:
                black_ai = self.create_ai(algo2_name)
                white_ai = self.create_ai(algo1_name)
                
            self.current_match = i + 1
            self.info_label.config(text=f"対戦 {i+1}/{match_count} 実行中...")
            
            try:
                result = self.play_single_game(black_ai, white_ai)
                
                # 結果を記録
                if result['black_score'] > result['white_score']:
                    winner = algo1_name if i % 2 == 0 else algo2_name
                elif result['white_score'] > result['black_score']:
                    winner = algo2_name if i % 2 == 0 else algo1_name
                else:
                    winner = 'draw'
                    
                results[winner] += 1
                total_times[algo1_name].extend(result['times'][::2])
                total_times[algo2_name].extend(result['times'][1::2])
                
                # 統計情報を更新
                self.update_stats(results, total_times)
                
            except Exception as e:
                print(f"Match error: {e}")
                continue
            
        messagebox.showinfo("完了", "トーナメントが終了しました")

    def update_stats(self, results: dict, times: dict):
        stats_text = f"結果統計:\n"
        total_games = sum(results.values())
        
        if total_games > 0:
            for algo in [self.algo1.get(), self.algo2.get()]:
                win_rate = (results[algo] / total_games) * 100 if algo in results else 0
                avg_time = sum(times[algo]) / len(times[algo]) if times[algo] else 0
                stats_text += f"{algo}: 勝率 {win_rate:.1f}%, 平均思考時間 {avg_time:.3f}秒\n"
                
            if 'draw' in results and results['draw'] > 0:
                draw_rate = (results['draw'] / total_games) * 100
                stats_text += f"引き分け: {draw_rate:.1f}%\n"
            
        self.stats_label.config(text=stats_text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    tournament = TournamentSystem()
    tournament.run()