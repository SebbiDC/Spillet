import pygame
import sys

pygame.init()

# ------------------------
# Screen and clock
# ------------------------
BASE_WIDTH, BASE_HEIGHT = 600, 400
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()

# Scaling factors
scale_x = WIDTH / BASE_WIDTH
scale_y = HEIGHT / BASE_HEIGHT

# ------------------------
# Colors
# ------------------------
WHITE = (240, 240, 240)
BLUE = (0, 150, 255)
DARK = (30, 30, 30)
PLATFORM_COLOR = (255, 60, 60)
BULLET_COLOR = (255, 50, 50)

# ------------------------
# Player
# ------------------------
size = 40
speed = 5
y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False
drop_down = False
drop_platform = None

x = BASE_WIDTH // 2 - size // 2
y = BASE_HEIGHT - size - 50
player_rect = pygame.Rect(x, y, size, size)

# ------------------------
# Map (grid-based)
# ------------------------
TILE = 40
ROOM_ROWS = 20
ROOM_COLS = 20
PLATFORM_HEIGHT = TILE // 2  # Half-height platforms

# 1 = terrain (solid), 2 = platform (pass-through), 0 = empty
room_grid = [
    "11111111111111111111",
    "10000000000000000001",
    "10002000002000200001",
    "10000000000000000001",
    "10200020002000200021",
    "10000000000000000001",
    "10000000002000000001",
    "10000000000000000001",
    "10000000200000020001",
    "10000000000000000001",
    "10200020002000200021",
    "10000000000000000001",
    "10000000002000000001",
    "10000000000000000001",
    "10000000200000020001",
    "10000000000000000001",
    "10200020002000200021",
    "10000000000000000001",
    "10000000000000000001",
    "11111111111111111111",
]

terrain = []
platforms = []

for y_idx, row in enumerate(room_grid):
    for x_idx, cell in enumerate(row):
        if cell == "1":
            terrain.append(pygame.Rect(x_idx * TILE, y_idx * TILE, TILE, TILE))
        elif cell == "2":
            platforms.append(pygame.Rect(x_idx * TILE, y_idx * TILE + TILE // 2, TILE, PLATFORM_HEIGHT))

# ------------------------
# Bullets
# ------------------------
bullet_width = 10
bullet_height = 4
bullet_speed = 8
bullets = []
fire_delay = 250
last_shot_time = 0
shooting = False

# ------------------------
# Camera
# ------------------------
camera_x = 0
camera_y = 0
camera_lerp_speed = 0.1
camera_lead = 50

# ------------------------
# Game loop
# ------------------------
while True:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False
            if event.key == pygame.K_s:
                for plat in platforms:
                    if player_rect.bottom == plat.top and player_rect.right > plat.left and player_rect.left < plat.right:
                        drop_down = True
                        drop_platform = plat
                        y_velocity = 5
                        on_ground = False
                        break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shooting = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            shooting = False

    # ------------------------
    # MOVEMENT
    # ------------------------
    keys = pygame.key.get_pressed()
    moving_horizontally = False
    x_velocity = 0
    if keys[pygame.K_a]:
        x_velocity = -speed
        moving_horizontally = True
    if keys[pygame.K_d]:
        x_velocity = speed
        moving_horizontally = True
    x += x_velocity

    y_velocity += gravity
    y += y_velocity

    # ------------------------
    # COLLISIONS
    # ------------------------
    on_ground = False

    # Horizontal collisions
    player_rect.x = x
    for terr in terrain:
        if player_rect.colliderect(terr):
            if x_velocity > 0:
                player_rect.right = terr.left
            elif x_velocity < 0:
                player_rect.left = terr.right
    x = player_rect.x

    # Vertical collisions
    prev_y = player_rect.bottom  # previous bottom
    player_rect.y = y
    for terr in terrain:
        if player_rect.colliderect(terr):
            if y_velocity > 0:  # falling
                player_rect.bottom = terr.top
                y_velocity = 0
                on_ground = True
            elif y_velocity < 0:  # jumping
                player_rect.top = terr.bottom
                y_velocity = 0
    y = player_rect.y

    # Drop-through platforms
    for plat in platforms:
        if drop_down and plat == drop_platform:
            continue
        # Land only if coming from above
        if y_velocity > 0 and prev_y <= plat.top and player_rect.colliderect(plat):
            player_rect.bottom = plat.top
            y_velocity = 0
            on_ground = True
            y = player_rect.y

    if drop_down and drop_platform and player_rect.top > drop_platform.bottom:
        drop_down = False
        drop_platform = None

    # ------------------------
    # BULLETS
    # ------------------------
    current_time = pygame.time.get_ticks()
    if shooting and current_time - last_shot_time >= fire_delay:
        mouse_x = pygame.mouse.get_pos()[0] / scale_x + camera_x
        mouse_y = pygame.mouse.get_pos()[1] / scale_y + camera_y

        start_x = player_rect.centerx
        start_y = player_rect.centery

        dx = mouse_x - start_x
        dy = mouse_y - start_y
        distance = max((dx**2 + dy**2)**0.5, 1)

        vx = (dx / distance) * bullet_speed
        vy = (dy / distance) * bullet_speed

        bullets.append({"rect": pygame.Rect(start_x, start_y, bullet_width, bullet_height), "vx": vx, "vy": vy})
        last_shot_time = current_time

    for bullet in bullets[:]:
        bullet["rect"].x += bullet["vx"]
        bullet["rect"].y += bullet["vy"]
        if bullet["rect"].x < 0 or bullet["rect"].x > ROOM_COLS*TILE or bullet["rect"].y < 0 or bullet["rect"].y > ROOM_ROWS*TILE:
            bullets.remove(bullet)

    # ------------------------
    # CAMERA
    # ------------------------
    target_camera_x = player_rect.centerx - BASE_WIDTH / 2
    target_camera_y = player_rect.centery - BASE_HEIGHT / 2
    if moving_horizontally:
        if keys[pygame.K_d]:
            target_camera_x += camera_lead
        elif keys[pygame.K_a]:
            target_camera_x -= camera_lead
    camera_x += (target_camera_x - camera_x) * camera_lerp_speed
    camera_y += (target_camera_y - camera_y) * camera_lerp_speed

    # ------------------------
    # DRAW
    # ------------------------
    screen.fill(DARK)
    for terr in terrain:
        pygame.draw.rect(screen, WHITE, pygame.Rect((terr.x - camera_x) * scale_x, (terr.y - camera_y) * scale_y, terr.width * scale_x, terr.height * scale_y))
    for plat in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, pygame.Rect((plat.x - camera_x) * scale_x, (plat.y - camera_y) * scale_y, plat.width * scale_x, plat.height * scale_y))
    pygame.draw.rect(screen, BLUE, pygame.Rect((player_rect.x - camera_x) * scale_x, (player_rect.y - camera_y) * scale_y, player_rect.width * scale_x, player_rect.height * scale_y))
    for bullet in bullets:
        pygame.draw.rect(screen, BULLET_COLOR, pygame.Rect((bullet["rect"].x - camera_x) * scale_x, (bullet["rect"].y - camera_y) * scale_y, bullet["rect"].width * scale_x, bullet["rect"].height * scale_y))

    pygame.display.flip()
    clock.tick(60)