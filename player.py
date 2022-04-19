import pygame
from os import walk
from support import *
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(
            topleft=pos)  # создает прямогульник по форме картинки, который используется для колизий
        self.hitbox = self.rect.inflate(0, -26)  # Возвращает новый прям-ник с размером, измененным на заданное

        # graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # movement
        self.direction = pygame.math.Vector2()  # нужно для управления персонажем
        # self.speed = 5
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.switch_duration_cooldown = 200
        self.weapon_switch_time = None

        # stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 123
        self.speed = self.stats['speed']

    def import_player_assets(self):
        character_path = 'graphics/player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
                           'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)
        # print(self.animations)

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # if keys[pygame.K_UP]:
            #     self.direction.y = -1
            # elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            #     self.direction.y = 1
            # elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            #     self.direction.x = -1
            # elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            #     self.direction.x = 1
            # else:
            #     self.direction.x = 0
            #     self.direction.y = 0

            # movement input
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            #  attack input
            if keys[pygame.K_SPACE]:
                self.direction.x = 0  # for stopping when
                self.direction.y = 0  # in attacking
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            # magic input
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print('magic')

            if keys[pygame.K_q] and self.can_switch_weapon:

                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                if self.weapon_index < len(list(weapon_data.keys())) - 1:  # check if index in range
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                self.weapon = list(weapon_data.keys())[self.weapon_index]  # change index to current one

    def get_status(self):
        # idle status
        if self.direction.x == 0 and self.direction.y == 0:  # проверяем, стоим мы или нет
            if not 'idle' in self.status and not 'attack' in self.status:  # проверяем, нет ли уже 'idle'/'attack' в статусе
                self.status = self.status + '_idle'  # если 'idle' ещё не добавлен, добавляем

        # attack status
        if self.attacking:
            self.direction.x == 0
            self.direction.y == 0
            if not 'attack' in self.status:  # см выше
                if 'idle' in self.status:
                    # если есть 'idle', то переписываем статус
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def move(self, speed):
        # поправим ускорение при диагональном перемешении из за сложения векторов
        if self.direction.magnitude() != 0:  # check length of vector (any length)
            self.direction = self.direction.normalize()  # setting the length of vector to one
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

        # self.rect.center += self.direction * speed

    def collision(self, direction):  # проверка/ослеживание столкновений
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

    def animate(self):
        animation = self.animations[self.status]
        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the img
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
