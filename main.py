import pygame
import sys
import random

pygame.init()

# ------------------------
# Constants
# ------------------------
BASE_WIDTH, BASE_HEIGHT = 600, 400
WIDTH, HEIGHT = 1920, 1080
TILE = 40
PLATFORM_HEIGHT = TILE // 2
PLAYER_SIZE = 40
PLAYER_SPEED = 5
GRAVITY = 0.6
JUMP_STRENGTH = -13
BULLET_SIZE = 8
BULLET_SPEED = 8
FIRE_DELAY = 250

# ------------------------
# Colors
# ------------------------
WHITE = (240, 240, 240)
BLUE = (0, 150, 255)
DARK = (30, 30, 30)
PLATFORM_COLOR = (255, 60, 60)
BULLET_COLOR = (255, 50, 50)
DOOR_COLOR = (255, 255, 0)
MAP_COLOR = (180, 180, 255)

# ------------------------
# Screen / Camera
# ------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Square")
clock = pygame.time.Clock()
scale_x = WIDTH / BASE_WIDTH
scale_y = HEIGHT / BASE_HEIGHT
camera_x = camera_y = 0
camera_lerp = 0.1
camera_lead = 50

# ------------------------
# Map
# ------------------------
show_map = False
MAP_SCALE = 20
MAP_PADDING = 10

# ------------------------
# Player
# ------------------------
player_rect = pygame.Rect(TILE + 2, TILE + 2, PLAYER_SIZE, PLAYER_SIZE)
x_velocity = y_velocity = 0
on_ground = False
drop_down = False
drop_platforms = set()
shooting = False
last_shot_time = 0
bullets = []

# ------------------------
# Player Movement
# ------------------------
def move_player():
    global y_velocity, on_ground, drop_down

    # Horizontal
    player_rect.x += x_velocity
    for terr in terrain:
        if player_rect.colliderect(terr):
            if x_velocity > 0: player_rect.right = terr.left
            elif x_velocity < 0: player_rect.left = terr.right

    # Vertical
    y_velocity += GRAVITY
    prev_bottom = player_rect.bottom
    player_rect.y += y_velocity
    on_ground = False

    for terr in terrain:
        if player_rect.colliderect(terr):
            if y_velocity > 0: player_rect.bottom = terr.top; y_velocity = 0; on_ground = True
            elif y_velocity < 0: player_rect.top = terr.bottom; y_velocity = 0

    for i, plat in enumerate(platforms):
        if drop_down and i in drop_platforms: continue
        if y_velocity >= 0 and prev_bottom <= plat.top and player_rect.colliderect(plat):
            player_rect.bottom = plat.top
            y_velocity = 0
            on_ground = True

    if drop_down and all(player_rect.top > platforms[i].bottom for i in drop_platforms):
        drop_down = False
        drop_platforms.clear()

# ------------------------
# Doors / Room Transition
# ------------------------
def handle_doors():
    global in_transition, transition_target_room, exit_door_name, transition_path, transition_index, previous_room_id, current_room_id

    if in_transition: return

    for door_type, rect in door_coords.items():
        if player_rect.colliderect(rect):
            current_room = room_graph[current_room_id]
            if door_type == "next":
                if current_room.connections["next"] is None:
                    next_room_id = len(room_graph)
                    current_room.connections["next"] = next_room_id
                else:
                    next_room_id = current_room.connections["next"]
            else:  # back door
                next_room_id = current_room.connections["back"]

            # Start transition
            in_transition = True
            transition_target_room = next_room_id
            exit_door_name = door_type
            transition_path = [(rect.centerx, rect.centery)]
            transition_index = 0

            # Update previous_room_id
            previous_room_id = current_room_id
            break



# ------------------------
# Bullets
# ------------------------
def handle_bullets():
    global last_shot_time
    current_time = pygame.time.get_ticks()
    if shooting and current_time - last_shot_time >= FIRE_DELAY:
        mx, my = pygame.mouse.get_pos()
        mx = mx / scale_x + camera_x
        my = my / scale_y + camera_y
        dx, dy = mx - player_rect.centerx, my - player_rect.centery
        dist = max((dx**2 + dy**2)**0.5, 1)
        bullets.append({"rect": pygame.Rect(player_rect.centerx, player_rect.centery, BULLET_SIZE, BULLET_SIZE),
                        "vx": dx/dist*BULLET_SPEED, "vy": dy/dist*BULLET_SPEED})
        last_shot_time = current_time

    for b in bullets[:]:
        b["rect"].x += b["vx"]
        b["rect"].y += b["vy"]
        if b["rect"].right < 0 or b["rect"].left > ROOM_COLS*TILE or b["rect"].bottom < 0 or b["rect"].top > ROOM_ROWS*TILE:
            bullets.remove(b)
            continue
        if any(b["rect"].colliderect(t) for t in terrain):
            bullets.remove(b)

# ------------------------
# Camera
# ------------------------
def update_camera(moving_horizontally):
    global camera_x, camera_y
    target_x = player_rect.centerx - BASE_WIDTH/2
    target_y = player_rect.centery - BASE_HEIGHT/2
    if moving_horizontally:
        target_x += camera_lead if x_velocity > 0 else -camera_lead
    camera_x += (target_x - camera_x) * camera_lerp
    camera_y += (target_y - camera_y) * camera_lerp

# ------------------------
# Map Drawing
# ------------------------
def draw_map():
    for room_id, room in room_graph.items():
        if room.visited and room_id != current_room_id:
            x = MAP_PADDING + (room_id % 10) * (MAP_SCALE + 2)
            y = MAP_PADDING + (room_id // 10) * (MAP_SCALE + 2)
            pygame.draw.rect(screen, MAP_COLOR, pygame.Rect(x, y, MAP_SCALE, MAP_SCALE))

# ------------------------
# Drawing
# ------------------------
def draw():
    screen.fill(DARK)
    for t in terrain: pygame.draw.rect(screen, WHITE, pygame.Rect((t.x-camera_x)*scale_x,(t.y-camera_y)*scale_y,t.width*scale_x,t.height*scale_y))
    for p in platforms: pygame.draw.rect(screen, PLATFORM_COLOR, pygame.Rect((p.x-camera_x)*scale_x,(p.y-camera_y)*scale_y,p.width*scale_x,p.height*scale_y))
    for d in door_coords.values(): pygame.draw.rect(screen, DOOR_COLOR, pygame.Rect((d.x-camera_x)*scale_x,(d.y-camera_y)*scale_y,d.width*scale_x,d.height*scale_y))
    pygame.draw.rect(screen, BLUE, pygame.Rect((player_rect.x-camera_x)*scale_x,(player_rect.y-camera_y)*scale_y,player_rect.width*scale_x,player_rect.height*scale_y))
    for b in bullets: pygame.draw.rect(screen, BULLET_COLOR, pygame.Rect((b["rect"].x-camera_x)*scale_x,(b["rect"].y-camera_y)*scale_y,b["rect"].width*scale_x,b["rect"].height*scale_y))
    if show_map: draw_map()

    if fade_alpha > 0:
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0,0,0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0,0))

    pygame.display.flip()

# ------------------------
# Main Loop
# ------------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: shooting = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1: shooting = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m: show_map = not show_map

    moving_horizontally = handle_input()
    move_player()
    handle_doors()
    handle_bullets()
    update_camera(moving_horizontally)
    draw()
    clock.tick(60)