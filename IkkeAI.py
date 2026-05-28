import pygame
import sys
import math
import random

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
ORANGE = (255, 165, 0)

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
player_hp = 5
player_max_hp = 5
player_damage_cooldown = 5

y_velocity = 0
gravity = 0.6
jump_strength = -12
on_ground = False



# Bullets
bullet_width = 5
bullet_height = 5
bullet_speed = 8
bullets = []
last_shot_time = 0
fire_rate = 300

wave_composition = {
    "grubb": 5
}



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
    "10000000000000000000000000000003000000000000000000000000000000000001",
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
            elif tile == "3":
                pygame.draw.rect(surface, ORANGE, (sx, sy, TILE_SIZE, TILE_SIZE))

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

#grubb spawn points
def get_spawn_points():
    spawns = []
    for row_index, row in enumerate(map_layout):
        for col_index, tile in enumerate(row):
            if tile == "3":
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                spawns.append((x, y))
    
    return spawns

# Monters
def spawn_wave(wave_number):
    grubbs = []
    for enemy_type, count in wave_composition.items():
        for i in range(count * wave_number):
            x, y = random.choice(spawn_points)
            if enemy_type == "grubb":
                grubbs.append({
                    "type": "grubb",
                    "x": x, "y": y,
                    "speed": 2,
                    "direction": random.choice([-1, 1]),
                    "hp": 3
                })
    return grubbs

wave = 0
spawn_points = get_spawn_points()
grubbs = []
wave_active = False

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
            if event.key == pygame.K_h and not wave_active:
                wave_active = True
                wave += 1
                grubbs = spawn_wave(wave)

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
        
        #grubbs
    for grubb in grubbs[:]:
        grubb["x"] += grubb["speed"] * grubb["direction"]
        grubb_rect = pygame.Rect(grubb["x"], grubb["y"], TILE_SIZE, TILE_SIZE)

        for tile_type, wall in get_wall_rects():
            if grubb_rect.colliderect(wall):
                grubb["direction"] *= -1
                grubb["x"] += grubb["speed"] * grubb["direction"]
                break

        foran_x = grubb["x"] + (TILE_SIZE if grubb["direction"] == 1 else 0)
        if not any(w.collidepoint(foran_x, grubb["y"] + TILE_SIZE + 1) for _, w in get_wall_rects()):
            grubb["direction"] *= -1

        for bullet in bullets[:]:
            if grubb_rect.colliderect(pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)):
                grubb["hp"] -= 1
                bullets.remove(bullet)
                if grubb["hp"] <= 0:
                    grubbs.remove(grubb)
                break

        if grubb in grubbs and grubb_rect.colliderect(player_rect) and player_damage_cooldown <= 0:
            player_hp -= 1
            player_damage_cooldown = 30

    if player_damage_cooldown > 0:
        player_damage_cooldown -= 1

    if len(grubbs) == 0 and wave_active:
        wave_active = False


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

    # Grubbs
    for grubb in grubbs:
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            (*apply_camera(grubb["x"], grubb["y"]), TILE_SIZE, TILE_SIZE)
        )

    pygame.display.flip()
    clock.tick(60)