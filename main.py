import threading
import time

from character import *
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


# Draw the ground
def draw_ground(screen):
    rigid_bodies = []
    positions = [(0, height), (83, 712)]
    i = 0
    for x, y in positions:
        rigid_body = RigidBody(screen, x, y, filename="transparent",
                               dimension=(width * 2, 30) if i == 0 else RIGID_BODY_DIMENSIONS)
        screen.blit(rigid_body.image, (x, y))
        rigid_bodies.append(rigid_body)
        i += 1
    return rigid_bodies


clock = pygame.time.Clock()
ground_lvl = height - 100

player = Character(screen=screen, name="Paladin")
player.is_active = True
player.type = PLAYER_TYPE

# Mouse management

pygame.mouse.set_visible(False)  # hide the cursor

# Image for "manual" cursor
mycursor = pygame.image.load(IMAGE_RESOURCES + 'target.png')
mycursor = pygame.transform.scale(mycursor, (40, 40))
background = pygame.image.load(IMAGE_RESOURCES + 'background.png')
background = pygame.transform.scale(background, (width, height))
characters = [player, Character(screen=screen, name="Paladin")]

ennemies = [Character(screen, name="Ennmy1")]

# for character in characters:
# character.is_active = True

spawn_points = [Spawn(screen, 20, 20, orientation=LEFT, type=PLAYER_TYPE), Spawn(screen, 100, 100, orientation=RIGHT)]
rigid_bodies = draw_ground(screen)
player.rigid_bodies.extend(rigid_bodies)

characters[1].add_collision_listenr(player)
# Add colistion detection
for rigid_body in rigid_bodies:
    characters[1].add_collision_listenr(player)


def look_toward_the_mouse(player):
    (m_x, m_y) = pygame.mouse.get_pos()
    player.orientation = RIGHT if player.rect.centerx < m_x else LEFT


while 1:
    clock.tick(120)

    for event in pygame.event.get():
        # check if the event is the X button
        if event.type == pygame.QUIT:
            # if it is quit the game
            pygame.quit()
            exit(0)

        # Keydown events
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.move_right()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.move_left()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                player.jump()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if not player.is_jumping:
                    player.move_down()

        # Keyup events
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.move_right(False)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.move_left(False)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                ##player.move_up(False)
                print("not jumping")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if not player.is_jumping:
                    player.move_down(False)

        # Allow attacking anytime
        if pygame.mouse.get_pressed()[0] and not player.is_attacking:
            mouse_pos = pygame.mouse.get_pos()
            if VERBOSE:
                print("Mouse down left")
                print("MOUSEBUTTONDOWN pos=" + str(mouse_pos))
            player.is_attacking = True


            def delayed_animation():
                time.sleep(ANIMATION_TIME)
                player.is_attacking = False


            t = threading.Thread(target=delayed_animation)
            t.start()

    screen.blit(background, (0, 0))
    for rigid_body in rigid_bodies:
        rigid_body.blitme()
    # Orient player toward the mouse
    look_toward_the_mouse(player)
    # manage charaters on the screen
    for character in characters:
        if not character.spawned and character.is_active:
            find_spawn_point_and_spawn(spawn_points=spawn_points, item=character)
        if character.is_active:
            character.update()
            character.blitme()

    screen.blit(mycursor, (pygame.mouse.get_pos()))
    pygame.display.flip()
