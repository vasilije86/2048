from tkinter import *
import random
import copy


class Play_2048(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("2048")
        self.geometry("430x600")
        self.game_board = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.high_score = 0
        self.max_depth = 3  # Depth for backtracking

        # UI Setup
        self.game_score = StringVar(self, "Score: 0")
        self.highest_score = StringVar(self, f"High Score: {self.high_score}")
        self.suggestion = StringVar(self, "Suggested Move: None")
        self.setup_ui()

        # Bind keys for moves
        self.bind_all("<Key>", self.moves)
        self.new_game()

    def setup_ui(self):
        Label(self, textvariable=self.game_score, font=("Arial", 18)).pack()
        Label(self, textvariable=self.highest_score, font=("Arial", 18)).pack()
        Label(self, textvariable=self.suggestion, font=("Arial", 16), fg="blue").pack(pady=5)
        self.canvas = Canvas(self, width=410, height=410, bg="#bbada0")
        self.canvas.pack(pady=10)
        Button(self, text="Hint", command=self.suggest_best_move, font=("Arial", 14)).pack(pady=10)

    def new_game(self):
        self.score = 0
        self.game_score.set("Score: 0")
        self.suggestion.set("Suggested Move: None")
        self.game_board = [[0] * 4 for _ in range(4)]
        self.add_random_tile()
        self.add_random_tile()
        self.update_ui()

    def add_random_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.game_board[i][j] == 0]
        if empty_cells:
            x, y = random.choice(empty_cells)
            self.game_board[x][y] = 2 if random.random() < 0.9 else 4

    def update_ui(self):
        self.canvas.delete("all")
        for i in range(4):
            for j in range(4):
                value = self.game_board[i][j]
                self.draw_tile(i, j, value)
        self.game_score.set(f"Score: {self.score}")
        if self.score > self.high_score:
            self.high_score = self.score
            self.highest_score.set(f"High Score: {self.high_score}")

    def draw_tile(self, row, col, value):
        colors = {
            0: ("#cdc1b4", ""),
            2: ("#eee4da", "#776e65"),
            4: ("#ede0c8", "#776e65"),
            8: ("#f2b179", "#f9f6f2"),
            16: ("#f59563", "#f9f6f2"),
            32: ("#f67c5f", "#f9f6f2"),
            64: ("#f65e3b", "#f9f6f2"),
            128: ("#edcf72", "#f9f6f2"),
            256: ("#edcc61", "#f9f6f2"),
            512: ("#edc850", "#f9f6f2"),
            1024: ("#edc53f", "#f9f6f2"),
            2048: ("#edc22e", "#f9f6f2"),
        }
        bg, fg = colors.get(value, ("#3c3a32", "#f9f6f2"))
        x1, y1 = col * 100 + 5, row * 100 + 5
        x2, y2 = x1 + 90, y1 + 90
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="")
        if value:
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(value), fill=fg, font=("Helvetica", 24, "bold"))

    def moves(self, event):
        key_to_direction = {"Up": "up", "Down": "down", "Left": "left", "Right": "right"}
        direction = key_to_direction.get(event.keysym)
        if direction:
            if self.make_move(direction):
                self.add_random_tile()
                self.update_ui()
                if self.is_game_over(self.game_board):
                    print("Game Over!")
                    self.new_game()

    def make_move(self, direction):
        if direction in ["up", "down"]:
            self.game_board = self.transpose(self.game_board)
        if direction in ["down", "right"]:
            self.game_board = self.reverse(self.game_board)

        moved = self.merge_tiles()

        if direction in ["down", "right"]:
            self.game_board = self.reverse(self.game_board)
        if direction in ["up", "down"]:
            self.game_board = self.transpose(self.game_board)

        return moved

    def merge_tiles(self):
        moved = False
        for row in self.game_board:
            compressed_row = [num for num in row if num != 0]
            for i in range(len(compressed_row) - 1):
                if compressed_row[i] == compressed_row[i + 1]:
                    compressed_row[i] *= 2
                    self.score += compressed_row[i]
                    compressed_row[i + 1] = 0
                    moved = True
            compressed_row = [num for num in compressed_row if num != 0]
            compressed_row += [0] * (4 - len(compressed_row))
            if compressed_row != row:
                moved = True
            row[:] = compressed_row
        return moved

    def suggest_best_move(self):
        best_score, best_move = self.best_move_with_backtracking(self.game_board, self.max_depth)
        self.suggestion.set(f"Suggested Move: {best_move.capitalize() if best_move else 'None'}")
        print(f"Suggested Move: {best_move}")

    def best_move_with_backtracking(self, board, depth):
        if depth == 0 or self.is_game_over(board):
            return self.heuristic_score(board), None

        best_score = -float("inf")
        best_move = None
        for move in ['up', 'down', 'left', 'right']:
            new_board = self.simulate_move(copy.deepcopy(board), move)
            if new_board != board:
                score, _ = self.best_move_with_backtracking(new_board, depth - 1)
                if score > best_score:
                    best_score = score
                    best_move = move
        return best_score, best_move

    def heuristic_score(self, board):
        score = sum(sum(row) for row in board)
        empty_tiles = sum(row.count(0) for row in board)
        return score + empty_tiles * 10

    def simulate_move(self, board, direction):
        if direction in ["up", "down"]:
            board = self.transpose(board)
        if direction in ["down", "right"]:
            board = self.reverse(board)

        self.merge_tiles_simulation(board)

        if direction in ["down", "right"]:
            board = self.reverse(board)
        if direction in ["up", "down"]:
            board = self.transpose(board)

        return board

    def merge_tiles_simulation(self, board):
        for row in board:
            compressed_row = [num for num in row if num != 0]
            for i in range(len(compressed_row) - 1):
                if compressed_row[i] == compressed_row[i + 1]:
                    compressed_row[i] *= 2
                    compressed_row[i + 1] = 0
            compressed_row = [num for num in compressed_row if num != 0]
            compressed_row += [0] * (4 - len(compressed_row))
            row[:] = compressed_row

    @staticmethod
    def transpose(matrix):
        return [list(row) for row in zip(*matrix)]

    @staticmethod
    def reverse(matrix):
        return [row[::-1] for row in matrix]

    def is_game_over(self, board):
        for i in range(4):
            for j in range(4):
                if board[i][j] == 0:
                    return False
                if j < 3 and board[i][j] == board[i][j + 1]:
                    return False
                if i < 3 and board[i][j] == board[i + 1][j]:
                    return False
        return True


if __name__ == "__main__":
    app = Play_2048()
    app.mainloop()
