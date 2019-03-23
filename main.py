import pygame
import time
import threading
from parametters import *
from utils import *
from colors import *

def init_screen():
    """
    Initalize the screen with width and heigh
    :return:
    """
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    return screen

screen = init_screen()