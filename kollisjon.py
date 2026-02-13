import pygame
import sys

pygame.init()


# Screen

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()


# Colors
WHITE = (240, 240, 240)
BLUE = (0, 150, 255)
DARK = (30, 30, 30)
PLATFORM_COLOR = (255, 60, 60)
BULLET_COLOR = (255, 50, 50)

# Player
size = 40
x = WIDTH // 2 - size // 2
y = HEIGHT - size - 50
speed = 5

y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False

# Player rectangle (for collision)
player_rect = pygame.Rect(x, y, size, size)

# Platforms
ground_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
platforms = [
    pygame.Rect(350, 250, 100, 10),
    pygame.Rect(150, 180, 100, 10),
]

# Bullets
bullet_width = 10
bullet_height = 4
bullet_speed = 8
bullets = []

# Fire rate limit (milliseconds)
fire_delay = 250
last_shot_time = 0

# Game loop
while True:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Jump
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False

        # Shoot bullets with cooldown
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_time = pygame.time.get_ticks()
            if current_time - last_shot_time >= fire_delay:
                bullet_x = player_rect.right
                bullet_y = player_rect.centery - bullet_height // 2
                bullets.append([bullet_x, bullet_y])
                last_shot_time = current_time

    # MOVEMENT
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    # Keep player inside screen horizontally
    x = max(0, min(WIDTH - size, x))

    # GRAVITY
    y_velocity += gravity
    y += y_velocity

    # Update player rect
    player_rect.x = x
    player_rect.y = y

    # COLLISIONS
    on_ground = False  # reset

    # Ground collision
    if player_rect.colliderect(ground_rect) and y_velocity >= 0:
        y = ground_rect.top - size
        y_velocity = 0
        on_ground = True
        player_rect.y = y

    # Platform collisions
    for plat in platforms:
        if player_rect.colliderect(plat) and y_velocity >= 0:
            y = plat.top - size
            y_velocity = 0
            on_ground = True
            player_rect.y = y

    # BULLETS UPDATE
    for bullet in bullets[:]:
        bullet[0] += bullet_speed
        if bullet[0] > WIDTH:
            bullets.remove(bullet)

    # DRAW
    screen.fill(DARK)

    # Draw ground
    pygame.draw.rect(screen, WHITE, ground_rect)

    # Draw platforms
    for plat in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, plat)

    # Draw player
    pygame.draw.rect(screen, BLUE, player_rect)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, BULLET_COLOR,
                         (bullet[0], bullet[1], bullet_width, bullet_height))

    pygame.display.flip()
    clock.tick(60)
