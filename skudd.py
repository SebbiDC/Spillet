import pygame
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Square Shooter")
clock = pygame.time.Clock()

# Player
player_size = 40
player_x = 50
player_y = HEIGHT // 2
player_speed = 5

# Bullets
bullet_width = 10
bullet_height = 4
bullet_speed = 8
bullets = []

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Fire bullet
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_x = player_x + player_size
                bullet_y = player_y + player_size // 2 - bullet_height // 2
                bullets.append([bullet_x, bullet_y])

    # Move bullets
    for bullet in bullets[:]:
        bullet[0] += bullet_speed
        if bullet[0] > WIDTH:
            bullets.remove(bullet)

    # Draw
    screen.fill((20, 20, 20))

    # Player
    pygame.draw.rect(
        screen,
        (0, 200, 255),
        (player_x, player_y, player_size, player_size)
    )

    # Bullets
    for bullet in bullets:
        pygame.draw.rect(
            screen,
            (255, 50, 50),
            (bullet[0], bullet[1], bullet_width, bullet_height)
        )

    pygame.display.flip()
    clock.tick(60)
