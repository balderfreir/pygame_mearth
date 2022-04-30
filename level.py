import pygame
from ui import *
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import *
from enemy import *


class Level:
    def __init__(self):
        # получение display surface
        self.display_surface = pygame.display.get_surface()

        # настройка группы спрайтов (https://habr.com/ru/post/588765/)
        self.visible_sprites = YSortCameraGroup()  # видимые спрайты
        self.obstacle_sprites = pygame.sprite.Group()  # спрайты препятсвия (могут взаимодействовать)

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprites setup
        self.create_map()

        # user interface
        self.ui = UI()

    def create_map(self):  # basic level setup
        layouts = {
            'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('map/map_Grass.csv'),
            'object': import_csv_layout('map/map_Objects.csv'),
            'entities': import_csv_layout('map/map_Entities.csv'),
        }
        graphics = {
            'grass': import_folder('graphics/grass'),
            'objects': import_folder('graphics/objects')
        }
        # for row_index, row in enumerate(WORLD_MAP):
        #     for col_index, col in enumerate(row):
        #         x = col_index * TITELSIZE
        #         y = row_index * TITELSIZE
        #         if col == 'X':
        #             Tile((x, y), [self.visible_sprites, self.obstacle_sprites])  # создаем/отображаем препятствие
        #         if col == 'p':
        #             self.player = Player((x, y), [self.visible_sprites],
        #                                  self.obstacle_sprites)  # создаем/отображаем игрока

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites],
                                 'invisible')  # создаем невидимые границы на карте, невидимые так как не используем self.visible_sprites
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y),
                                 [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                                 'grass', random_grass_image)  # создаем траву

                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)

                        if style == 'entities':
                            if col == '394':
                                self.player = Player((x, y),
                                                     [self.visible_sprites],
                                                     self.obstacle_sprites,
                                                     self.create_attack,  # методы передаем без ()
                                                     self.destroy_attack,
                                                     self.create_magic)  # создаем/отображаем игрока
                            else:
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'
                                Enemy(monster_name, (x, y), [self.visible_sprites, self.attackable_sprites],self.obstacle_sprites)

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])  #,self.obstacle_sprites

    def create_magic(self, style, strength, cost):
        # self.current_magic = Magic(self.player, self.visible_sprites)
        print(style)
        print(strength)
        print(cost)

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def run(self):
        # отрисовка и обновление игры
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.ui.display(self.player)

        # debug(self.player.direction)
        # debug(self.player.status)



class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # gengeral setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load('graphics/tilemap/ground.png').convert()  # загружаем изображение "земли"
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))  # получаем прямогуольник по загруженной картинке

    def custom_draw(self, player):
        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset  # определяем координаты
        self.display_surface.blit(self.floor_surf, floor_offset_pos)  # отрисовывает одну поверхность (землю) на другой

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda
                spite: spite.rect.centery):  # сортировка нужна для правильной очереди отрисовки, что бы overlap выглядил нормально
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
