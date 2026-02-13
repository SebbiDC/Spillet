import pygame
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 500, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Counter")
clock = pygame.time.Clock()

# Colors
BG = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

# Font
font = pygame.font.SysFont(None, 48)

# Counter
space_count = 0

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_count += 1

    # Draw
    screen.fill(BG)

    text = font.render(f"Space pressed: {space_count}", True, TEXT_COLOR)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

    pygame.display.flip()
    clock.tick(60)
