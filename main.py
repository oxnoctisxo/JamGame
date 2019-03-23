import threading
import time

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


def find_spawn_point_and_spawn(spawn_points, item):
    """
    Find a spawn point avaible for the character/ennemy and spawns him
    :param spawn_points:
    :param item:
    :return:
    """
    for spawn_point in spawn_points:
        if spawn_point.can_spawn(item):
            if VERBOSE:
                print("Spawning", str(item))
            spawn_point.spawn(item)
            return True
    return False


(screen, width, height) = init_screen()

ground_lvl = height - 100

player = Character(screen=screen, name="Paladin")
player.is_active = True
player.type = PLAYER_TYPE

characters = [player, Character(screen=screen, name="Paladin")]

characters[1].add_collision_listenr(player)
for character in characters:
    character.is_active = True

spawn_points = [Spawn(screen,20, 20, orientation=LEFT,type=PLAYER_TYPE), Spawn(screen,100, 100, orientation=RIGHT)]

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
    draw_ground(screen, ground_lvl=height, ground_width=ground_width)
    # manage charaters on the screen
    for character in characters:
        if not character.spawned and character.is_active:
            find_spawn_point_and_spawn(spawn_points=spawn_points, item=character)
        if character.is_active:
            character.update()
            character.blitme()

    pygame.display.flip()
