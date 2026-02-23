import pygame
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Easy Maze")
clock = pygame.time.Clock()

# Colors
BG = (30, 30, 30)
WALL = (200, 200, 200)
GOAL = (0, 155, 0)

# Grid
TILE = 40
ROWS = COLS = WIDTH // TILE

# Simple maze layout (1 = wall, 0 = path)
maze = [
    "1111111111",
    "1000000001",
    "1011111101",
    "1010000101",
    "1010110101",
    "1010010101",
    "1010111101",
    "1000000001",
    "1111111101",
    "1111111111",
]

# Player
player_x, player_y = 1, 1

# Goal
goal_x, goal_y = 6, 5

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    # Draw
    screen.fill(BG)

    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == "1":
                pygame.draw.rect(
                    screen,
                    WALL,
                    (x * TILE, y * TILE, TILE, TILE)
                )

    # Goal
    pygame.draw.rect(
        screen,
        GOAL,
        (goal_x * TILE, goal_y * TILE, TILE, TILE)
    )

    pygame.display.flip()
    clock.tick(10)
