# I acknowledge the use of OpenAI ChatGPT (GPT-5.1 Thinking, OpenAI, https://chatgpt.com/)
# to develop the code in this file for CSC-44102 Assessment 2.



import random
import tkinter as tk
from typing import List, Tuple

TILE = 20
GRID_W, GRID_H = 24, 24  # 24x24 grid -> 480x480 window
W, H = GRID_W * TILE, GRID_H * TILE
TICK_MS_START = 140
TICK_MS_MIN = 70
SPEEDUP_EVERY = 4  # apples per speedup

DIRS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
}

class SnakeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Snake Game - CSC-44102 Assessment 2")
        self.c = tk.Canvas(root, width=W, height=H, bg="#111", highlightthickness=0)
        self.c.pack()

        self.running = True
        self.dead = False
        self.score = 0
        self.tick_ms = TICK_MS_START
        self.dir = "Right"
        self.pending_dir = "Right"
        self.snake: List[Tuple[int, int]] = []
        self.apple: Tuple[int, int] = (0, 0)

        root.bind("<KeyPress>", self.on_key)
        self.restart()
        self.loop()

    def restart(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.snake = [(cx - 1, cy), (cx, cy)]  # 2 segments to start
        self.dir = "Right"
        self.pending_dir = "Right"
        self.score = 0
        self.tick_ms = TICK_MS_START
        self.dead = False
        self.running = True
        self.spawn_apple()

    def on_key(self, e):
        k = e.keysym
        if k in DIRS:
            # prevent instant 180-degree turns
            if not self.dead:
                if (self.dir, k) not in {("Up","Down"),("Down","Up"),("Left","Right"),("Right","Left")}:
                    self.pending_dir = k
        elif k == "space":
            if self.dead:
                self.restart()
            else:
                self.running = not self.running

    def loop(self):
        if self.running and not self.dead:
            self.update()
        self.draw()
        self.root.after(self.tick_ms if self.running else 100, self.loop)

    def update(self):
        self.dir = self.pending_dir
        dx, dy = DIRS[self.dir]
        head_x, head_y = self.snake[-1]
        nx, ny = head_x + dx, head_y + dy

        # wall collision
        if nx < 0 or nx >= GRID_W or ny < 0 or ny >= GRID_H:
            self.dead = True
            self.running = False
            return

        # self collision (check new head vs body excluding tail if we grow later)
        if (nx, ny) in self.snake:
            self.dead = True
            self.running = False
            return

        # move
        self.snake.append((nx, ny))

        # apple?
        if (nx, ny) == self.apple:
            self.score += 1
            self.spawn_apple()
            # speed up every few apples
            if self.score % SPEEDUP_EVERY == 0:
                self.tick_ms = max(TICK_MS_MIN, self.tick_ms - 10)
        else:
            # remove tail (no growth)
            self.snake.pop(0)

    def spawn_apple(self):
        free = [(x, y) for x in range(GRID_W) for y in range(GRID_H) if (x, y) not in self.snake]
        self.apple = random.choice(free) if free else (-1, -1)

    def draw(self):
        self.c.delete("all")
        # grid (optional light)
        for x in range(0, W, TILE): self.c.create_line(x, 0, x, H, fill="#222")
        for y in range(0, H, TILE): self.c.create_line(0, y, W, y, fill="#222")

        # apple
        ax, ay = self.apple
        if ax >= 0:
            self.rect(ax, ay, fill="#ef4565")

        # snake
        for i, (sx, sy) in enumerate(self.snake):
            fill = "#3da9fc" if i < len(self.snake) - 1 else "#7f5af0"  # head highlighted
            self.rect(sx, sy, fill=fill)

        # HUD
        self.c.create_text(6, 6, anchor="nw", fill="#fff", font=("Helvetica", 12, "bold"),
                           text=f"Score: {self.score}  Speed: {round(1000/self.tick_ms,1)} tps")

        if not self.running or self.dead:
            self.c.create_rectangle(0, 0, W, H, fill="#000", stipple="gray50", outline="")
            msg = "Paused\nPress Space to resume" if not self.dead else f"Game Over\nScore: {self.score}\n\nPress Space to restart"
            self.c.create_text(W/2, H/2, fill="#fff", font=("Helvetica", 20, "bold"),
                               text=msg, justify="center")

    def rect(self, gx: int, gy: int, fill: str):
        x1, y1 = gx * TILE, gy * TILE
        x2, y2 = x1 + TILE, y1 + TILE
        self.c.create_rectangle(x1+1, y1+1, x2-1, y2-1, fill=fill, outline="")

def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()    
