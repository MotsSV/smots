from pygame import *
from pygame.locals import *
from random import randint

init()
mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60 
TANK_SPEED = 3
BULLET_SPEED = 5
BULLET_COOLDOWN = 500
MAX_BULLETS = 3
RELOAD_TIME = 2000
INITIAL_HP = 100
DAMAGE_PER_SHOT = 25

fire_sound = mixer.Sound("assets/music/fire.ogg")
explosion_sound = mixer.Sound("assets/music/explosion.ogg")
engine_sound = mixer.Sound("assets/music/engine.ogg")
mixer.music.load("assets/music/battle.ogg")
mixer.music.play(-1)

RED = (200, 0, 0)
BLUE = (0, 0, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 200, 0)

window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Tank Battle")
clock = time.Clock()

font_main = font.Font(None, 80)
font_small = font.Font(None, 36)

tank_red = transform.scale(image.load("assets/pictures/tank_red.png"), (50, 50))
tank_blue = transform.scale(image.load("assets/pictures/tank_blue.png"), (50, 50))
bullet_img = transform.scale(image.load("assets/pictures/bullet.png"), (10, 10))
bg = transform.scale(image.load("assets/pictures/bg.jpg"), (WIDTH, HEIGHT))

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def main_menu():
    while True:
        window.fill(BLACK)
        draw_text("Головне меню", font_main, WHITE, window, WIDTH // 2, 100)

        mx, my = mouse.get_pos()

        button_play = Rect(WIDTH // 2 - 100, 200, 200, 50)
        button_settings = Rect(WIDTH // 2 - 100, 300, 200, 50)
        button_quit = Rect(WIDTH // 2 - 100, 400, 200, 50)

        draw.rect(window, GREEN if button_play.collidepoint((mx, my)) else GRAY, button_play)
        draw.rect(window, GREEN if button_settings.collidepoint((mx, my)) else GRAY, button_settings)
        draw.rect(window, GREEN if button_quit.collidepoint((mx, my)) else GRAY, button_quit)

        draw_text("Грати", font_small, BLACK, window, WIDTH // 2, 225)
        draw_text("Налаштування", font_small, BLACK, window, WIDTH // 2, 325)
        draw_text("Вихід", font_small, BLACK, window, WIDTH // 2, 425)

        for e in event.get():
            if e.type == QUIT:
                quit()
            if e.type == MOUSEBUTTONDOWN:
                if button_play.collidepoint((mx, my)):
                    return "play"
                if button_settings.collidepoint((mx, my)):
                    return "settings"
                if button_quit.collidepoint((mx, my)):
                    quit()

        display.update()
        clock.tick(FPS)

def settings_menu():
    global FPS
    slider = Rect(WIDTH // 2 - 100, 200, 200, 20)
    slider_knob = Rect(WIDTH // 2 - 10, 190, 20, 40)
    fps_value = FPS
    dragging = False  # Флаг, указывающий, что ползунок перемещается

    while True:
        window.fill(BLACK)
        draw_text("Налаштування", font_main, WHITE, window, WIDTH // 2, 100)

        mx, my = mouse.get_pos()
        mb = mouse.get_pressed()

        draw.rect(window, GRAY, slider)
        draw.rect(window, GREEN if slider_knob.collidepoint((mx, my)) or dragging else WHITE, slider_knob)

        if mb[0]:
            if slider_knob.collidepoint((mx, my)) or dragging:
                dragging = True
                slider_knob.x = mx - 10
                if slider_knob.x < slider.x:
                    slider_knob.x = slider.x
                if slider_knob.x > slider.x + slider.width - slider_knob.width:
                    slider_knob.x = slider.x + slider.width - slider_knob.width
                fps_value = int((slider_knob.x - slider.x) / slider.width * 1620 + 30)  # 1458 = 1488 - 30
        else:
            dragging = False

        draw_text(f"FPS: {fps_value}", font_small, WHITE, window, WIDTH // 2, 250)

        button_back = Rect(WIDTH // 2 - 100, 400, 200, 50)
        draw.rect(window, GREEN if button_back.collidepoint((mx, my)) else GRAY, button_back)
        draw_text("Назад", font_small, BLACK, window, WIDTH // 2, 425)

        for e in event.get():
            if e.type == QUIT:
                quit()
            if e.type == MOUSEBUTTONDOWN:
                if button_back.collidepoint((mx, my)):
                    return fps_value

        display.update()
        clock.tick(FPS)

def get_player_name(prompt):
    input_box = Rect(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 50)
    name = ""
    active = True
    while active:
        window.fill(BLACK)
        text = font_main.render(prompt, True, WHITE)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
        draw.rect(window, WHITE, input_box, 2)
        name_text = font_main.render(name, True, WHITE)
        window.blit(name_text, (input_box.x + 10, input_box.y + 10))

        for e in event.get():
            if e.type == QUIT:
                quit()
            if e.type == KEYDOWN:
                if e.key == K_RETURN and name:
                    active = False
                elif e.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 6:
                    name += e.unicode

        display.update()
        clock.tick(FPS)

    return name

def choose_game_mode():
    button_1 = Rect(WIDTH // 2 - 200, HEIGHT // 2 - 50, 180, 60)
    button_3 = Rect(WIDTH // 2 + 20, HEIGHT // 2 - 50, 180, 60)

    selected = None
    while selected is None:
        window.fill(BLACK)
        text = font_main.render("Вибери режим:", True, WHITE)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 150))

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
        self.angle = 0
        self.hp = INITIAL_HP

    def update(self):
        keys = key.get_pressed()
        if keys[self.controls["up"]] and self.rect.y > 5:
            self.rect.y -= self.speed
            self.angle = 0
        if keys[self.controls["down"]] and self.rect.y < HEIGHT - 55:
            self.rect.y += self.speed
            self.angle = 180
        if keys[self.controls["left"]] and self.rect.x > 5:
            self.rect.x -= self.speed
            self.angle = 90
        if keys[self.controls["right"]] and self.rect.x < WIDTH - 55:
            self.rect.x += self.speed
            self.angle = 270

        self.image = transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

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

class Bullet(sprite.Sprite):
    def __init__(self, x, y, color, angle):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
        self.angle = angle
        self.color = color
        self.direction = self.calculate_direction()

    def calculate_direction(self):
        if self.angle == 0:
            return (0, -1)
        elif self.angle == 180:
            return (0, 1)
        elif self.angle == 90:
            return (-1, 0)
        elif self.angle == 270:
            return (1, 0)

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

class Explosion(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = transform.scale(image.load("assets/explosion/simple_explosion.png"), (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 30

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

controls_p1 = {"up": K_w, "down": K_s, "left": K_a, "right": K_d, "shoot": K_SPACE}
controls_p2 = {"up": K_UP, "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT, "shoot": K_RSHIFT}

player1_score = 0
player2_score = 0

while True:
    menu_action = main_menu()
    if menu_action == "play":
        player1_name = get_player_name("Гравець 1:")
        player2_name = get_player_name("Гравець 2:")
        rounds_to_win = choose_game_mode()

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

                window.blit(bg, (0, 0))
                players.draw(window)
                bullets.draw(window)
                explosions.draw(window)

                if player1.reloading:
                    reload_text = font_small.render("Reloading...", True, WHITE)
                    window.blit(reload_text, (player1.rect.x, player1.rect.y - 20))
                if player2.reloading:
                    reload_text = font_small.render("Reloading...", True, WHITE)
                    window.blit(reload_text, (player2.rect.x, player2.rect.y - 20))

                hp_text_p1 = font_small.render(f"{player1_name}: {player1.hp} HP", True, WHITE)
                hp_text_p2 = font_small.render(f"{player2_name}: {player2.hp} HP", True, WHITE)
                window.blit(hp_text_p1, (20, 10))
                window.blit(hp_text_p2, (WIDTH - hp_text_p2.get_width() - 20, 10))

                score_text = font_small.render(f"Рахунок: {player1_score} : {player2_score}", True, WHITE)
                window.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

                for bullet in bullets:
                    if bullet.color == "blue" and sprite.collide_rect(bullet, player1):
                        player1.hp -= DAMAGE_PER_SHOT
                        explosion = Explosion(player1.rect.centerx, player1.rect.centery)
                        explosions.add(explosion)
                        explosion_sound.play()
                        bullet.kill()
                        if player1.hp <= 0:
                            player2_score += 1
                            game_over = True
                    elif bullet.color == "red" and sprite.collide_rect(bullet, player2):
                        player2.hp -= DAMAGE_PER_SHOT
                        explosion = Explosion(player2.rect.centerx, player2.rect.centery)
                        explosions.add(explosion)
                        explosion_sound.play()
                        bullet.kill()
                        if player2.hp <= 0:
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

            player1.hp = INITIAL_HP
            player2.hp = INITIAL_HP
            player1.rect.center = (200, HEIGHT - 80)
            player2.rect.center = (WIDTH - 200, 30)

        window.fill(BLACK)
        window.blit(font_main.render("GAME OVER", True, WHITE), (WIDTH // 2 - 150, 100))
        window.blit(font_main.render(f"Winner: {winner}", True, WHITE), (WIDTH // 2 - 150, 200))
        window.blit(font_small.render(f"{player1_name}: {player1_score}", True, WHITE), (WIDTH // 2 - 150, 300))
        window.blit(font_small.render(f"{player2_name}: {player2_score}", True, WHITE), (WIDTH // 2 - 150, 350))
        display.update()
        time.delay(5000)

    elif menu_action == "settings":
        FPS = settings_menu()
    elif menu_action == "quit":
        quit()
