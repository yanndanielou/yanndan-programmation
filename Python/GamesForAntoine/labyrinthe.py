import tkinter as tk
import random


class MazeGame:
    def __init__(self, root, size=10):
        self.size = size
        self.root = root
        self.root.title("Maze Game")
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack()
        self.cell_size = 400 // self.size
        self.solution_path = []

        self.maze, self.solution_path = self.generate_maze_with_solution()
        self.player_pos = (1, 1)

        self.root.bind("<KeyPress>", self.key_press)
        self.draw_maze()

    def generate_maze_with_solution(self):
        maze = [["#" for _ in range(self.size)] for _ in range(self.size)]
        solution_path = []
        self._generate_path(maze, solution_path, 1, 1)
        maze[1][1] = "S"
        maze[self.size - 2][self.size - 2] = "E"
        return maze, solution_path

    def _generate_path(self, maze, solution_path, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        solution_path.append((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < self.size - 1 and 1 <= ny < self.size - 1 and maze[nx][ny] == "#":
                if sum(1 for dx, dy in directions if maze[nx + dx][ny + dy] == " ") < 2:
                    maze[nx][ny] = " "
                    self._generate_path(maze, solution_path, nx, ny)
                    if maze[self.size - 2][self.size - 2] == "E":
                        break
        return maze

    def draw_maze(self, show_solution=False):
        self.canvas.delete("all")
        for i in range(self.size):
            for j in range(self.size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                fill = "black" if self.maze[i][j] == "#" else "white"

                if (i, j) == self.player_pos:
                    fill = "blue"
                elif self.maze[i][j] == "E":
                    fill = "green"
                elif show_solution and (i, j) in self.solution_path:
                    fill = "yellow"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)

    def move_player(self, dx, dy):
        x, y = self.player_pos
        new_position = (x + dx, y + dy)
        if self.maze[new_position[0]][new_position[1]] != "#":
            self.player_pos = new_position

    def key_press(self, event):
        if event.keysym == "Up":
            self.move_player(-1, 0)
        elif event.keysym == "Down":
            self.move_player(1, 0)
        elif event.keysym == "Left":
            self.move_player(0, -1)
        elif event.keysym == "Right":
            self.move_player(0, 1)
        elif event.keysym == "s":
            self.draw_maze(show_solution=True)

        self.draw_maze()

        if self.maze[self.player_pos[0]][self.player_pos[1]] == "E":
            print("You've reached the end!")
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()
