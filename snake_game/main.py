'''
Basic implementation of Snake
Based on tutorial: https://www.youtube.com/watch?v=8dfePlONtls
'''

import pygame
from pygame.locals import *
from time import sleep
import random

SIZE = 40
WINDOW_X = 800
WINDOW_Y = 800
BG_COLOR = (123, 33, 123)
TEXT_COLOR = (0, 0, 0)
DEBUG = True

# TODO Make own resources

# TODO Make sure apple can't spawn on top of snake

# TODO Ex 1: Make boundaries wrap around

# TODO Ex 2: Menu with speed setting, starting length
# Score = length starting length

class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Basic Snake game")
        pygame.mixer.init()

        self.play_background_music("bg_music_1")

        self.font = pygame.font.SysFont('arial', 30)

        self.surface = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
        # self.surface.fill(BG_COLOR)
        self.render_background("background")

        self.snake = Snake(self.surface, 2)
        self.snake.draw()

        self.apple = Apple(self.surface)
        self.apple.draw()

    def is_collision(self, x1, y1, x2, y2):
        # if self.apple.x <= self.snake.x[0] < self.apple.x + SIZE:
        #     if self.apple.y <= self.snake.y[0] < self.apple.y + SIZE:
        if x2 <= x1 < x2 + SIZE:
            if y2 <= y1 < y2 + SIZE:
                return True
        return False

    def display_score(self, x, y):
        # score = self.font.render("TEST", True, (0, 0, 0))
        score = self.font.render(f"Score: {self.snake.length}", True, TEXT_COLOR)
        self.surface.blit(score, (x, y))

    def play_sound(self, filename):
        sound = pygame.mixer.Sound(f"resources/{filename}.mp3")
        pygame.mixer.Sound.play(sound)

    def play_background_music(self, filename):
        pygame.mixer.music.load(f"resources/{filename}.mp3")
        pygame.mixer.music.play()

    def render_background(self, filename):
        bg = pygame.image.load(f"resources/{filename}.jpg")
        self.surface.blit(bg, (0, 0))

    def play(self):
        self.render_background("background")
        self.snake.walk()
        self.apple.draw()
        self.display_score(WINDOW_X - 150, 10)
        pygame.display.flip()

        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound("ding")
            self.snake.increase_length()
            self.apple.move()

            if DEBUG:
                print("Collision")

        # TODO CHECK RANGE
        for i in range(1, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.play_sound("crash")
                if DEBUG:
                    print("Game over")
                raise "self_collision"

    def show_game_over(self):

        pygame.mixer.music.pause()

        self.render_background("background")
        # self.surface.fill(BG_COLOR)
        self.display_score(int(WINDOW_X / 4), int(WINDOW_Y / 2))
        replay_message = self.font.render("To play again press Enter. To exit press Escape", True, TEXT_COLOR)
        self.surface.blit(replay_message, (int(WINDOW_X / 4), int(WINDOW_Y / 2) + 50))
        pygame.display.flip()

    def reset(self):
        self.snake = Snake(self.surface, 2)
        self.apple = Apple(self.surface)

    def run(self):
        '''
        Game event loop
        :return:
        '''

        running = True
        pause = False
        while running:
            # self.snake.draw()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RETURN:
                        pygame.mixer.music.unpause()
                        pause = False
                    if not pause:
                        if event.key == K_UP:
                            self.snake.move_up()
                        elif event.key == K_DOWN:
                            self.snake.move_down()
                        elif event.key == K_LEFT:
                            self.snake.move_left()
                        elif event.key == K_RIGHT:
                            self.snake.move_right()
                elif event.type == QUIT:
                    running = False

            try:
                if not pause:
                    self.play()
            except Exception as e:
                pause = True
                self.show_game_over()
                self.reset()

            sleep(0.2)



class Snake:
    def __init__(self, surface, length):
        self.parent_screen = surface
        self.length = length
        self.block = pygame.image.load("resources/block.jpg").convert()
        self.x = [SIZE] * self.length
        self.y = [SIZE] * self.length
        self.direction = 'right'

    def draw(self):
        # self.parent_screen.fill(BG_COLOR)
        # self.parent_screen.render_background("background")
        for i in range(self.length):
            self.parent_screen.blit(self.block, (self.x[i], self.y[i]))
        pygame.display.flip()

    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)

    def walk(self):

        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        if self.direction == 'right':
            self.x[0] += SIZE
        elif self.direction == 'left':
            self.x[0] -= SIZE
        elif self.direction == 'up':
            self.y[0] -= SIZE
        elif self.direction == 'down':
            self.y[0] += SIZE
        self.draw()

    def move_left(self):
        if self.direction != 'right':
            self.direction = 'left'

    def move_right(self):
        if self.direction != 'left':
            self.direction = 'right'

    def move_up(self):
        if self.direction != 'down':
            self.direction = 'up'

    def move_down(self):
        if self.direction != 'up':
            self.direction = 'down'


class Apple:
    def __init__(self, surface):
        self.image = pygame.image.load("resources/apple.jpg").convert()
        self.parent_screen = surface
        self.x = None
        self.y = None
        self.move()

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))
        pygame.display.flip()

    def move(self):
        self.x = random.randint(0,int(WINDOW_X/SIZE)) * SIZE
        self.y = random.randint(0,int(WINDOW_Y/SIZE)) * SIZE


if __name__ == "__main__":
    game = Game()
    game.run()
