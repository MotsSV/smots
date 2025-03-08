from pygame import *
from random import randint

# Ініціалізація Pygame
init()
mixer.init()

# Константи
WIDTH, HEIGHT = 800, 600
FPS = 60
TANK_SPEED = 3
BULLET_SPEED = 5
BULLET_COOLDOWN = 500  # мілісекунди
MAX_BULLETS = 3  # Макс. кількість куль перед перезарядкою
RELOAD_TIME = 2000  # Час перезарядки (мс)

# Завантаження музики та звуків
fire_sound = mixer.Sound("assets/music/fire.ogg")
mixer.music.load("assets/music/battle.ogg")
mixer.music.play(-1)

# Кольори
RED = (200, 0, 0)
BLUE = (0, 0, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Вікно
window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Tank Battle")
clock = time.Clock()

# Шрифти
font_main = font.Font(None, 80)
font_small = font.Font(None, 36)

# Завантаження зображень
tank_red = transform.scale(image.load("assets/pictures/tank_red.png"), (50, 50))
tank_blue = transform.scale(image.load("assets/pictures/tank_blue.png"), (50, 50))
bullet_img = transform.scale(image.load("assets/pictures/bullet.png"), (10, 10))
bg = transform.scale(image.load("assets/pictures/bg.jpg"), (WIDTH, HEIGHT))

# Функція для введення імені гравця
def get_player_name(prompt):
    input_box = Rect(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 40)
    name = ""
    active = True
    while active:
        window.fill(BLACK)
        text = font_main.render(prompt, True, WHITE)
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
        draw.rect(window, WHITE, input_box, 2)  # Виправлено тут
        name_text = font_main.render(name, True, WHITE)
        window.blit(name_text, (input_box.x + 5, input_box.y + 5))

        for e in event.get():
            if e.type == QUIT:
                quit()
            if e.type == KEYDOWN:
                if e.key == K_RETURN and name:
                    active = False
                elif e.key == K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += e.unicode

        display.update()
        clock.tick(FPS)

    return name

# Функція вибору режиму гри
def choose_game_mode():
    button_1 = Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 180, 60)  # Збільшили ширину кнопки
    button_3 = Rect(WIDTH//2 + 30, HEIGHT//2 - 50, 180, 60)   # Збільшили ширину кнопки

    selected = None
    while selected is None:
        window.fill(BLACK)
        text = font_main.render("Вибери режим:", True, WHITE)
        window.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 150))

        draw.rect(window, GRAY, button_1)
        draw.rect(window, GRAY, button_3)

        # Розміщуємо текст з самого лівого краю кнопки
        text_1 = font_main.render("До 1", True, BLACK)
        text_3 = font_main.render("До 3", True, BLACK)
        window.blit(text_1, (button_1.x + 10, button_1.y + 10))  # Текст починається зліва
        window.blit(text_3, (button_3.x + 10, button_3.y + 10))  # Текст починається зліва

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

# Отримання даних від гравців
player1_name = get_player_name("Гравець 1:")
player2_name = get_player_name("Гравець 2:")
rounds_to_win = choose_game_mode()

# Клас танка
class Tank(sprite.Sprite):
    def __init__(self, x, y, color, controls):
        super().__init__()
        self.image = tank_red if color == "red" else tank_blue
        self.rect = self.image.get_rect(center=(x, y))
        self.color = color
        self.controls = controls
        self.speed = TANK_SPEED
        self.last_shot = 0
        self.bullet_count = MAX_BULLETS
        self.reloading = False
        self.reload_start = 0

    def update(self):
        keys = key.get_pressed()
        if keys[self.controls["up"]] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[self.controls["down"]] and self.rect.y < HEIGHT - 55:
            self.rect.y += self.speed
        if keys[self.controls["left"]] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[self.controls["right"]] and self.rect.x < WIDTH - 55:
            self.rect.x += self.speed
        
        # Перевірка перезарядки
        if self.reloading and time.get_ticks() - self.reload_start > RELOAD_TIME:
            self.bullet_count = MAX_BULLETS
            self.reloading = False

    def fire(self):
        now = time.get_ticks()
        if now - self.last_shot > BULLET_COOLDOWN and self.bullet_count > 0 and not self.reloading:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.y, self.color)
            bullets.add(bullet)
            fire_sound.play()
            self.bullet_count -= 1
            if self.bullet_count == 0:
                self.reloading = True
                self.reload_start = time.get_ticks()

# Клас кулі
class Bullet(sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -BULLET_SPEED if color == "red" else BULLET_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Контролери гравців
controls_p1 = {"up": K_w, "down": K_s, "left": K_a, "right": K_d, "shoot": K_SPACE}
controls_p2 = {"up": K_UP, "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT, "shoot": K_RETURN}

# Лічильник перемог
player1_score = 0
player2_score = 0

# Основний цикл гри
running = True
while running:
    player1 = Tank(200, HEIGHT - 80, "red", controls_p1)
    player2 = Tank(WIDTH - 200, 30, "blue", controls_p2)
    players = sprite.Group(player1, player2)
    bullets = sprite.Group()
    
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

        # Оновлення спрайтів
        players.update()
        bullets.update()

        # Малювання всього на екрані
        window.blit(bg, (0, 0))
        players.draw(window)
        bullets.draw(window)

        # Перевірка зіткнень
        if sprite.spritecollide(player1, bullets, True):
            player2_score += 1
            game_over = True
        if sprite.spritecollide(player2, bullets, True):
            player1_score += 1
            game_over = True

        display.update()
        clock.tick(FPS)

    if player1_score >= rounds_to_win:
        winner = player1_name
        running = False
    elif player2_score >= rounds_to_win:
        winner = player2_name
        running = False

# Екран перемоги
window.fill(BLACK)
window.blit(font_main.render("WIN", True, WHITE), (350, 200))
window.blit(font_main.render(winner, True, WHITE), (350, 300))
display.update()
time.delay(3000)

quit()
