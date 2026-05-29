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
gold_fetch = 10
gold = 0



# Physics
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
damage = 1



# Map
TILE_SIZE = 50
PLATFORM_HEIGHT = TILE_SIZE // 2

map_layout = [
    "11111111111111111111111111111111000111111111111111111111111111111111",
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
    "10000000000000000000003000000000000000000000000000000000000000000001",
    "10000000000000000002222220000000000000000000030000030000000000000001",
    "10003000000000300000000003000000000030000000022222222000000000000001",
    "11111111111111220000000002200002111111100000000000000003000000000001",
    "10000000000000000000300000000000000000000000000000000222200000000001",
    "10000000000000000222222000000000000000000000000000000000000000003001",
    "10000030000000000000000000030000000000000003000000000000000022222221",
    "10000222000000000000001000222200000000000022220000000003000000000001",
    "11000000000001000000011000000000000000000000000000011111100000000011",
    "11100030000111000300111000000000000300000000000000111111110003000111",
    "11111111111111111111111111111111111111111111111111111111111111111111",
]

# Draw map tiles
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

# Build collision rectangles from map
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

# Get spawn point positions from map
def get_spawn_points():
    spawns = []
    for row_index, row in enumerate(map_layout):
        for col_index, tile in enumerate(row):
            if tile == "3":
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                spawns.append((x, y))
    return spawns

# Build a queue of monsters for the wave
def spawn_wave(wave_number):
    queue = []
    for enemy_type, count in wave_composition.items():
        for i in range(int(20 * wave_number / 2 + 5)):
            x, y = random.choice(get_spawn_points())
            if enemy_type == "grubb":
                queue.append({
                    "type": "grubb",
                    "x": x, "y": y,
                    "speed": 2,
                    "direction": random.choice([-1, 1]),
                    "hp": 3,
                    "vy": 0
                })
                print(f"Wave {wave_number}: {len(queue)} grubbs")
    return queue

def roll_shop():
    return random.sample(all_cards, 3)

# Wave state
wave = 0
grubbs = []
wave_active = False
spawn_queue = []
spawn_timer = 0

# Wave settings
wave_composition = {
    "grubb": 20
}

# cards
all_cards = [
    {"name": "Vigor - Max HP +1",             "price": 100, "effect": "max_hp"},
    {"name": "Sprint - Speed +1",             "price": 35,  "effect": "speed"},
    {"name": "Gattling - Fire rate +1",       "price": 100, "effect": "fire_rate"},
    {"name": "Greed - Gold gain x1.2",        "price": 95,  "effect": "gold_gain"},
    {"name": "High caliber - Damage +1",      "price": 200, "effect": "gun_dmg"},
    {"name": "Bandage - Recover health",      "price": 60,  "effect": "current_hp"},
    {"name": "Leg day - Jump higher",         "price": 60,  "effect": "jump_height"}
    ]
shop_cards = roll_shop()
shop_open = False




