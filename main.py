import threading
import time

import pygame

from character import *
from colors import *
from my_utils import *


def init_screen():
    """
    Initalize the screen with width and heigh
    :return:
    """
    pygame.init()

    infoObject = pygame.display.Info()
    width = int(infoObject.current_w * SCREEN_RATIO)
    height = int(infoObject.current_h * SCREEN_RATIO)
    screen = pygame.display.set_mode((width, height))
    if VERBOSE:
        print("width =" + str(width))
    if VERBOSE:
        print("height=" + str(height))

    return (screen, width, height)


(screen, width, height) = init_screen()

ground_lvl = height - 100

player = Character(screen=screen, name="Paladin")

while 1:

    for event in pygame.event.get():
        # check if the event is the X button
        if event.type == pygame.QUIT:
            # if it is quit the game
            pygame.quit()
            exit(0)

        # Keydown events
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                player.moving_right = True
            elif event.key == pygame.K_LEFT:
                player.moving_left = True
            elif event.key == pygame.K_UP:
                player.moving_up = True
            elif event.key == pygame.K_DOWN:
                player.moving_down = True

        # Keyup events
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                player.moving_right = False
            elif event.key == pygame.K_LEFT:
                player.moving_left = False
            elif event.key == pygame.K_UP:
                player.moving_up = False
            elif event.key == pygame.K_DOWN:
                player.moving_down = False
        # Allow attacking anytime
        if pygame.mouse.get_pressed()[0] and not player.is_attacking:
            print("Mouse doung left")
            player.is_attacking = True


            def delayed_animation():
                time.sleep(ANIMATION_TIME)
                player.is_attacking = False


            t = threading.Thread(target=delayed_animation)
            t.start()

    screen.fill(blue_sky)
    draw_ground(screen, ground_lvl=ground_lvl, ground_width=ground_width)
    player.blitme()
    player.update()

    pygame.display.flip()
