from main import *
from parametters import *


# Draw the ground
def draw_ground():
    ground = pygame.image.load("resources/images/ground.png")
    # while width_rest > 0:
    #     x = width_rest
    #     y = height - ground_width
    #     screen.blit(ground, (x,y))
    #     width_rest -= ground_width
    for i in range(0, int(width % ground_lvl) + 1):
        x = i * ground_width
        y = height - ground_width
        screen.blit(ground, (x, y))
