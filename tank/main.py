from pygame import *
from random import randint

# Initialize Pygame and mixer
init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TANK_SPEED = 3
BULLET_SPEED = 5  # Швидкість пулі
BULLET_COOLDOWN = 500  # Затримка між пострілами
MAX_BULLETS = 3  # Максимальна кількість пуль
RELOAD_TIME = 2000  # Час перезарядки

# Load sounds
fire_sound = mixer.Sound("assets/music/fire.ogg")
explosion_sound = mixer.Sound("assets/music/explosion.ogg")
engine_sound = mixer.Sound("assets/music/engine.ogg")
mixer.music.load("assets/music/battle.ogg")
mixer.music.play(-1)

# Colors
RED = (200, 0, 0)
BLUE = (0, 0, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Initialize window
window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Tank Battle")
clock = time.Clock()

# Fonts
font_main = font.Font(None, 80)
font_small = font.Font(None, 36)

# Load images
tank_red = transform.scale(image.load("assets/pictures/tank_red.png"), (50, 50))
tank_blue = transform.scale(image.load("assets/pictures/tank_blue.png"), (50, 50))
bullet_img = transform.scale(image.load("assets/pictures/bullet.png"), (10, 10))
bg = transform.scale(image.load("assets/pictures/bg.jpg"), (WIDTH, HEIGHT))

# Function to get player name
def get_player_name(prompt):
    input_box = Rect(WIDTH//2 - 150, HEIGHT//2 - 20, 300, 50)  # Larger input box
    name = ""
    active = True
    while active:
        window.fill(BLACK)
        text = font_main.render(prompt, True, WHITE)
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
        draw.rect(window, WHITE, input_box, 2) 
        name_text = font_main.render(name, True, WHITE)
        window.blit(name_text, (input_box.x + 10, input_box.y + 10))  # Adjusted text position

        for e in event.get():
            if e.type == QUIT:
                quit()
            if e.type == KEYDOWN:
                if e.key == K_RETURN and name:
                    active = False
                elif e.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 6:  # Limit name to 6 characters
                    name += e.unicode

        display.update()
        clock.tick(FPS)

    return name

# Function to choose game mode
def choose_game_mode():
    button_1 = Rect(WIDTH//2 - 200, HEIGHT//2 - 50, 180, 60)  # Adjusted button position
    button_3 = Rect(WIDTH//2 + 20, HEIGHT//2 - 50, 180, 60)  # Increased spacing between buttons

    selected = None
    while selected is None:
        window.fill(BLACK)
        text = font_main.render("Вибери режим:", True, WHITE)
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 150))

        draw.rect(window, GRAY, button_1)
        draw.rect(window, GRAY, button_3)

        text_1 = font_main.render("До 1", True, BLACK)
        text_3 = font_main.render("До 3", True, BLACK)
        window.blit(text_1, (button_1.x + 50, button_1.y + 10)) 
        window.blit(text_3, (button_3.x + 50, button_3.y + 10)) 

        for e in event.get():
            if e.type == QUIT:
                quit()
            if e.type == MOUSEBUTTONDOWN:
                if button_1.collidepoint(e.pos):
                    selected = 1
                if button_3.collidepoint(e.pos):
                    selected = 3

        display.update()
        clock.tick(FPS)

    return selected

# Tank class
class Tank(sprite.Sprite):
    def __init__(self, x, y, color, controls):
        super().__init__()
        self.original_image = tank_red if color == "red" else tank_blue
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.color = color
        self.controls = controls
        self.speed = TANK_SPEED
        self.last_shot = 0
        self.bullet_count = MAX_BULLETS
        self.reloading = False
        self.reload_start = 0
        self.angle = 0  # Угол поворота танка

    def update(self):
        keys = key.get_pressed()
        if keys[self.controls["up"]] and self.rect.y > 5:
            self.rect.y -= self.speed
            self.angle = 0  # Поворот вверх
        if keys[self.controls["down"]] and self.rect.y < HEIGHT - 55:
            self.rect.y += self.speed
            self.angle = 180  # Поворот вниз
        if keys[self.controls["left"]] and self.rect.x > 5:
            self.rect.x -= self.speed
            self.angle = 90  # Поворот вліво
        if keys[self.controls["right"]] and self.rect.x < WIDTH - 55:
            self.rect.x += self.speed
            self.angle = 270  # Поворот вправо
        
        # Поворот изображения танка
        self.image = transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Логика перезарядки
        if self.reloading and time.get_ticks() - self.reload_start > RELOAD_TIME:
            self.bullet_count = MAX_BULLETS
            self.reloading = False

    def fire(self):
        now = time.get_ticks()
        if now - self.last_shot > BULLET_COOLDOWN and self.bullet_count > 0 and not self.reloading:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.color, self.angle)
            bullets.add(bullet)
            fire_sound.play()
            self.bullet_count -= 1
            if self.bullet_count == 0:
                self.reloading = True
                self.reload_start = time.get_ticks()

# Bullet class
class Bullet(sprite.Sprite):
    def __init__(self, x, y, color, angle):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
        self.angle = angle  # Угол направления пули
        self.direction = self.calculate_direction()

    def calculate_direction(self):
        # Рассчитываем направление пули на основе угла
        if self.angle == 0:
            return (0, -1)  # Вверх
        elif self.angle == 180:
            return (0, 1)  # Вниз
        elif self.angle == 90:
            return (-1, 0)  # Вліво
        elif self.angle == 270:
            return (1, 0)  # Вправо

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

# Explosion class
class Explosion(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = transform.scale(image.load("assets/explosion/simple_explosion.png"), (50, 50))  # Просте зображення вибуху
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 30  # Час життя вибуху (у кадрах)

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# Player controls
controls_p1 = {"up": K_w, "down": K_s, "left": K_a, "right": K_d, "shoot": K_SPACE}
controls_p2 = {"up": K_UP, "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT, "shoot": K_RSHIFT}

# Initialize scores
player1_score = 0
player2_score = 0

# Отримуємо імена гравців та режим гри
player1_name = get_player_name("Гравець 1:")
player2_name = get_player_name("Гравець 2:")
rounds_to_win = choose_game_mode()

# Основной игровой цикл
running = True
while running:
    player1 = Tank(200, HEIGHT - 80, "red", controls_p1)
    player2 = Tank(WIDTH - 200, 30, "blue", controls_p2)
    players = sprite.Group(player1, player2)
    bullets = sprite.Group()
    explosions = sprite.Group()
    
    game_over = False
    while not game_over:
        for e in event.get():
            if e.type == QUIT:
                quit()
            elif e.type == KEYDOWN:
                if e.key == controls_p1["shoot"]:
                    player1.fire()
                if e.key == controls_p2["shoot"]:
                    player2.fire()

        players.update()
        bullets.update()
        explosions.update()

        # Малюємо все на екрані
        window.blit(bg, (0, 0))
        players.draw(window)
        bullets.draw(window)
        explosions.draw(window)

        # Відображення статусу перезарядки
        if player1.reloading:
            reload_text = font_small.render("Reloading...", True, WHITE)
            window.blit(reload_text, (player1.rect.x, player1.rect.y - 20))
        if player2.reloading:
            reload_text = font_small.render("Reloading...", True, WHITE)
            window.blit(reload_text, (player2.rect.x, player2.rect.y - 20))

        # Відображення рахунку
        score_text = font_small.render(f"{player1_name}: {player1_score}  {player2_name}: {player2_score}", True, WHITE)
        window.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        # Перевірка на зіткнення
        if sprite.spritecollide(player1, bullets, True):
            player2_score += 1
            explosion = Explosion(player1.rect.centerx, player1.rect.centery)
            explosions.add(explosion)
            explosion_sound.play()
            game_over = True
        if sprite.spritecollide(player2, bullets, True):
            player1_score += 1
            explosion = Explosion(player2.rect.centerx, player2.rect.centery)
            explosions.add(explosion)
            explosion_sound.play()
            game_over = True

        display.update()
        clock.tick(FPS)

    # Перевірка на переможця
    if player1_score >= rounds_to_win:
        winner = player1_name
        running = False
    elif player2_score >= rounds_to_win:
        winner = player2_name
        running = False

    # Скидання танків до початкових позицій для наступного раунду
    player1.rect.center = (200, HEIGHT - 80)
    player2.rect.center = (WIDTH - 200, 30)

# Екран завершення гри
window.fill(BLACK)
window.blit(font_main.render("GAME OVER", True, WHITE), (WIDTH // 2 - 150, 100))
window.blit(font_main.render(f"Winner: {winner}", True, WHITE), (WIDTH // 2 - 150, 200))
window.blit(font_small.render(f"{player1_name}: {player1_score}", True, WHITE), (WIDTH // 2 - 150, 300))
window.blit(font_small.render(f"{player2_name}: {player2_score}", True, WHITE), (WIDTH // 2 - 150, 350))
display.update()
time.delay(5000)  # Затримка 5 секунд

quit()
