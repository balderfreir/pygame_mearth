import pygame, sys
from settings import *
from level import Level


class Game:
    def __init__(self):
        # общие настройки
        pygame.init()  # команда запускает pygame
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))  # создаем окно для игры
        pygame.display.set_caption('Mearth')
        self.clock = pygame.time.Clock()  # нужен для того, чтобы убедиться, что игра работает с заданной частотой кадров
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():  # для каждоого события из списка объектов (из списска событий, которые моожет отследить pygame)
                if event.type == pygame.QUIT:  # проверяем на правдивость условие, то есть является ли событие "выходом из игры"
                    pygame.quit()  # грохает модули pygame что были инициализированы
                    sys.exit()  # грохает интерпретатор

            self.screen.fill('black')  # заполняем экран черным цветом
            self.level.run()
            pygame.display.update()  # обновляем экран
            self.clock.tick(FPS)  # контролируем длительность кадра


if __name__ == '__main__':  # проверка на фаил
    game = Game()  # если да, создаем объект класса Game
    game.run()  # вызываем метод run
