import pygame
import random
import sys
import os

pygame.init()
WIDTH, HEIGHT = 640, 480
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spring Hopper Ultimate")

clock = pygame.time.Clock()

# Colors
SKY_TOP = (30, 30, 60)
SKY_BOTTOM = (100, 150, 200)
WHITE = (255, 255, 255)
PLATFORM = (50, 205, 120)
SPIKE = (200, 50, 50)
STAR_COLOR = (255, 230, 100)
OUTLINE = (30, 30, 30)
PINK = (255, 105, 180)

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
state = STATE_MENU

# High score
if not os.path.exists("highscore.txt"):
    with open("highscore.txt", "w") as f:
        f.write("0")
with open("highscore.txt", "r") as f:
    high_score = int(f.read())

def draw_gradient():
    for y in range(HEIGHT):
        r = SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * y // HEIGHT
        g = SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * y // HEIGHT
        b = SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * y // HEIGHT
        pygame.draw.line(win, (r, g, b), (0, y), (WIDTH, y))

def reset_game():
    global player, vel_y, on_ground, double_jump, platforms, stars, hazards
    global scroll_x, score

    player = pygame.Rect(100, 300, 30, 30)
    vel_y = 0
    on_ground = False
    double_jump = True
    platforms = [pygame.Rect(100, 400, 100, 10), pygame.Rect(300, 320, 100, 10)]
    stars.clear()
    hazards.clear()
    scroll_x = 0
    score = 0

def draw_game():
    draw_gradient()

    for p in platforms:
        rect = p.move(-scroll_x, 0)
        pygame.draw.rect(win, OUTLINE, rect.inflate(4, 4))
        pygame.draw.rect(win, PLATFORM, rect)

    for h in hazards:
        rect = h.move(-scroll_x, 0)
        pygame.draw.rect(win, OUTLINE, rect.inflate(4, 4))
        pygame.draw.rect(win, SPIKE, rect)
        pygame.draw.polygon(win, SPIKE, [
            (rect.x, rect.y + 10),
            (rect.x + rect.width // 2, rect.y - 10),
            (rect.x + rect.width, rect.y + 10)
        ])

    for s in stars:
        r = s.move(-scroll_x, 0)
        pygame.draw.circle(win, STAR_COLOR, r.center, 7)
        pygame.draw.circle(win, OUTLINE, r.center, 8, 2)

    pr = player.move(-scroll_x, 0)
    pygame.draw.circle(win, OUTLINE, pr.center, player.width // 2 + 3)
    pygame.draw.circle(win, PINK, pr.center, player.width // 2)

    text = font.render(f"Score: {score}  High: {high_score}", True, WHITE)
    win.blit(text, (10, 10))

def spawn_platform():
    x = platforms[-1].x + random.randint(150, 220)
    y = random.randint(220, 400)
    new_platform = pygame.Rect(x, y, 100, 10)
    platforms.append(new_platform)

    if random.random() < 0.6:
        stars.append(pygame.Rect(x + random.randint(20, 70), y - 20, 14, 14))
    if random.random() < 0.3:
        hazards.append(pygame.Rect(x + random.randint(10, 80), y - 10, 30, 10))

# Game vars
player = pygame.Rect(100, 300, 30, 30)
vel_y = 0
on_ground = False
double_jump = True
platforms = [pygame.Rect(100, 400, 100, 10), pygame.Rect(300, 320, 100, 10)]
stars = []
hazards = []
scroll_x = 0
speed = 2
score = 0

# Main loop
run = True
while run:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if state == STATE_MENU and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                reset_game()
                state = STATE_PLAYING

        if state == STATE_GAMEOVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = STATE_MENU

    if state == STATE_MENU:
        draw_gradient()
        title = big_font.render("Spring Hopper", True, WHITE)
        info = font.render("Press ENTER to Play", True, WHITE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        win.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.update()
        continue

    if state == STATE_GAMEOVER:
        draw_gradient()
        over = big_font.render("Game Over", True, WHITE)
        score_txt = font.render(f"Score: {score}  High Score: {high_score}", True, WHITE)
        retry = font.render("Press ENTER to Retry", True, WHITE)
        win.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 3))
        win.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 2))
        win.blit(retry, (WIDTH // 2 - retry.get_width() // 2, HEIGHT // 2 + 40))
        pygame.display.update()
        continue

    # --- Game playing logic ---
    vel_y += 0.5
    player.y += vel_y

    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5
    if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
        if on_ground:
            vel_y = -10
            double_jump = True
        elif double_jump:
            vel_y = -9
            double_jump = False

    on_ground = False
    for p in platforms:
        rect = p.move(-scroll_x, 0)
        if player.colliderect(rect) and vel_y >= 0 and player.bottom <= rect.top + 12:
            player.bottom = rect.top
            vel_y = 0
            on_ground = True

    for h in hazards:
        rect = h.move(-scroll_x, 0)
        if player.colliderect(rect.inflate(-5, -5)):
            state = STATE_GAMEOVER
            if score > high_score:
                with open("highscore.txt", "w") as f:
                    f.write(str(score))
                    high_score = score

    for s in stars[:]:
        if player.colliderect(s.move(-scroll_x, 0)):
            stars.remove(s)
            score += 5

    if player.x - scroll_x > WIDTH // 2:
        scroll_x += speed
        score += 1

    if player.top > HEIGHT:
        state = STATE_GAMEOVER
        if score > high_score:
            with open("highscore.txt", "w") as f:
                f.write(str(score))
                high_score = score

    if platforms[-1].x - scroll_x < WIDTH + 100:
        spawn_platform()

    draw_game()
    pygame.display.update()

pygame.quit()
sys.exit()
