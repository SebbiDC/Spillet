import pygame
import sys
import math

pygame.init()

# Screen
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()

# Colors
WHITE = (240, 240, 240)
BLUE = (0, 150, 255)
DARK = (30, 30, 30)

# Camera
camera_x = 0
camera_y = 0

def apply_camera(x, y):
    return x - camera_x, y - camera_y

# Player
square_size = 50
square_x = WIDTH // 2
square_y = HEIGHT // 2
speed = 5

y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False



# Bullets
bullet_width = 10
bullet_height = 4
bullet_speed = 8
bullets = []
last_shot_time = 0
fire_rate = 300

# Map
TILE_SIZE = 50
PLATFORM_HEIGHT = TILE_SIZE // 2

map_layout = [
    "11111111111111111111111111111111111111111111111111111111111111111111",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10020000000010000000000000000000000000000000000000000000000000000001",
    "10000000200010000000000000000000000000000000000000000000000000000001",
    "10000020000010000000000000000000000000000000000000000000000000000001",
    "10111111111010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000000000001000000001000000000000000000000001",
    "10000000000010000000000000110000000000000000000000000000000000000001",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000000000000000000000000000000000000000000001",
    "10000000000010000000000000200000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000222200010000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "11111111111111111111111111111111111111111111111111111111111111111111",
]

def draw_map(surface):
    for row_index, row in enumerate(map_layout):
        for col_index, tile in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            sx, sy = apply_camera(x, y)

            if tile == "1":
                pygame.draw.rect(surface, WHITE, (sx, sy, TILE_SIZE, TILE_SIZE))
            elif tile == "2":
                pygame.draw.rect(surface, BLUE, (sx, sy + PLATFORM_HEIGHT, TILE_SIZE, PLATFORM_HEIGHT))

def get_wall_rects():
    walls = []
    for row_index, row in enumerate(map_layout):
        for col_index, tile in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if tile == "1":
                walls.append(("solid", pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)))
            elif tile == "2":
                walls.append(("platform", pygame.Rect(x, y + PLATFORM_HEIGHT, TILE_SIZE, PLATFORM_HEIGHT)))
    return walls

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        square_x -= speed
    if keys[pygame.K_d]:
        square_x += speed
        

 

    # Map collision
    on_ground_this_frame = False
    player_rect = pygame.Rect(square_x, square_y, square_size, square_size)

    for tile_type, wall in get_wall_rects():
        if player_rect.colliderect(wall):
            overlap_left = player_rect.right - wall.left
            overlap_right = wall.right - player_rect.left
            overlap_top = player_rect.bottom - wall.top
            overlap_bottom = wall.bottom - player_rect.top
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if tile_type == "platform":
                if min_overlap == overlap_top and y_velocity >= 0:
                    square_y = wall.top - square_size
                    y_velocity = 0
                    on_ground_this_frame = True
            
            
            else:
                if min_overlap == overlap_top:
                    square_y = wall.top - square_size
                    y_velocity = 0
                    on_ground_this_frame = True
                elif min_overlap == overlap_bottom:
                    square_y = wall.bottom
                    y_velocity = 0
                elif min_overlap == overlap_left:
                    square_x = wall.left - square_size
                elif min_overlap == overlap_right:
                    square_x = wall.right
                    
    if on_ground == True:
        gravity_toggle = 1
        
    else:
        gravity_toggle = 0
                    
       # Gravity
    if gravity_toggle == 0:
         y_velocity += gravity
         square_y += y_velocity


    if on_ground_this_frame:
        on_ground = True


    # Shooting
    if pygame.mouse.get_pressed()[0]:
        now = pygame.time.get_ticks()
        if now - last_shot_time >= fire_rate:
            bullet_x = square_x + square_size
            bullet_y = square_y + square_size // 2

            mx, my = pygame.mouse.get_pos()
            mx += camera_x
            my += camera_y

            dx, dy = mx - bullet_x, my - bullet_y
            dist = math.sqrt(dx**2 + dy**2) or 1

            bullets.append([bullet_x, bullet_y, (dx/dist)*bullet_speed, (dy/dist)*bullet_speed])
            last_shot_time = now

    # Move bullets
    for bullet in bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]

        bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)

        for tile_type, wall in get_wall_rects():
            if bullet_rect.colliderect(wall):
                bullets.remove(bullet)
                break

    # Camera follow
    camera_x = square_x - WIDTH // 2
    camera_y = square_y - HEIGHT // 2

    # Draw
    screen.fill(DARK)

    draw_map(screen)

    # Player
    pygame.draw.rect(
        screen,
        (0, 200, 255),
        (*apply_camera(square_x, square_y), square_size, square_size)
    )

    # Bullets
    for bullet in bullets:
        pygame.draw.rect(
            screen,
            (255, 50, 50),
            (*apply_camera(bullet[0], bullet[1]), bullet_width, bullet_height)
        )

    pygame.display.flip()
    clock.tick(60)