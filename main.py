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

# Square (player)
size = 40
x = WIDTH // 2 - size // 2
y = HEIGHT - size - 50
speed = 5

y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False

# Ground
ground_y = HEIGHT - 50


#platform_terrain
box_terrain = pygame.Rect(350, 250, 100, 10)

# Bullets
bullet_width = 10
bullet_height = 4
bullet_speed = 8
bullets = []

#Limmit firerate
fire_delay = 250
last_shot_time = 0







# Game loop
while True:

    # --- EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Jump
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False

        # Shoot bullet (with cooldown)
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_time = pygame.time.get_ticks()
            if current_time - last_shot_time >= fire_delay:
                bullet_x = x + size
                bullet_y = y + size // 2 - bullet_height // 2
                bullets.append([bullet_x, bullet_y])
                last_shot_time = current_time


    # --- MOVEMENT ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    x = max(0, min(WIDTH - size, x))


    # --- GRAVITY ---
    y_velocity += gravity
    y += y_velocity

    if y + size >= ground_y:
        y = ground_y - size
        y_velocity = 0
        on_ground = True


    # --- BULLETS ---
    for bullet in bullets[:]:
        bullet[0] += bullet_speed
        if bullet[0] > WIDTH:
            bullets.remove(bullet)


    # --- DRAW ---
    screen.fill(DARK)

    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))
    pygame.draw.rect(screen, BLUE, (x, y, size, size))

    for bullet in bullets:
        pygame.draw.rect(screen, (255, 50, 50),
                         (bullet[0], bullet[1], bullet_width, bullet_height))

    pygame.draw.rect(screen, (255, 60, 60), box_terrain)

    pygame.display.flip()
    clock.tick(60)

