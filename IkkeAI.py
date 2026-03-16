import pygame
import sys

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
bullets = []



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
        
    # Fire bullet
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            bullet_x = square_x + square_size
            bullet_y = square_y + square_size // 2 - bullet_height // 2
            bullets.append([bullet_x, bullet_y])

    # Move bullets
    for bullet in bullets[:]:
        bullet[0] += bullet_speed
        if bullet[0] > WIDTH:
            bullets.remove(bullet)


    # Draw
    screen.fill(DARK)

    # Ground
    pygame.draw.rect(screen, WHITE, (0, ground_y, WIDTH, HEIGHT - ground_y))

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
            (bullet[0], bullet[1], bullet_width, bullet_height)
    )
        
    

    pygame.display.flip()
    clock.tick(60)
