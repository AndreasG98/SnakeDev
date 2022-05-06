'''
Basic implementation of Snake
Based on tutorial: https://www.youtube.com/watch?v=8dfePlONtls
Resources taken from: https://github.com/codebasics/python_projects/tree/main/1_snake_game
'''

import pygame
from pygame.locals import *
from time import sleep
import random
from math import floor

SIZE = 40
WINDOW_X = 800
WINDOW_Y = 800
# BG_COLOR = (123, 33, 123)
TEXT_COLOR = (0, 0, 0)
SELECTED_TEXT_COLOR = (255, 0, 0)
DEBUG = False  # True


# Final todo: remove unused stuff like above variables and debug prints
# also code style and comments
# organize method order like static methods together

# TODO Features
# Portal item


def debug_print(string):
    if DEBUG:
        print(string)


class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake")
        pygame.mixer.init()

        self.tick_over = False

        # Keep track of how many ticks the game has been through
        self.runtime = 0
        self.playtime = 0

        # Menu settings
        self.selected_menu_item = "start"
        self.setting_speed = 5
        self.setting_start_length = 2

        self.play_background_music("OSRS_Scape_Santa")

        self.font = pygame.font.SysFont('arial', 30)

        self.surface = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
        self.render_background("Mosaic_Background")

        self.snake = Snake(self.surface, self.setting_start_length)
        self.snake.draw()

        self.apple = Apple(self.surface, self)
        self.draw_item(self.apple)

        # These are initialized but usually don't show up at the start
        self.bomb = Bomb(self.surface, self)

        # 2 separate portal objects are easier to manage
        self.portal_a = Portal(self.surface)
        self.portal_b = Portal(self.surface)

        self.portal_in_use = False  # Is the snake currently inside the portal?
        self.portal_use_playtime = None  # The playtime stamp when the portal was used
        self.portal_active = False  # Is there currently an active portal?
        self.portal_time_since_last = 0  # How many gameplay ticks since the last portal closed, or since the start
        self.portal_time_remaining = 0  # How many gameplay tickets until the portals close

    @staticmethod
    def is_collision(x1, y1, x2, y2):
        if x2 <= x1 < x2 + SIZE:
            if y2 <= y1 < y2 + SIZE:
                return True
        return False

    @staticmethod
    def is_collision_multiple(existing_item, count, spawn_x, spawn_y, snake=False):
        for i in range(count):
            if Game.is_collision(existing_item.x[i], existing_item.y[i], spawn_x, spawn_y):
                return True
        return False

    @staticmethod
    def play_sound(filename):
        sound = pygame.mixer.Sound(f"resources/{filename}.mp3")
        pygame.mixer.Sound.play(sound)

    @staticmethod
    def play_background_music(filename):
        pygame.mixer.music.load(f"resources/{filename}.mp3")
        pygame.mixer.music.play()

    @staticmethod
    def generate_coordinates():

        x = (random.randint(0, int(WINDOW_X / SIZE))) * SIZE
        y = (random.randint(0, int(WINDOW_Y / SIZE))) * SIZE

        # This should fix the case where an apple is placed at the upper edge of the window size
        # and is rendered off the edge of the screen
        if x >= WINDOW_X or y >= WINDOW_Y:
            x -= 40
            y -= 40

        return x, y

    def move_item(self, item, count=None):
        """
        This method changes the coordinates of an item to a random unoccupied point
        :param item: is the item to place
        :param count: is the number of items, if there are multiples
        :return: Boolean, item, count. Boolean True if success, False if there was a collision. Item and count
                 are the same as the input parameters to simplify re-running the method
        """

        # Generate coordinates, all items use the same ones
        curr_x, curr_y = self.generate_coordinates()

        # Checks if the item is colliding with the snake
        if self.is_collision_multiple(self.snake, self.snake.length, curr_x, curr_y):
            debug_print("Spawn collision between" + str(type(item)) + "and snake")
            # self.move_item(item, count)
            return False, item, count

        # Check if objects are initialized before trying to check for collision
        bomb_initialized, apple_initialized, portal_a_initialized, portal_b_initialized = self.check_object_init()

        # If the bomb has been initialized, we can check if the item collides with any existing bomb
        # We also need to make sure it has at least 1 set of coordinates
        if bomb_initialized and len(self.bomb.x) != 0 and len(self.bomb.y) != 0:
            print("Bomb arrays", self.bomb.x, self.bomb.y)
            # self.bomb.count has to have - 1 because this count includes the one we're adding now
            if self.is_collision_multiple(self.bomb, self.bomb.count - 1, curr_x, curr_y):
                debug_print("Spawn collision between" + str(type(item)) + "and bomb")
                # self.move_item(item, count)
                return False, item, count

        # If the apple has been initialized, we can check if the item collides with the apple
        if apple_initialized:
            if self.is_collision(self.apple.x, self.apple.y, curr_x, curr_y):
                debug_print("Spawn collision between" + str(type(item)) + "and apple")
                # self.move_item(item, count)
                return False, item, count

        # If portal a has been initialized, we can check if the item collides with the portal
        if portal_a_initialized:
            # The coordinates are not 'None'; They're integers
            if None not in (self.portal_a.x, self.portal_a.y, ):
                if self.is_collision(self.portal_a.x, self.portal_a.y, curr_x, curr_y):
                    debug_print("Spawn collision between" + str(type(item)) + "and portal a")
                    return False, item, count

        if portal_b_initialized:
            # The coordinates are not 'None'; They're integers
            if None not in (self.portal_b.x, self.portal_b.y, ):
                if self.is_collision(self.portal_b.x, self.portal_b.y, curr_x, curr_y):
                    debug_print("Spawn collision between" + str(type(item)) + "and portal b")
                    return False, item, count

        # Repeat of the snake collision method above
        # # Make sure the item hasn't spawned on top of the snake
        # for i in range(0, self.snake.length):
        #     # On spawn, if the apple is colliding with any snake segment it will move it again
        #     if Game.is_collision(self.snake.x[i], self.snake.y[i], curr_x, curr_y):
        #         debug_print(str(type(item)) + "spawned on snake at" + str(curr_x), str(curr_y))
        #         return False, item, count

        # If it hasn't returned by now, there are no collisions. we can set the actual item's coordinates!
        # print("Successfully got coordinates", type(item), curr_x, curr_y)
        if count is None:
            item.x = curr_x
            item.y = curr_y
        # Set only the provided index if count is provided
        elif count is not None:
            # print("Appending coordinates to item list", curr_x, curr_y)
            item.x.append(curr_x)
            item.y.append(curr_y)

        debug_print(str(type(item)) + " moved to " + str(curr_x) + str(curr_y))

        # Return True signals that it does not need to try to move the item again
        return True, item, count

    def check_object_init(self):
        """
        Checks all of the objects that may be partially or not at all initialized at the start
        :return: bomb_initialized, apple_initialized, portal_a_initialized, portal_b_initialized. Each of these is
                True if the object has been properly initialized, False if not.
        """

        # Make sure the bomb is initialized before trying to use it
        # This solves exceptions due to initialization order at startup
        try:
            self.bomb
        except AttributeError:
            bomb_initialized = False
        else:
            bomb_initialized = True

        # Make sure the apple is initialized before trying to use it
        # This solves exceptions due to initialization order at startup
        try:
            self.apple
        except AttributeError:
            apple_initialized = False
        else:
            apple_initialized = True

        # Make sure the portal is initialized before trying to use it
        # This solves exceptions due to initialization order at startup
        try:
            self.portal_a
        except AttributeError:
            portal_a_initialized = False
        else:
            portal_a_initialized = True
        try:
            self.portal_b
        except AttributeError:
            portal_b_initialized = False
        else:
            portal_b_initialized = True

        return bomb_initialized, apple_initialized, portal_a_initialized, portal_b_initialized

    def draw_item(self, item, count=None):
        # if DEBUG:
        #     print("Draw item", item, count)
        if count is None:
            # print(type(item), item.x, item.y)
            self.surface.blit(item.image, (item.x, item.y))
        else:
            debug_print("draw_item, count provided")
            # if DEBUG:
            #     print("Drawing", count, "items")
            #     print("Debug info:\n", item.x, item.y)
            for i in range(0, count):
                debug_print("draw_item, idx # " + str(i))
                self.surface.blit(item.image, (item.x[i], item.y[i]))
        pygame.display.flip()

    def display_score(self, blit_arg=None):
        score_text = self.font.render(f"Score: {self.snake.length - self.setting_start_length}", True, TEXT_COLOR)
        if blit_arg is None:
            blit_arg = score_text.get_rect(center=(WINDOW_X / 2, WINDOW_Y / 4))
        self.surface.blit(score_text, blit_arg)

    def render_background(self, filename):
        bg = pygame.image.load(f"resources/{filename}.jpg")
        self.surface.blit(bg, (0, 0))

    def menu(self):
        '''
        Displays a menu screen on launch
        :selected: Is the currently selected menu item
        :return: None
        '''

        # Background image
        self.render_background("Mosaic_Background")

        # Highlight the selected menu item
        start_color = TEXT_COLOR
        speed_color = TEXT_COLOR
        length_color = TEXT_COLOR

        if self.selected_menu_item == 'start':
            start_color = SELECTED_TEXT_COLOR
        elif self.selected_menu_item == 'speed':
            speed_color = SELECTED_TEXT_COLOR
        elif self.selected_menu_item == 'length':
            length_color = SELECTED_TEXT_COLOR

        # Title text
        title_text = self.font.render(f"Welcome to Snake!", True, TEXT_COLOR)
        self.surface.blit(title_text, title_text.get_rect(center=(WINDOW_X / 2, WINDOW_Y / 4)))

        # Need 3 selectable texts: start game, speed and start length
        start_text = self.font.render(f"Start", True, start_color)
        self.surface.blit(start_text, start_text.get_rect(center=(WINDOW_X / 2, WINDOW_Y / 2)))

        speed_setting_text = self.font.render(f"Speed: {self.setting_speed}", True, speed_color)
        self.surface.blit(speed_setting_text, speed_setting_text.get_rect(center=(WINDOW_X / 2, WINDOW_Y / 2 + 50)))

        length_setting_text = self.font.render(f"Start length: {self.setting_start_length}", True, length_color)
        self.surface.blit(length_setting_text, length_setting_text.get_rect(center=(WINDOW_X / 2, WINDOW_Y / 2 + 100)))

        pygame.display.flip()

    def spawn_portals(self, rand):
        # TODO
        print("Spawn portals")

        # The portals won't spawn this time
        if rand < 500:
            # print("Portal rand < 500", rand)
            return
        if self.portal_active:
            print("portals already active")
            return

        # Start with portal A
        result = False
        while not result:
            result, item, count = self.move_item(self.portal_a)

        # Now do portal B
        result = False
        while not result:
            result, item, count = self.move_item(self.portal_b)

        # Now that both have coordinates, draw them
        self.draw_item(self.portal_a)
        self.draw_item(self.portal_b)

        # Set portal values
        self.portal_time_since_last = 0
        self.portal_time_remaining = random.randint(0, 40) + 10
        self.portal_active = True

    def close_portals(self):

        print("Close portals")

        # If the snake is inside the portal it won't close
        # This will be called again next tick
        if self.portal_in_use:
            return False

        # Close portals and reset timers
        self.portal_a.x = None
        self.portal_a.y = None
        self.portal_b.x = None
        self.portal_b.y = None

        self.portal_active = False
        self.portal_time_remaining = 0
        self.portal_time_since_last = 0

    def check_teleport(self, util=False, idx=0):
        """
        Checks if the head of the snake has touched a portal.
        Also allows for snake body checking to see if the portal needs to remain open.

        :param util: False when checking portals, True if collision checking for portal_in_use
        :param idx: Default 0 when checking portals, the index of the snake body segment to check if for
                    portal_in_use
        :return: Returns nothing if util=False. If util=True, returns True if the segment of the snake
                    given by idx is in contact with the portal
        """

        print("Check teleport")
        if self.is_collision(self.portal_a.x, self.portal_a.y, self.snake.x[idx], self.snake.y[idx]):
            if not util:
                self.portal_in_use = True
                self.portal_use_playtime = self.playtime
                self.snake.teleported = True
                self.snake.teleported_x = self.portal_b.x
                self.snake.teleported_y = self.portal_b.y
                print("Entered portal A, going to", self.snake.teleported_x, self.snake.teleported_y)
            if util:
                return True
        elif self.is_collision(self.portal_b.x, self.portal_b.y, self.snake.x[idx], self.snake.y[idx]):
            if not util:
                self.portal_in_use = True
                self.portal_use_playtime = self.playtime
                self.snake.teleported = True
                self.snake.teleported_x = self.portal_a.x
                self.snake.teleported_y = self.portal_a.y
                print("Entered portal B, going to", self.snake.teleported_x, self.snake.teleported_y)
            if util:
                return True
        else:
            return

        if util:
            return False

        self.play_sound("OSRS_Ice_Barrage")

    def play(self):
        self.render_background("Mosaic_Background")

        self.snake.walk(self)
        self.draw_item(self.apple)
        debug_print("Successfully drew apple")
        self.display_score((WINDOW_X - 150, 10))

        # Do portal stuff here

        # print("Portal info pre:", self.snake.teleported, self.portal_in_use, self.portal_time_remaining)

        # If it's active
        if self.portal_active:
            # If time is up, close the portals
            if self.portal_time_remaining <= 0:
                if not self.close_portals():
                    print("Portal in use, unable to close.")
                else:
                    print("Successfully closed portals.")

            # If there's time left, draw them and decrement remaining time
            else:
                self.draw_item(self.portal_a)
                self.draw_item(self.portal_b)
                self.portal_time_remaining -= 1

                self.check_teleport()

        # If it's inactive, increment the amount of time since the last portal and try rng to see if they spawn
        else:
            self.portal_time_since_last += 1
            # TODO Change randint param later, 300/500 is for testing
            rand = random.randint(0, 450) + self.portal_time_since_last
            self.spawn_portals(rand)

        if self.portal_in_use:
            if not self.snake.check_segment_distance():
                self.portal_in_use = False

        # print("Portal info post:", self.portal_in_use, self.portal_time_remaining)

        # Between the score update and render, see if we need to add a bomb
        old_bomb_count = self.bomb.count
        self.bomb.count = floor(self.snake.length / 5)

        # If we need a bomb now, "move" it to initialize
        if old_bomb_count != self.bomb.count:
            # print("Bomb count > 0")
            result = False
            while not result:
                # The count has to be
                result, item, count = self.move_item(self.bomb, self.bomb.count)

        # We need to render bombs
        if self.bomb.count > 0:
            debug_print("More than 0 bombs")
            # print("Rendering bomb", self.bomb.count)
            self.draw_item(self.bomb, self.bomb.count)

            # We might as well check for bomb collision here too
            # print("Checking for bomb collision with snake. Count:", self.bomb.count)
            if self.is_collision_multiple(self.bomb, self.bomb.count, self.snake.x[0], self.snake.y[0]):
                # print("bomb collision")
                self.play_sound("OSRS_Goblin_Death")
                raise "bomb_collision"
            # print("no bomb collision")
        else:
            debug_print("No bombs to render or check or collision")

        # Display stuff
        pygame.display.flip()

        # Check for apple collision
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound("Minecraft_Eating")
            self.snake.increase_length()
            result = False
            while not result:
                result, item, count = self.move_item(self.apple)

            if DEBUG:
                print("Collision with apple at ", self.apple.x, self.apple.y)

        # Check for the snake colliding with itself
        # if not self.first_tick:
        if self.playtime > 1:
            # print("Checking self-collision at run/playtime", self.runtime, self.playtime)
            for i in range(4, self.snake.length):
                # print("Self-collision snake check", i, self.snake.length)
                if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                    self.play_sound("OSRS_Goblin_Death")
                    # if DEBUG:
                    #     print("Game over, self collision")
                    raise "self_collision"

    def show_game_over(self):

        pygame.mixer.music.pause()

        self.render_background("Mosaic_Background")
        # self.surface.fill(BG_COLOR)
        self.display_score((int(WINDOW_X / 2), int(WINDOW_Y / 4)))
        replay_message = self.font.render("Press enter to return to menu. To exit press Escape", True, TEXT_COLOR)
        self.surface.blit(replay_message, replay_message.get_rect(center=(WINDOW_X / 2, WINDOW_Y / 2)))
        pygame.display.flip()

    def reset(self):
        self.snake = Snake(self.surface, self.setting_start_length)
        self.apple = Apple(self.surface, self)

    def run(self):
        '''
        Game event loop
        :return: None
        '''

        running = True
        menu = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RETURN:
                        if menu and self.selected_menu_item == 'start':
                            # if not self.init_complete:
                            #     self.finish_init()
                            menu = False
                            print("Exited menu. Settings:", self.setting_speed, self.setting_start_length)
                            while self.snake.length < self.setting_start_length:
                                self.snake.increase_length()
                        pygame.mixer.music.unpause()
                        if pause:
                            pause = False
                            menu = True
                    if menu:
                        if event.key == K_UP:
                            if self.selected_menu_item == 'speed':
                                self.selected_menu_item = 'start'
                            elif self.selected_menu_item == 'length':
                                self.selected_menu_item = 'speed'
                        elif event.key == K_DOWN:
                            if self.selected_menu_item == 'start':
                                self.selected_menu_item = 'speed'
                            elif self.selected_menu_item == 'speed':
                                self.selected_menu_item = 'length'
                        elif event.key == K_LEFT:
                            if self.selected_menu_item == 'speed' and self.setting_speed > 1:
                                self.setting_speed -= 1
                            elif self.selected_menu_item == 'length' and self.setting_start_length > 1:
                                self.setting_start_length -= 1
                        elif event.key == K_RIGHT:
                            if self.selected_menu_item == 'speed' and self.setting_speed < 10:
                                self.setting_speed += 1
                            elif self.selected_menu_item == 'length' and self.setting_start_length < 10:
                                self.setting_start_length += 1
                    elif not pause:
                        if event.key == K_UP:
                            self.snake.move_up()
                        elif event.key == K_DOWN:
                            self.snake.move_down()
                        elif event.key == K_LEFT:
                            self.snake.move_left()
                        elif event.key == K_RIGHT:
                            self.snake.move_right()
                        elif event.key == K_q:
                            pause = True
                            menu = True
                elif event.type == QUIT:
                    running = False

            if menu:
                # print("Menu", self.selected_menu_item)
                self.menu()
            else:
                try:
                    if not pause:
                        self.playtime += 1
                        self.play()
                except (Exception,) as e:
                    if DEBUG:
                        print("Exception", e)
                    pause = True
                    # self.first_tick = True
                    self.show_game_over()
                    self.reset()

            self.runtime += 1

            sleep((10 - self.setting_speed) / 20)


