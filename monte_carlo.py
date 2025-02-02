import tkinter as tk
from tkinter import messagebox
import copy
import random

class Othello:
    def __init__(self):
        self.board = [[0] * 8 for _ in range(8)]  # 8x8のボードを0で初期化
        self.board[3][3] = self.board[4][4] = 1  # プレイヤー1 (白)
        self.board[3][4] = self.board[4][3] = 2  # プレイヤー2 (黒)

    def is_on_board(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def get_legal_moves(self, player):
        opponent = 3 - player
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        legal_moves = []

        for x in range(8):
            for y in range(8):
                if self.board[x][y] != 0:  # 空いていないセルはスキップ
                    continue

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    has_opponent_between = False

                    while self.is_on_board(nx, ny) and self.board[nx][ny] == opponent:
                        has_opponent_between = True
                        nx += dx
                        ny += dy

                    if has_opponent_between and self.is_on_board(nx, ny) and self.board[nx][ny] == player:
                        legal_moves.append((x, y))
                        break

        return legal_moves

    def make_move(self, move, player):
        x, y = move
        self.board[x][y] = player
        opponent = 3 - player
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            stones_to_flip = []

            while self.is_on_board(nx, ny) and self.board[nx][ny] == opponent:
                stones_to_flip.append((nx, ny))
                nx += dx
                ny += dy

            if self.is_on_board(nx, ny) and self.board[nx][ny] == player:
                for flip_x, flip_y in stones_to_flip:
                    self.board[flip_x][flip_y] = player

    def is_game_over(self):
        return not (self.get_legal_moves(1) or self.get_legal_moves(2))

    def get_winner(self):
        player1_score = sum(row.count(1) for row in self.board)
        player2_score = sum(row.count(2) for row in self.board)
        if player1_score > player2_score:
            return 1
        elif player2_score > player1_score:
            return 2
        else:
            return 0  # 引き分け

class OthelloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("オセロ")
        self.game = Othello()
        self.current_player = 1  # プレイヤー1が最初
        self.buttons = [[None for _ in range(8)] for _ in range(8)]

        self.create_board()
        self.update_board()

    def create_board(self):
        for x in range(8):
            for y in range(8):
                btn = tk.Button(self.root, width=4, height=2, command=lambda x=x, y=y: self.handle_click(x, y))
                btn.grid(row=x, column=y)
                self.buttons[x][y] = btn

    def update_board(self):
        for x in range(8):
            for y in range(8):
                if self.game.board[x][y] == 1:
                    self.buttons[x][y].config(text="●", state="disabled")
                elif self.game.board[x][y] == 2:
                    self.buttons[x][y].config(text="○", state="disabled")
                else:
                    self.buttons[x][y].config(text="", state="normal")

        # 勝敗判定
        if self.game.is_game_over():
            winner = self.game.get_winner()
            if winner == 1:
                messagebox.showinfo("ゲーム終了", "プレイヤー1（●）の勝ち！")
            elif winner == 2:
                messagebox.showinfo("ゲーム終了", "プレイヤー2（○）の勝ち！")
            else:
                messagebox.showinfo("ゲーム終了", "引き分け！")
            self.root.destroy()

        # パス判定
        legal_moves = self.game.get_legal_moves(self.current_player)
        if not legal_moves:  # 現在のプレイヤーが置ける場所がない場合
            messagebox.showinfo("パス", f"プレイヤー{self.current_player}は置ける場所がないためパスします。")
            self.current_player = 3 - self.current_player  # 次のプレイヤーに交代

            # 次のプレイヤーも置ける場所がない場合はゲーム終了
            if not self.game.get_legal_moves(self.current_player):
                self.update_board()
            else:
                # 次のプレイヤーが合法手を持つ場合に自動で更新
                self.update_board()

    def handle_click(self, x, y):
        # プレイヤーの手を処理
        if (x, y) in self.game.get_legal_moves(self.current_player):
            self.game.make_move((x, y), self.current_player)
            self.current_player = 3 - self.current_player  # プレイヤー交代
            self.update_board()

            # AIのターン
            self.root.after(500, self.ai_move)

    def ai_move(self):
        # AIの合法手を取得
        legal_moves = self.game.get_legal_moves(self.current_player)
        if legal_moves:
            move = random.choice(legal_moves)
            self.game.make_move(move, self.current_player)
            self.current_player = 3 - self.current_player  # プレイヤー交代
            self.update_board()
        else:
            # AIも置ける場所がない場合
            messagebox.showinfo("パス", f"AI（プレイヤー{self.current_player}）は置ける場所がないためパスします。")
            self.current_player = 3 - self.current_player
            self.update_board()


if __name__ == "__main__":
    root = tk.Tk()
    gui = OthelloGUI(root)
    root.mainloop()