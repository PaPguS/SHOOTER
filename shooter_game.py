from pygame import *
from random import randint
from time import time as timer


# базовый класс для спрайтов
class GameSprite(sprite.Sprite):
    """
    image_file - имя файла с картинкой для спрайта
    x - координата x спрайта
    y - координата y спрайта
    speed - скорость спрайта
    size_x - размер спрайта по горизонтали
    size_y - размер спрайта по вертикали
    """

    def __init__(self, image_file, x, y, speed, size_x, size_y):
        super().__init__()  # конструктор суперкласса
        self.image = transform.scale(
            image.load(image_file), (size_x, size_y)
        )  # создание внешнего вида спрайта - картинки
        self.speed = speed  # скорость
        self.rect = (
            self.image.get_rect()
        )  # прозрачная подложка спрайта - физическая модель
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        # отобразить картинку спрайта в тех же координатах, что и его физическая модель
        window.blit(self.image, (self.rect.x, self.rect.y))


# класс для игрока
class Player(GameSprite):
    # метод для управления игрока стрелками клавиатуры
    def update(self):
        # получаем словарь состояний клавиш
        keys = key.get_pressed()

        # если нажата клавиша влево и физическая модель не ушла за левую границу игры
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed

        # если нажата клавиша вправо и физическая модель не ушла за правую границу игры
        if keys[K_RIGHT] and self.rect.x < width - 70:
            self.rect.x += self.speed

    # метод для стрельбы пулями
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bullet)


# класс для врагов
class Enemy(GameSprite):
    # метод для движения врага
    def update(self):
        global lost
        self.rect.y += self.speed
        if self.rect.y > height:
            self.rect.x = randint(80, width - 80)
            self.rect.y = -50
            lost += 1


# класс для пуль
class Bullet(GameSprite):
    # движение пули
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()


# размеры окна
width = 700
height = 500

# создание окна
window = display.set_mode((width, height))
display.set_caption("Space Invaders")

# названия файлов
img_back = "galaxy.jpg"  # фон игры
img_hero = "rocket.png"  # игрок
img_enemy1 = "ufo.png"  # враг 1
img_enemy2 = "asteroid.png"  # враг 2
img_bullet = "bullet.png"  # пуля

# открываем фон
background = transform.scale(image.load(img_back), (width, height))

# подключаем музыку
mixer.init()
mixer.music.load("space.ogg")  # фоновая музыка
mixer.music.play()
fire_sound = mixer.Sound("fire.ogg")  # звук выстрела

# переменная окончания игры
finish = False  # когда True, то спрайты перестают работать
# переменная завершения программы
game = True  # завершается при нажатии кнопки закрыть окно
# переменная перезарядки
reload_bullets = False  # если True - происходит перезарядка

# счетчики
score = 0  # счетчик сбитых
lost = 0  # счетчик пропущенных
max_lost = 10  # максимум пропущенных
max_score = 20  # количество очков для победы
life = 3  # количество жизней
max_bullets = 5  # максимум пуль в обойме
num_bullet = 0  # количество пуль

# шрифт
font.init()
font1 = font.SysFont("Arial", 36)
font2 = font.SysFont("Arial", 80)
win = font2.render("YOU WIN!", True, (255, 255, 255))
lose = font2.render("YOU LOSE!", True, (180, 0, 0))

# внутриигровые часы и ФПС
clock = time.Clock()
FPS = 60

# создание спрайтов
ship = Player(img_hero, 5, height - 100, 10, 80, 100)

# создание группы монстров (астероиды и НЛО)
monsters = sprite.Group()
for i in range(5):
    monster = Enemy(img_enemy1, randint(0, width - 80), -40, randint(1, 5), 80, 50)
    monsters.add(monster)

# создание группы астероидов
asteroids = sprite.Group()
for i in range(3):
    asteroid = Enemy(img_enemy2, randint(0, width - 50), -40, randint(1, 7), 50, 50)
    asteroids.add(asteroid)

bullets = sprite.Group()


# игровой цикл
while game:
    # обработка нажатия кнопки Закрыть окно
    for e in event.get():
        if e.type == QUIT:
            game = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                # проверка возможности выстрела
                if num_bullet < 5 and reload_bullets == False:
                    fire_sound.play()
                    ship.fire()
                    num_bullet += 1
                if num_bullet >= 5 and reload_bullets == False:
                    last_time = timer()
                    reload_bullets = True

    if finish != True:
        window.blit(background, (0, 0))

        text = font1.render("Счет: " + str(score), True, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font1.render("Пропущено: " + str(lost), True, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update()

        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        if reload_bullets:
            now_time = timer()
            if now_time - last_time < 3:
                reload_text = font2.render("Wait, reload...", True, (150, 0, 0))
                window.blit(reload_text, (200, 400))
            else:
                num_bullet = 0
                reload_bullets = False

        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(
            ship, asteroids, False
        ):
            sprite.spritecollide(ship, monsters, True)
            sprite.spritecollide(ship, asteroids, True)
            life -= 1

        # столкновение пуль и врагов
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(
                img_enemy1, randint(80, width - 80), -40, randint(1, 5), 80, 50
            )
            monsters.add(monster)

        # проигрыш - проверка столкновения игрока с одним врагом
        if life == 0 or lost >= max_lost:
            finish = True
            window.blit(lose, (200, 200))

        # выигрыш - набрали больше max_score очков
        if score >= max_score:
            finish = True
            window.blit(win, (200, 200))

        if life == 3:
            life_color = (0, 150, 0)
        elif life == 2:
            life_color = (150, 150, 0)
        elif life == 1:
            life_color = (150, 0, 0)

        life_text = font2.render(str(life), True, life_color)
        window.blit(life_text, (650, 10))

    else:
        finish = False
        score = 0
        lost = 0
        num_bullet = 0
        life = 3
        reload_bullets = False
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        for a in asteroids:
            a.kill()

        time.delay(3000)
        for i in range(5):
            monster = Enemy(
                img_enemy1, randint(80, width - 80), -40, randint(1, 5), 80, 50
            )
            monsters.add(monster)

        for i in range(3):
            asteroid = Enemy(
                img_enemy2, randint(0, width - 50), -40, randint(1, 7), 50, 50
            )
            asteroids.add(asteroid)

    display.update()
    clock.tick(FPS)