class Snake:

    def __init__(self, surface, length):
        self.parent_screen = surface
        self.length = length
        self.snake_head = pygame.image.load("resources/snake_head.jpg").convert()
        self.snake_body = pygame.image.load("resources/snake_body.jpg").convert()
        self.x = []
        self.y = []
        self.direction = 'right'
        self.setup = True

        for i in range(0, self.length):
            self.increase_length()

        print("Snake length is now:", self.length)

        self.setup = False

        # If you enter a teleported, teleported becomes true and next
        # tick you will appear at the teleported x/y coordinates
        self.teleported = False
        self.teleported_x = None
        self.teleported_y = None

    def draw(self):

        # The head has a different image
        self.parent_screen.blit(self.snake_head, (self.x[0], self.y[0]))

        # Draw all the body portions
        for i in range(1, self.length):
            self.parent_screen.blit(self.snake_body, (self.x[i], self.y[i]))

        pygame.display.flip()

    def increase_length(self):

        # If this is the first part (the head)
        # Generate coordinates that aren't on the edge and apply them
        if len(self.x) == 0 and len(self.y) == 0:
            valid_coordinates = False
            start_x = None
            start_y = None
            while not valid_coordinates:
                start_x, start_y = Game.generate_coordinates()
                if (WINDOW_X - SIZE) >= start_x >= SIZE and (WINDOW_Y - SIZE) >= start_y >= SIZE:
                    valid_coordinates = True
            self.x.append(start_x)
            self.y.append(start_y)
            return

        curr_len = len(self.x)
        self.x.append(self.x[curr_len - 1])
        self.y.append(self.y[curr_len - 1])

        if not self.setup:
            self.length += 1

    def walk(self, game_instance):

        if self.teleported:
            print("Snake was teleported!")
            self.x[0] = self.teleported_x
            self.y[0] = self.teleported_y
            self.teleported = False
            game_instance.portal_in_use = True

        # Basically a linked list, just moving all the body parts to the position of the next one
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

        # This makes the snake wrap around if it reaches the edge
        self.x[0] = self.x[0] % WINDOW_X
        self.y[0] = self.y[0] % WINDOW_Y

        self.draw()

    def check_segment_distance(self):
        """
        Checks if the body is likely being teleported by looking at distance between segments
        :return:
        """

        portal_use = True

        for i in range(0, self.length - 2):
            x1 = self.x[i]
            y1 = self.y[i]

            # for j in range(1, self.length):
            x2 = self.x[i + 1]
            y2 = self.y[i + 1]

            x_diff = abs(x2 - x1)
            y_diff = abs(y2 - y1)

            if x_diff > SIZE or y_diff > SIZE:
                print("X or Y segments far away, separation:", x_diff, y_diff)
                if x1 == 0 and x2 == (WINDOW_X - SIZE):
                    print("X segments likely wrapped around")
                    portal_use = False
                elif x2 == 0 and x1 == (WINDOW_X - SIZE):
                    print("X segments likely wrapped around")
                    portal_use = False
                elif y1 == 0 and y2 == (WINDOW_Y - SIZE):
                    print("Y segments likely wrapped around")
                    portal_use = False
                elif y2 == 0 and y1 == (WINDOW_Y - SIZE):
                    print("Y segments likely wrapped around")
                    portal_use = False
                else:
                    print("Likely no wrap around, probably portal")
                    portal_use = True
                    break
        return portal_use


    # Conditionals within each move function prevents the snake from doubling back over itself

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

    def __init__(self, surface, game_instance):
        self.image = pygame.image.load("resources/OSRS_Christmas_Cracker.jpg").convert()
        self.parent_screen = surface
        self.x = None
        self.y = None

        result = False
        while not result:
            result, item, count = game_instance.move_item(self)


class Bomb:

    def __init__(self, surface, game_instance):
        self.image = pygame.image.load("resources/bomb.jpg").convert()
        self.parent_screen = surface
        self.count = 0
        self.x = []
        self.y = []


class Portal:

    def __init__(self, surface):
        self.image = pygame.image.load("resources/portal.jpg").convert()
        self.parent_screen = surface
        self.x = None
        self.y = None


if __name__ == "__main__":
    game = Game()
    game.run()
