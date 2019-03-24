from character import *
from my_utils import *
import os


def play_normal_sound():
    pygame.mixer.music.load(SOUND_RESOURCES + 'idle.ogg')
    pygame.mixer.music.play(-1)


def play_popup_sound():
    print("PopUp sound")
    popup_sound = pygame.mixer.Sound(SOUND_RESOURCES + POPUP_SOUND)
    pygame.mixer.Channel(POPUP_CHANNEL).play(popup_sound)
    pass


def init_screen():
    """
    Initialize the screen with width and height
    :return:
    """
    if VERBOSE:
        print("os.name = ", os.name)
    x = 60
    y = 60
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    infoObject = pygame.display.Info()
    width = int(infoObject.current_w * SCREEN_RATIO)
    height = int(infoObject.current_h * SCREEN_RATIO)
    screen = pygame.display.set_mode((width, height))
    if VERBOSE:
        print("width = " + str(width) + " Ratio = " + str(SCREEN_RATIO))
    if VERBOSE:
        print("height = " + str(height))

    pygame.display.set_caption('*** Clickb8 ***')
    pv_image = pygame.image.load(IMAGE_RESOURCES + 'onglet_bw.png')
    pv_image = pygame.transform.scale(pv_image, ONGLET_DIMENSION)
    inital_pv_x, inital_pv_y = 30, 20
    pvs = [(inital_pv_x + (ONGLET_DIMENSION[0] * i), inital_pv_y) for i in range(0, PLAYER_HP + 1)]
    return (screen, width, height, pv_image, pvs)


def find_spawn_point_and_spawn(spawn_points, item):
    """
    Find a spawn point available for the character/enemy and spawns him
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


(screen, width, height, pv_image, pvs) = init_screen()

pop_up_cache = pygame.image.load(IMAGE_RESOURCES + "popup_bw.png")
pop_up_cache = pygame.transform.scale(pop_up_cache, (width, height))


# Draw the ground
def draw_ground(screen):
    rigid_bodies = []
    positions = [(0, height), (427, 519 + 27)]  # (83, 712)
    i = 0
    for x, y in positions:
        dimension = (width * 2, 30) if i == 0 else (int(width / 2.55), 25) if i == 1 else RIGID_BODY_DIMENSIONS

        rigid_body = RigidBody(screen, x, y, filename="transparent",
                               dimension=dimension)
        screen.blit(rigid_body.image, (x, y))
        rigid_bodies.append(rigid_body)
        i += 1
    return rigid_bodies


clock = pygame.time.Clock()
ground_lvl = height - 100

player = Hero(screen=screen, name="Paladin", is_forward=False)
player.is_active = True
player.type = PLAYER_TYPE

rigid_bodies = draw_ground(screen)
player.rigid_bodies.extend(rigid_bodies)

# Mouse management

pygame.mouse.set_visible(False)  # hide the cursor

# Image for "manual" cursor
mycursor = pygame.image.load(IMAGE_RESOURCES + 'target.png')
mycursor = pygame.transform.scale(mycursor, (40, 40))
background = pygame.image.load(IMAGE_RESOURCES + 'background.png')
background = pygame.transform.scale(background, (width, height))

boss = Boss(screen, player)
boss.set_active(True)
boss.rigid_bodies.append(rigid_bodies[0])
# Subscribe Boss and Player to each other's projectiles
player.collision_listeners = boss.projectiles
boss.collision_listeners  = player.projectiles
characters = [player, boss]

ennemies = [Ennemy(screen)] * 1

for ennemy in ennemies:
    ennemy.is_active = True
    ennemy.rigid_bodies.extend(rigid_bodies)
    ennemy.jump()

spawn_points = [Spawn(screen, width / 2, height / 2, orientation=LEFT, type=PLAYER_TYPE)
    , Spawn(screen, 0, 0, orientation=RIGHT, type=ENNEMY_TYPE)
    , Spawn(screen, 0, 0, orientation=RIGHT, type=ENNEMY_TYPE, is_for_boss=True)
                ]

# AI management
ais = []
ais.append(EnnemyBehavior(ennemies))
ais.append(EnemyAIBoss(boss))

# Non owned Projectiles management ( could be particles )
projectiles = []

characters[1].add_collision_listenr(player)
# Add collision detection
for rigid_body in rigid_bodies:
    characters[1].add_collision_listenr(player)


def look_toward_the_mouse(player):
    (m_x, m_y) = pygame.mouse.get_pos()
    player.orientation = RIGHT if player.rect.centerx < m_x else LEFT


show_popup = False

while 1:
    clock.tick(60)  # 60 FPS (frames per second)

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
            ##elif event.key == pygame.K_UP or event.key == pygame.K_w:
            ##player.move_up(False)
            # print("not jumping")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if not player.is_jumping:
                    player.move_down(False)

        # Allow attacking anytime
        if pygame.mouse.get_pressed()[0] and not player.is_attacking:
            player.is_attacking = True
            print("Mouse: ", pygame.mouse.get_pos())
        if not pygame.mouse.get_pressed()[0] and player.is_attacking:
            player.is_attacking = False

    screen.blit(background, (0, 0))
    # High likely possible to have a popup every 10 seconds
    before = show_popup
    show_popup = True if show_popup else rand.randint(0, 40 * 60) == 7
    # If it popped up
    if before == False and show_popup == True:
        play_popup_sound()
    if not show_popup:
        for rigid_body in rigid_bodies:
            rigid_body.blitme()
        # Orient player toward the mouse
        look_toward_the_mouse(player)
        for ai in ais:
            ai.update()
        # manage characters on the screen
        for character in (characters + ennemies):
            if not character.spawned and character.is_active:
                find_spawn_point_and_spawn(spawn_points=spawn_points, item=character)
            if character.is_active:
                character.update()
                character.blitme()
                for projectile in character.projectiles:
                    projectile.update()
                    projectile.blitme()

        ennemies_computed = False


        def compute_ennemies():
            for ennemy in ennemies:
                ennemy.collision_listeners = player.projectiles
                ennemy.update()
                ennemy.blitme()
                ennemies_computed = True


        def print_pv():
            for i in range(0, player.hp + 1):
                x, y = pvs[i]
                screen.blit(pv_image, (x, y))


        compute_ennemies()
        print_pv()
    else:
        press = False
        screen.blit(pop_up_cache, (0, 0))
        # Click at the right top
        press = False if pygame.mouse.get_pressed()[0] else 0.83 * width < pygame.mouse.get_pos()[0] < width and 0 < \
                                                            pygame.mouse.get_pos()[1] < 0.18 * height
        if press:
            print("pressed")
            show_popup = False
    # q = queue.Queue()
    #
    #
    # def do_work(func):
    #     func()
    #
    #
    # def worker():
    #     while True:
    #         item = q.get()
    #         if item is None:
    #             break
    #         do_work(item)
    #         q.task_done()
    #
    #
    # threads = []
    # for i in range(num_worker_threads):
    #     t = threading.Thread(target=worker)
    #     t.start()
    #     threads.append(t)
    #
    # for item in [compute_ennemies()]:
    #     q.put(item)
    #
    # # block until all tasks are done
    # q.join()
    #
    # # stop workers
    # for i in range(num_worker_threads):
    #     q.put(None)
    # for t in threads:
    #     t.join()
    screen.blit(mycursor, (pygame.mouse.get_pos()))
    pygame.display.flip()
