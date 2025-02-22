import pygame
import random

# Ініціалізація Pygame
pygame.init()

# Встановлення параметрів екрану та кольорів
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Surfers - Спрощена версія")

# Кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Гравець (Потяг)
train_width = 80
train_height = 50
train_x = WIDTH // 2 - train_width // 2
train_y = HEIGHT - train_height - 50
train_speed = 5

# Мужик з собакою
man_width = 50
man_height = 50
man_x = WIDTH // 2 - man_width // 2
man_y = -50
man_speed = 5

# Перешкоди
obstacles = []

# Монети
coins = []

# Лічильник балів
score = 0

# Швидкість гри
speed = 5

# Механіка зміни смуги
lane_width = 250
lanes = [WIDTH // 4, WIDTH // 2, 3 * WIDTH // 4]

# Потяг
train_rect = pygame.Rect(train_x, train_y, train_width, train_height)

# Створення перешкод
def create_obstacle():
    x = random.choice(lanes)
    y = -50
    return pygame.Rect(x, y, 50, 50)  # Перешкода - малий квадрат (жовтий)

# Створення монети
def create_coin():
    x = random.choice(lanes)
    y = -50
    return pygame.Rect(x, y, 20, 20)  # Монета - маленьке коло

# Створення мужика з собакою
def create_man():
    x = random.choice(lanes)
    y = -50
    return pygame.Rect(x, y, man_width, man_height)

# Малювання потяга
def draw_train(x, y):
    for i in range(3):  # Потяг складається з 3-х червоних квадратів
        pygame.draw.rect(screen, RED, (x + i * (train_width // 3), y, train_width // 3, train_height))

# Малювання мужика з собакою
def draw_man(x, y):
    pygame.draw.rect(screen, RED, (x, y, man_width, man_height))

# Малювання перешкод
def draw_obstacles():
    for obs in obstacles:
        pygame.draw.rect(screen, YELLOW, obs)  # Малюємо перешкоди жовтими прямокутниками

# Малювання монет
def draw_coins():
    for coin in coins:
        pygame.draw.circle(screen, YELLOW, coin.center, 10)  # Малюємо монети як жовті кола

# Перевірка зіткнення з перешкодами
def check_obstacle_collision():
    global train_x, train_y
    for obs in obstacles:
        if train_rect.colliderect(obs):
            return True
    return False

# Перевірка зіткнення з монетою
def check_coin_collision():
    global score
    for coin in coins:
        if train_rect.colliderect(coin):
            coins.remove(coin)
            score += 1
            return True
    return False

# Головний цикл гри
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)  # Залити екран чорним

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Рух потяга між смугами
    if keys[pygame.K_LEFT] and train_x > lanes[0]:
        train_x -= lane_width
    if keys[pygame.K_RIGHT] and train_x < lanes[2]:
        train_x += lane_width

    # Створення перешкод, монет та мужика з собакою
    if random.random() < 0.02:
        obstacles.append(create_obstacle())

    if random.random() < 0.05:
        coins.append(create_coin())

    if random.random() < 0.01:
        man_x = random.choice(lanes)
        man_y = -50
        man_rect = pygame.Rect(man_x, man_y, man_width, man_height)

    # Рух перешкод, монет та мужика з собакою
    for obs in obstacles:
        obs.y += speed
        if obs.y > HEIGHT:  # Якщо перешкода виходить за межі екрану, повертаємо її на верх
            obs.y = -50
            obs.x = random.choice(lanes)

    for coin in coins:
        coin.y += speed
        if coin.y > HEIGHT:  # Якщо монета виходить за межі екрану, повертаємо її на верх
            coin.y = -50
            coin.x = random.choice(lanes)

    man_y += man_speed
    if man_y > HEIGHT:
        man_y = -50
        man_x = random.choice(lanes)

    # Перевірка зіткнення з перешкодами
    if check_obstacle_collision():
        print("Гра завершена! Ви врезались у перешкоду!")
        running = False

    # Перевірка зіткнення з монетою
    check_coin_collision()

    # Малювання елементів гри
    draw_obstacles()
    draw_coins()
    draw_train(train_x, train_y)
    draw_man(man_x, man_y)

    # Малюємо лічильник балів
    font = pygame.font.SysFont('Arial', 30)
    score_text = font.render(f"Бали: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Оновлюємо екран і контролюємо FPS
    pygame.display.flip()
    clock.tick(60)  # 60 кадрів на секунду

pygame.quit()
