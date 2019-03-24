
# Parameters file containing mainly CONSTANTS

SCREEN_RATIO = 0.8  # Pygame screen will take 80% of the screen resolution

RIGHT = "Right"
LEFT = "Left"
UP = "Up"
DOWN = "Down"

# channel 0 (the default) is used for the main game music (unlimited loop)
# channel 1 is used for ATTACK sound
ATTACK_CHANNEL = 1
ATTACK_SOUND = 'Shoot_01.ogg'
# channel 2 is used for SPINNER sound
SPINNER_CHANNEL = 2
SPINNER_SOUND = 'Spinner_01.ogg'
# channel 3 is used for POPUP sound
POPUP_CHANNEL = 3
POPUP_SOUND = 'popup_3times.ogg'

PLAYER_HP = 10
MOB_HP = 1
# Click indexes
LEFT_CLICK = 1
RIGHT_CLICK = 3

# Types (mainly used for collision)
PLAYER_TYPE = 0
ENNEMY_TYPE = 1
RIGID_BODY = 2

# Visual Information
CHARACTER_DIMENSIONS = (150, 150)
BOSS_DIMENSION = (300, 300)
POPUP_DIMENSIONS = (150, 150)
RIGID_BODY_DIMENSIONS = (25, 25)
PROJECTILE_DIMENSIONS = (30, 30)
ARROW_DIMENSIONS = (150, 114)
ONGLET_DIMENSION = (60, 30)
JUMP_MULTIPLIER = 2.5

SPAWN_TIME = 100
# Projectile-Related info
PROJECTILE_SPEED = 3
PLAYER_ATTACK_SPEED = 0.4
# Screen related information
width, height = 200, 200
ground_width = 170

# Animation parameters
ANIMATION_TIME = 0.2

# RESOURCES
IMAGE_RESOURCES = "resources/images/"
SOUND_RESOURCES = "resources/sounds/"

# TIMERS
BOSS_TIMER = 600

VERBOSE = True

num_worker_threads = 4
