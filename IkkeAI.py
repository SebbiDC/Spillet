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

# Square (player)
square_size = 50
square_x = WIDTH // 2
square_y = HEIGHT // 2
speed = 5

y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False

# Ground
ground_y = HEIGHT - 50

# Bullets
bullet_width = 10
bullet_height = 4
bullet_speed = 8
bullets = []  # Each bullet is [x, y, vx, vy]
last_shot_time = 0
fire_rate = 300  # Milliseconds between shots

# Map
TILE_SIZE = 50
PLATFORM_HEIGHT = TILE_SIZE // 2  # Platforms are half the size of normal tiles
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
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "10000000000000000000000000000000000000000000000000000000000000000001",
    "11111111111111111111111111111111111111111111111111111111111111111111",
]

# 0 = air, 1 = solid wall/floor, 2 = platform (half height)
def draw_map(surface):
    for row_index, row in enumerate(map_layout):
        for col_index, tile in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if tile == "1":
                pygame.draw.rect(surface, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile == "2":
                # Draw platform at the bottom half of the tile slot
                pygame.draw.rect(surface, BLUE, (x, y + PLATFORM_HEIGHT, TILE_SIZE, PLATFORM_HEIGHT))

def get_wall_rects():
    walls = []
    for row_index, row in enumerate(map_layout):
        for col_index, tile in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if tile == "1":
                walls.append(("solid", pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)))
            elif tile == "2":
                # Collision rect sits at the bottom half of the tile slot
                walls.append(("platform", pygame.Rect(x, y + PLATFORM_HEIGHT, TILE_SIZE, PLATFORM_HEIGHT)))
    return walls



# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Jump
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                y_velocity = jump_strength
                on_ground = False
        
        
        # Key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        square_x -= speed
    if keys[pygame.K_d]:
        square_x += speed   
        
    # Apply gravity
    y_velocity += gravity
    square_y += y_velocity

    # Collision with ground
    if square_y + square_size >= ground_y:
        square_y = ground_y - square_size
        y_velocity = 0
        on_ground = True

    # Collision with map walls
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
                # Platforms only block from above, and only when falling
                if min_overlap == overlap_top and y_velocity >= 0:
                    square_y = wall.top - square_size
                    y_velocity = 0
                    on_ground_this_frame = True
            else:
                # Solid tiles block from all sides
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

    if on_ground_this_frame:
        on_ground = True

        # Fire bullet
    if pygame.mouse.get_pressed()[0]:
        now = pygame.time.get_ticks()
        if now - last_shot_time >= fire_rate:
            bullet_x = square_x + square_size
            bullet_y = square_y + square_size // 2 - bullet_height // 2
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - bullet_x, my - bullet_y
            dist = math.sqrt(dx**2 + dy**2) or 1
            bullets.append([bullet_x, bullet_y, (dx/dist)*bullet_speed, (dy/dist)*bullet_speed])
            last_shot_time = now

    # Move bullets
    for bullet in bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        if bullet[0] > WIDTH or bullet[0] < 0 or bullet[1] > HEIGHT or bullet[1] < 0:
            bullets.remove(bullet)
        # Remove bullet if it hits a wall
        bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)
        for tile_type, wall in get_wall_rects():
            if bullet_rect.colliderect(wall) and bullet in bullets:
                bullets.remove(bullet)


    # Draw
    screen.fill(DARK)

    # Ground
    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))

    # Map
    draw_map(screen)

    # Square
    pygame.draw.rect(
        screen,
        (0, 200, 255),
        (square_x, square_y, square_size, square_size)
    )
    
    # Bullets
    for bullet in bullets:
        pygame.draw.rect(
            screen,
            (255, 50, 50),
            (int(bullet[0]), int(bullet[1]), bullet_width, bullet_height)
    )
        
    

    pygame.display.flip()
    clock.tick(60)