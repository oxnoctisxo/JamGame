from parametters import *

import pygame

# Draw the ground
def draw_ground(screen,ground_lvl=0,ground_width=0):
    ground = pygame.image.load("resources/images/ground.png")
    for i in range(0, int(width % ground_lvl) + 1):
        x = i * ground_width
        y = height - ground_width
        screen.blit(ground, (x, y))
