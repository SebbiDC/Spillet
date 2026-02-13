import pygame
import sys

pygame.init()

# ------------------------
# Base and current resolution
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
drop_down = False       # True while dropping
drop_platform = None    # platform being dropped through

x = BASE_WIDTH // 2 - size // 2
y = BASE_HEIGHT - size - 50
player_rect = pygame.Rect(x, y, size, size)

# ------------------------
# Platforms
# ------------------------
ground_rect = pygame.Rect(0, BASE_HEIGHT - 50, BASE_WIDTH, 50)
platforms = [
    pygame.Rect(350, 250, 400, 10),
    pygame.Rect(150, 180, 100, 10),
]

# ------------------------
# Bullets
# ------------------------
bullet_width = 10
bullet_height = 4
bullet_speed = 8
bullets = []

fire_delay = 250  # ms
last_shot_time = 0
shooting = False  # True when left mouse button held

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
    # ------------------------
    # EVENTS
    # ------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Jump
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False

            # Drop through platforms
            if event.key == pygame.K_s:
                for plat in platforms:
                    # Check if standing on top of platform
                    if (player_rect.bottom == plat.top and
                        player_rect.right > plat.left and
                        player_rect.left < plat.right):
                        drop_down = True
                        drop_platform = plat
                        y_velocity = 5  # small push to start falling
                        on_ground = False
                        break

        # Autofire
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shooting = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            shooting = False

    # ------------------------
    # MOVEMENT
    # ------------------------
    keys = pygame.key.get_pressed()
    moving_horizontally = False
    if keys[pygame.K_a]:
        x -= speed
        moving_horizontally = True
    if keys[pygame.K_d]:
        x += speed
        moving_horizontally = True
    x = max(0, min(BASE_WIDTH - size, x))

    # GRAVITY
    y_velocity += gravity
    y += y_velocity
    player_rect.x = x
    player_rect.y = y

    # ------------------------
    # COLLISIONS
    # ------------------------
    on_ground = False

    # Ground collision
    if player_rect.colliderect(ground_rect) and y_velocity >= 0:
        y = ground_rect.top - size
        y_velocity = 0
        on_ground = True
        player_rect.y = y

    # Platform collisions
    for plat in platforms:
        if drop_down and plat == drop_platform:
            continue  # skip collision with platform being dropped through
        if player_rect.colliderect(plat) and y_velocity >= 0:
            y = plat.top - size
            y_velocity = 0
            on_ground = True
            player_rect.y = y

    # Reset drop_down once fully below platform
    if drop_down and player_rect.top > drop_platform.bottom:
        drop_down = False
        drop_platform = None

    # ------------------------
    # BULLETS AUTOFIRE
    # ------------------------
    current_time = pygame.time.get_ticks()
    if shooting and current_time - last_shot_time >= fire_delay:
        mouse_x = pygame.mouse.get_pos()[0] / scale_x + camera_x
        mouse_y = pygame.mouse.get_pos()[1] / scale_y + camera_y

        start_x = player_rect.centerx
        start_y = player_rect.centery

        dx = mouse_x - start_x
        dy = mouse_y - start_y
        distance = (dx**2 + dy**2)**0.5
        if distance == 0:
            distance = 1

        vx = (dx / distance) * bullet_speed
        vy = (dy / distance) * bullet_speed

        bullets.append({
            "rect": pygame.Rect(start_x, start_y, bullet_width, bullet_height),
            "vx": vx,
            "vy": vy
        })

        last_shot_time = current_time

    # ------------------------
    # BULLETS MOVEMENT
    # ------------------------
    for bullet in bullets[:]:
        bullet["rect"].x += bullet["vx"]
        bullet["rect"].y += bullet["vy"]
        if (bullet["rect"].x < 0 or bullet["rect"].x > BASE_WIDTH or
            bullet["rect"].y < 0 or bullet["rect"].y > BASE_HEIGHT):
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

    # Draw ground
    pygame.draw.rect(screen, WHITE,
                     pygame.Rect((ground_rect.x - camera_x) * scale_x,
                                 (ground_rect.y - camera_y) * scale_y,
                                 ground_rect.width * scale_x,
                                 ground_rect.height * scale_y))

    # Draw platforms
    for plat in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR,
                         pygame.Rect((plat.x - camera_x) * scale_x,
                                     (plat.y - camera_y) * scale_y,
                                     plat.width * scale_x,
                                     plat.height * scale_y))

    # Draw player
    pygame.draw.rect(screen, BLUE,
                     pygame.Rect((player_rect.x - camera_x) * scale_x,
                                 (player_rect.y - camera_y) * scale_y,
                                 player_rect.width * scale_x,
                                 player_rect.height * scale_y))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, BULLET_COLOR,
                         pygame.Rect((bullet["rect"].x - camera_x) * scale_x,
                                     (bullet["rect"].y - camera_y) * scale_y,
                                     bullet["rect"].width * scale_x,
                                     bullet["rect"].height * scale_y))

    pygame.display.flip()
    clock.tick(60)