# Game loop
while True:
    # Events
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
                spawn_queue = spawn_wave(wave)
                spawn_timer = 60
            if event.key == pygame.K_b:
                shop_open = not shop_open
        
        if event.type == pygame.MOUSEBUTTONDOWN and shop_open:
            mx, my = pygame.mouse.get_pos()
            for i, card in enumerate(shop_cards):
                card_x = 400 + i * 200
                card_y = 400
                card_rect = pygame.Rect(card_x, card_y, 180, 250)
                if card_rect.collidepoint(mx, my) and gold >= card["price"]:
                    gold -= card["price"]
                    shop_cards.pop(i)
                    
                    # Give the buff
                    if card["effect"] == "max_hp":
                        player_max_hp += 1
                        
                    if card["effect"] == "speed":
                        speed += 3
                    
                    if card["effect"] == "fire_rate":
                        fire_rate -= 100
                        
                    if card["effect"] == "gold_gain":
                        gold_fetch *= 1.2
                        
                    if card["effect"] == "gun_dmg":
                        damage += 1
                    
                    if card["effect"] == "current_hp":
                        player_hp += player_max_hp // 2
                        
                    if card["effect"] == "jump_height":
                        jump_strength -= 1
                    break
            
            # Reroll button
            reroll_rect = pygame.Rect(400, 680, 200, 50)
            if reroll_rect.collidepoint(mx, my) and gold >= 25:
                gold -= 25
                shop_cards = roll_shop()
                                 

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        square_x -= speed
    if keys[pygame.K_d]:
        square_x += speed

    # Map collision
    under_y = square_y + square_size + 1
    has_floor = any(w.collidepoint(square_x + square_size // 2, under_y) for _, w in get_wall_rects())
    if on_ground and not has_floor:
        on_ground = False

    if on_ground:
        y_velocity = 0
    else:
        y_velocity += gravity
        y_velocity = min(y_velocity, 20)
    square_y += y_velocity

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
                    on_ground = True
            else:
                if min_overlap == overlap_top:
                    square_y = wall.top - square_size
                    y_velocity = 0
                    on_ground = True
                elif min_overlap == overlap_bottom:
                    square_y = wall.bottom
                    y_velocity = 0
                elif min_overlap == overlap_left:
                    square_x = wall.left - square_size
                elif min_overlap == overlap_right:
                    square_x = wall.right
            player_rect = pygame.Rect(square_x, square_y, square_size, square_size)

    # Spawn queue
    if spawn_queue:
        spawn_timer -= 1
        if spawn_timer <= 0:
            grubbs.append(spawn_queue.pop(0))
            spawn_timer = 60

    # Grubbs
    for grubb in grubbs[:]:

        # Horizontal movement
        grubb["x"] += grubb["speed"] * grubb["direction"]
        grubb_rect = pygame.Rect(grubb["x"], grubb["y"], TILE_SIZE, TILE_SIZE)

        # Horizontal wall collision
        for tile_type, wall in get_wall_rects():
            if tile_type == "solid" and grubb_rect.colliderect(wall):
                overlap_left = grubb_rect.right - wall.left
                overlap_right = wall.right - grubb_rect.left
                if overlap_left < overlap_right:
                    grubb["x"] = wall.left - TILE_SIZE
                else:
                    grubb["x"] = wall.right
                grubb["direction"] *= -1
                grubb_rect = pygame.Rect(grubb["x"], grubb["y"], TILE_SIZE, TILE_SIZE)
                break

        # Edge detection
        foran_x = grubb["x"] + (TILE_SIZE if grubb["direction"] == 1 else 0)
        if not any(w.collidepoint(foran_x, grubb["y"] + TILE_SIZE + 1) for _, w in get_wall_rects()):
            grubb["direction"] *= -1

        # Vertical movement
        grubb["vy"] += gravity
        grubb["vy"] = min(grubb["vy"], 20)
        grubb["y"] += grubb["vy"]
        grubb_rect = pygame.Rect(grubb["x"], grubb["y"], TILE_SIZE, TILE_SIZE)

        # Vertical collision
        for tile_type, wall in get_wall_rects():
            if grubb_rect.colliderect(wall):
                overlap_top = grubb_rect.bottom - wall.top
                overlap_bottom = wall.bottom - grubb_rect.top
                if overlap_top < overlap_bottom and tile_type in ("solid", "platform"):
                    grubb["y"] = wall.top - TILE_SIZE
                    grubb["vy"] = 0
                elif overlap_bottom <= overlap_top and tile_type == "solid":
                    grubb["y"] = wall.bottom
                    grubb["vy"] = 0
                grubb_rect = pygame.Rect(grubb["x"], grubb["y"], TILE_SIZE, TILE_SIZE)

        # Bullet hit
        for bullet in bullets[:]:
            if grubb_rect.colliderect(pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)):
                grubb["hp"] -= damage
                bullets.remove(bullet)
                if grubb["hp"] <= 0:
                    grubbs.remove(grubb)
                    gold += gold_fetch
                    print(gold)
                break

        # Touch damage
        if grubb in grubbs and grubb_rect.colliderect(player_rect) and player_damage_cooldown <= 0:
            player_hp -= 1
            player_damage_cooldown = 30
            print(player_hp)

    # Player damage cooldown
    if player_damage_cooldown > 0:
        player_damage_cooldown -= 1
        
        
    # Death check
    if player_hp <= 0:
        square_x = WIDTH // 2
        square_y = HEIGHT // 2
        y_velocity = 0
        on_ground = False
        speed = 5
        player_hp = 5
        player_max_hp = 5
        player_damage_cooldown = 0
        gold_fetch = 10
        gold = 0
        fire_rate = 300
        bullet_speed = 8
        damage = 1
        jump_strength = -12
        bullets = []
        grubbs = []
        spawn_queue = []
        wave = 0
        wave_active = False
        shop_cards = roll_shop()
        shop_open = False

    # Wave clear check
    if len(grubbs) == 0 and len(spawn_queue) == 0 and wave_active:
        wave_active = False

    # Shooting
    if pygame.mouse.get_pressed()[0]:
        now = pygame.time.get_ticks()
        if now - last_shot_time >= fire_rate:
            bullet_x = square_x + square_size // 2
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
            if tile_type == "solid" and bullet_rect.colliderect(wall):
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



    # Shop
    if shop_open:
        font = pygame.font.Font(None, 28)
        for i, card in enumerate(shop_cards):
            card_x = 400 + i * 220
            card_y = 400
            pygame.draw.rect(screen, (80, 80, 80), (card_x, card_y, 180, 250))
            pygame.draw.rect(screen, WHITE, (card_x, card_y, 180, 250), 2)
            screen.blit(font.render(card["name"], True, WHITE), (card_x + 10, card_y + 20))
            screen.blit(font.render(f"{card['price']} gold", True, ORANGE), (card_x + 10, card_y + 60))
        # Reroll button
        pygame.draw.rect(screen, (60, 60, 60), (400, 680, 200, 50))
        screen.blit(font.render("Reroll - 25g", True, WHITE), (410, 695))
        # Gold display
        screen.blit(font.render(f"Gold: {gold}", True, ORANGE), (400, 370))
    
    
    # Wave counter
    font = pygame.font.Font(None, 48)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    screen.blit(wave_text, (WIDTH - wave_text.get_width() - 20, 20))
    
    
    
    for i in range(player_max_hp):
        color = (0, 200, 0) if i < player_hp else (150, 0, 0)
        pygame.draw.rect(screen, color, (20 + i * 40, 20, 30, 30))
    
    
    pygame.display.flip()
    clock.tick(60)