import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Surfers - Спрощена версія")

 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

train_width = 80
train_height = 50
train_x = WIDTH // 2 - train_width // 2
train_y = HEIGHT - train_height - 50
train_speed = 5


man_width = 50
man_height = 50
man_x = WIDTH // 2 - man_width // 2
man_y = -50
man_speed = 5


obstacles = []

coins = []


score = 0


speed = 5


lane_width = 250
lanes = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]


train_rect = pygame.Rect(train_x, train_y, train_width, train_height)

def create_obstacle():
    x = random.choice(lanes)
    y = -50
    return pygame.Rect(x, y, 50, 50) 

def create_coin():
    x = random.choice(lanes)
    y = -50
    return pygame.Rect(x, y, 20, 20)  


def create_man():
    x = random.choice(lanes)
    y = -50
    return pygame.Rect(x, y, man_width, man_height)


def draw_train(x, y):
    for i in range(3):  
        pygame.draw.rect(screen, RED, (x + i * (train_width // 3), y, train_width // 3, train_height))

def draw_man(x, y):
    pygame.draw.rect(screen, RED, (x, y, man_width, man_height))

def draw_obstacles():
    for obs in obstacles:
        pygame.draw.rect(screen, YELLOW, obs)  

def draw_coins():
    for coin in coins:
        pygame.draw.circle(screen, YELLOW, coin.center, 10) 

def check_obstacle_collision():
    global train_x, train_y
    for obs in obstacles:
        if train_rect.colliderect(obs):
            return True
    return False

def check_coin_collision():
    global score
    for coin in coins:
        if train_rect.colliderect(coin):
            coins.remove(coin)
            score += 1
            return True
    return False

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and train_x > lanes[0]:
        train_x -= lane_width
    if keys[pygame.K_RIGHT] and train_x < lanes[2]:
        train_x += lane_width

    if random.random() < 0.02:
        obstacles.append(create_obstacle())

    if random.random() < 0.05:
        coins.append(create_coin())

    if random.random() < 0.01:
        man_x = random.choice(lanes)
        man_y = -50
        man_rect = pygame.Rect(man_x, man_y, man_width, man_height)

    for obs in obstacles:
        obs.y += speed
        if obs.y > HEIGHT:  
            obs.y = -50
            obs.x = random.choice(lanes)

    for coin in coins:
        coin.y += speed
        if coin.y > HEIGHT: 
            coin.y = -50
            coin.x = random.choice(lanes)

    man_y += man_speed
    if man_y > HEIGHT:
        man_y = -50
        man_x = random.choice(lanes)

    if check_obstacle_collision():
        print("Гра завершена! Ви врезались у перешкоду!")
        running = False

    check_coin_collision()

    draw_obstacles()
    draw_coins()
    draw_train(train_x, train_y)
    draw_man(man_x, man_y)

    font = pygame.font.SysFont('Arial', 30)
    score_text = font.render(f"Бали: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
