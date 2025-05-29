import pygame
import random
import os

pygame.init()

width, height = 300, 600
block_size = 30
cols, rows = width // block_size, height // block_size
highscore_file = "highscore.txt"
font = pygame.font.SysFont("Arial", 24)

colors = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}

shapes = {
    'I': [[(0, 1), (1, 1), (2, 1), (3, 1)],
          [(2, 0), (2, 1), (2, 2), (2, 3)]],

    'O': [[(1, 0), (2, 0), (1, 1), (2, 1)]],

    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 1)],
          [(1, 2), (0, 1), (1, 1), (2, 1)],
          [(0, 1), (1, 0), (1, 1), (1, 2)]],

    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)],
          [(1, 0), (1, 1), (2, 1), (2, 2)]],

    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
          [(2, 0), (2, 1), (1, 1), (1, 2)]],

    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (2, 0), (1, 1), (1, 2)],
          [(0, 1), (1, 1), (2, 1), (2, 2)],
          [(1, 0), (1, 1), (0, 2), (1, 2)]],

    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)],
          [(1, 0), (1, 1), (1, 2), (2, 2)],
          [(0, 1), (1, 1), (2, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]]
}


def create_grid(locked):
    return [[locked.get((x, y), (0, 0, 0)) for x in range(cols)] for y in range(rows)]

class Piece:
    def __init__(self, x, y, shape):
        self.x, self.y = x, y
        self.shape = shape
        self.color = colors[shape]
        self.rotation = 0

    def image(self):
        return shapes[self.shape][self.rotation % len(shapes[self.shape])]

    def cells(self):
        return [(self.x + dx, self.y + dy) for dx, dy in self.image()]


def valid_space(piece, grid):
    for x, y in piece.cells():
        if x < 0 or x >= cols or y >= rows or (y >= 0 and grid[y][x] != (0, 0, 0)):
            return False
    return True

def check_lines(grid, locked):
    cleared = 0
    for y in range(rows - 1, -1, -1):
        if (0, 0, 0) not in grid[y]:
            cleared += 1
            for x in range(cols):
                locked.pop((x, y), None)
            for k in sorted(locked, key=lambda k: k[1])[::-1]:
                x, yy = k
                if yy < y:
                    locked[(x, yy + 1)] = locked.pop((x, yy))
    return cleared

def draw_grid(surface, grid):
    for y in range(rows):
        for x in range(cols):
            pygame.draw.rect(surface, grid[y][x], (x * block_size, y * block_size, block_size, block_size))
    for y in range(rows):
        pygame.draw.line(surface, (50, 50, 50), (0, y * block_size), (width, y * block_size))
    for x in range(cols):
        pygame.draw.line(surface, (50, 50, 50), (x * block_size, 0), (x * block_size, height))

def draw_ui(surface, score, high_score):
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 0))
    surface.blit(score_text, (10, 10))
    surface.blit(high_score_text, (10, 40))

def draw_window(surface, grid, score, high_score):
    surface.fill((0, 0, 0))
    draw_grid(surface, grid)
    draw_ui(surface, score, high_score)

def get_new_piece():
    return Piece(3, 0, random.choice(list(shapes.keys())))

def hard_drop(piece, grid):
    while valid_space(piece, grid):
        piece.y += 1
    piece.y -= 1

def load_high_score():
    if os.path.exists(highscore_file):
        with open(highscore_file, 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0


def save_high_score(score):
    with open(highscore_file, 'w') as f:
        f.write(str(score))


def main():
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    locked_positions = {}
    current_piece = get_new_piece()
    next_piece = get_new_piece()
    fall_time, fall_speed = 99999, 0.5
    change_piece = False
    score = 0
    high_score = load_high_score()
    run = True

    try:
        while run:
            grid = create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            clock.tick()

            if fall_time / 1000 >= fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                    change_piece = True

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    run = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                    elif e.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                    elif e.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                    elif e.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not valid_space(current_piece, grid):
                            current_piece.rotation -= 1
                    elif e.key == pygame.K_SPACE:
                        hard_drop(current_piece, grid)
                        change_piece = True

            for x, y in current_piece.cells():
                if y >= 0:
                    grid[y][x] = current_piece.color

            if change_piece:
                for pos in current_piece.cells():
                    if pos[1] >= 0:
                        locked_positions[pos] = current_piece.color
                current_piece = next_piece
                next_piece = get_new_piece()
                change_piece = False
                lines = check_lines(grid, locked_positions)
                score += lines * 100
                if score > high_score:
                    high_score = score

            draw_window(screen, grid, score, high_score)
            pygame.display.update()

            if any(y < 1 for (i, y) in locked_positions):
                if score > load_high_score():
                    save_high_score(score)
                run = False

    except Exception as e:
        print(f"Error: {e}")

    pygame.quit()


if __name__ == "__main__":
    main()