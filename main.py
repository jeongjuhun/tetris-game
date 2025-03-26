import pygame
import random
import math

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GHOST = (150, 150, 150)
BOMB_COLOR = (255, 50, 50)
COLORS = [(0, 255, 255), (255, 165, 0), (0, 255, 0),
          (255, 0, 0), (0, 0, 255), (255, 255, 0), (128, 0, 128)]

# 블럭 모양
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1], [1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 0], [1, 1, 1]]
]

CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
WIDTH = COLUMNS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
PREVIEW_WIDTH = 6 * CELL_SIZE
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH + PREVIEW_WIDTH * 2, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)
particles = []

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.color = color
        self.life = 30

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.2
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.is_bomb = random.random() < 0.1
        if self.is_bomb:
            self.color = BOMB_COLOR

    def rotate(self):
        rotated = list(zip(*self.shape[::-1]))
        self.shape = [list(row) for row in rotated]

def draw_border():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, HEIGHT), 4)

def draw_board(board):
    for y in range(ROWS):
        for x in range(COLUMNS):
            color = board[y][x]
            if color:
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def draw_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                px = (piece.x + x) * CELL_SIZE
                py = (piece.y + y) * CELL_SIZE
                pygame.draw.rect(screen, piece.color, (px, py, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (px, py, CELL_SIZE, CELL_SIZE), 1)

def draw_ghost_piece(board, piece):
    ghost = Tetromino()
    ghost.shape = piece.shape
    ghost.color = GHOST
    ghost.x = piece.x
    ghost.y = piece.y
    ghost.is_bomb = False
    while valid_position(board, ghost, dy=1):
        ghost.y += 1
    draw_piece(ghost)

def draw_next_piece(piece):
    label = font.render("Next", True, WHITE)
    screen.blit(label, (WIDTH + 10, 10))
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                px = WIDTH + 10 + x * CELL_SIZE
                py = 40 + y * CELL_SIZE
                pygame.draw.rect(screen, piece.color, (px, py, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (px, py, CELL_SIZE, CELL_SIZE), 1)

def draw_hold_piece(piece):
    label = font.render("Hold", True, WHITE)
    screen.blit(label, (WIDTH + PREVIEW_WIDTH + 10, 10))
    if not piece:
        return
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                px = WIDTH + PREVIEW_WIDTH + 10 + x * CELL_SIZE
                py = 40 + y * CELL_SIZE
                pygame.draw.rect(screen, piece.color, (px, py, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, GRAY, (px, py, CELL_SIZE, CELL_SIZE), 1)

def draw_score(score, level):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 40))

def draw_game_over():
    text = big_font.render("GAME OVER", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    subtext = font.render("Press R to Restart", True, WHITE)
    screen.blit(subtext, (WIDTH // 2 - subtext.get_width() // 2, HEIGHT // 2 + 40))

def valid_position(board, piece, dx=0, dy=0):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                nx, ny = piece.x + x + dx, piece.y + y + dy
                if nx < 0 or nx >= COLUMNS or ny >= ROWS:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True

def explode(board, x, y, color):
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLUMNS and 0 <= ny < ROWS:
                board[ny][nx] = 0
                for _ in range(5):
                    px = nx * CELL_SIZE + CELL_SIZE // 2
                    py = ny * CELL_SIZE + CELL_SIZE // 2
                    particles.append(Particle(px, py, color))

def place_piece(board, piece):
    bomb_bonus = 0
    if piece.is_bomb:
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    explode(board, piece.x + x, piece.y + y, piece.color)
        bomb_bonus = 20
    else:
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board[piece.y + y][piece.x + x] = piece.color
    return bomb_bonus

def clear_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines = ROWS - len(new_board)
    for _ in range(lines):
        new_board.insert(0, [0] * COLUMNS)
    return new_board, lines

def main():
    board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
    current_piece = Tetromino()
    next_piece = Tetromino()
    hold_piece = None
    can_hold = True
    score = 0
    fall_time = 0
    level = 0
    game_over = False
    running = True

    while running:
        dt = clock.tick(FPS)
        fall_time += dt
        level = score // 500
        fall_speed = max(100, 500 - level * 50)
        screen.fill(BLACK)

        if not game_over:
            if fall_time > fall_speed:
                if valid_position(board, current_piece, dy=1):
                    current_piece.y += 1
                else:
                    bonus = place_piece(board, current_piece)
                    board, lines = clear_lines(board)
                    score += bonus + lines * 100
                    current_piece = next_piece
                    next_piece = Tetromino()
                    can_hold = True
                    if not valid_position(board, current_piece):
                        game_over = True
                fall_time = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and valid_position(board, current_piece, dx=-1):
                        current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT and valid_position(board, current_piece, dx=1):
                        current_piece.x += 1
                    elif event.key == pygame.K_DOWN and valid_position(board, current_piece, dy=1):
                        current_piece.y += 1
                    elif event.key == pygame.K_UP:
                        old = current_piece.shape
                        current_piece.rotate()
                        if not valid_position(board, current_piece):
                            current_piece.shape = old
                    elif event.key == pygame.K_c and can_hold:
                        if hold_piece is None:
                            hold_piece = current_piece
                            current_piece = next_piece
                            next_piece = Tetromino()
                        else:
                            hold_piece, current_piece = current_piece, hold_piece
                        current_piece.x = COLUMNS // 2 - len(current_piece.shape[0]) // 2
                        current_piece.y = 0
                        can_hold = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    main()
                    return

        draw_board(board)
        draw_border()
        draw_ghost_piece(board, current_piece)
        if not game_over:
            draw_piece(current_piece)
        draw_next_piece(next_piece)
        draw_hold_piece(hold_piece)
        draw_score(score, level)
        if game_over:
            draw_game_over()

        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
