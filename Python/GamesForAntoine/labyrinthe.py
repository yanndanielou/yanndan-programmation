import tkinter as tk
import random
from typing import List, Tuple, Dict

from logger import logger_config
import logging
import sys


EXIT_CASE_CONTENT = "E"
START_CASE_CONTENT = "S"
WALL_CASE_CONTENT = "#"
FREE_CASE_CONTENT = " "


class MazeGame:
    def __init__(self, root: tk.Tk, embedded_in_other_application: bool, size: int = 50) -> None:

        print(f"Initial recursion limit : {sys.getrecursionlimit()}")
        sys.setrecursionlimit(15000)
        print(f"New recursion limit : {sys.getrecursionlimit()}")

        self.embedded_in_other_application = embedded_in_other_application
        self.size = size
        self.root = root
        self.root.title("Maze Game")
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack()
        self.cell_size = 400 // self.size
        self.best_solution_path: List[Tuple[int, int]] = []

        self.maze, self.best_solution_path = self.generate_maze_with_solution()
        self.player_pos = (1, 1)

        # self.print()

        self.root.bind("<KeyPress>", self.key_press)
        self.draw_maze()

    def generate_maze_with_solution(self) -> Tuple[List[List[str]], List[Tuple[int, int]]]:
        with logger_config.stopwatch_with_label("generate_maze_with_solution"):
            # Keep generating until we obtain a valid path from start to exit
            attempts = 0
            while True:
                attempts += 1
                maze = [[WALL_CASE_CONTENT for _ in range(self.size)] for _ in range(self.size)]
                # carve out free cells
                self._generate_path(maze, [], 1, 1)
                maze[1][1] = START_CASE_CONTENT
                maze[self.size - 2][self.size - 2] = EXIT_CASE_CONTENT

                path = self._bfs_shortest_path(maze, (1, 1), (self.size - 2, self.size - 2))
                if path:
                    return maze, path

                if attempts >= 10:
                    logging.warning("Could not find a path after %d attempts", attempts)
                    return maze, []

    def _generate_path(self, maze: List[List[str]], solution_path: List[Tuple[int, int]], x: int, y: int) -> None:
        """Carve free cells using a randomized DFS-like approach. Mutates `maze` in place.
        The `solution_path` parameter is only used to record visitation order (not the final solution).
        """
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        # mark current cell as free if needed
        if maze[x][y] == WALL_CASE_CONTENT:
            maze[x][y] = FREE_CASE_CONTENT
        solution_path.append((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < self.size - 1 and 1 <= ny < self.size - 1 and maze[nx][ny] == WALL_CASE_CONTENT:
                # count how many free neighbors the candidate cell already has (to avoid creating loops)
                free_neighbors = 0
                for ddx, ddy in directions:
                    nnx, nny = nx + ddx, ny + ddy
                    if 1 <= nnx < self.size - 1 and 1 <= nny < self.size - 1 and maze[nnx][nny] == FREE_CASE_CONTENT:
                        free_neighbors += 1
                if free_neighbors < 2:
                    maze[nx][ny] = FREE_CASE_CONTENT
                    self._generate_path(maze, solution_path, nx, ny)

    def _bfs_shortest_path(self, maze: List[List[str]], start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return the shortest path from start to end (inclusive) using BFS, or an empty list if none exists."""
        from collections import deque

        q = deque([start])
        visited = {start}
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        while q:
            cur = q.popleft()
            if cur == end:
                # reconstruct path
                path: List[Tuple[int, int]] = []
                node = cur
                while node != start:
                    path.append(node)
                    node = parent[node]
                path.append(start)
                path.reverse()
                return path

            x, y = cur
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and maze[nx][ny] != WALL_CASE_CONTENT and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    q.append((nx, ny))

        return []

    def draw_maze(self, show_solution: bool = False) -> None:
        with logger_config.stopwatch_with_label("draw_maze"):

            self.canvas.delete("all")
            for i in range(self.size):
                for j in range(self.size):
                    x1 = j * self.cell_size
                    y1 = i * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size

                    fill = "black" if self.maze[i][j] == WALL_CASE_CONTENT else "white"

                    if (i, j) == self.player_pos:
                        fill = "blue"
                    elif self.maze[i][j] == EXIT_CASE_CONTENT:
                        fill = "green"
                    elif show_solution and (i, j) in self.best_solution_path:
                        fill = "yellow"

                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)

    def move_player(self, dx: int, dy: int) -> None:
        x, y = self.player_pos
        new_position = (x + dx, y + dy)
        if self.maze[new_position[0]][new_position[1]] != WALL_CASE_CONTENT:
            self.player_pos = new_position
            print(f"Moved player {dx} {dy} to {new_position}")

        else:
            print(f"Could not move player {dx} {dy} to {new_position}")

    def key_press(self, event: tk.Event) -> None:
        show_solution = False
        if event.keysym == "Up":
            self.move_player(-1, 0)
        elif event.keysym == "Down":
            self.move_player(1, 0)
        elif event.keysym == "Left":
            self.move_player(0, -1)
        elif event.keysym == "Right":
            self.move_player(0, 1)
        elif event.keysym == "s":
            show_solution = True

        self.draw_maze(show_solution)

        if self.maze[self.player_pos[0]][self.player_pos[1]] == EXIT_CASE_CONTENT:
            print("You've reached the end!")
            if self.embedded_in_other_application:
                self.canvas.quit()
            else:
                self.root.quit()

    def print(self) -> None:
        for x in range(1, self.size):
            for y in range(1, self.size):
                print(f"x:{x}, y:{y} = {self.maze[x ][ y]}")


if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root, False)
    root.mainloop()
