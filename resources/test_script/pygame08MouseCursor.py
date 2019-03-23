# -*- coding: utf-8 -*-
import sys, pygame

pygame.init()

infoObject = pygame.display.Info()
screen = pygame.display.set_mode((int(infoObject.current_w * 0.4), int(infoObject.current_h * 0.4)))

print("width =" + str(infoObject.current_w))
print("height=" + str(infoObject.current_h))

running = True

myblue = [25, 125, 195]
screen.fill(myblue)

pygame.mouse.set_visible(False)  # hide the cursor

# Image for "manual" cursor
mycursor = pygame.image.load('index.png').convert_alpha()
mycursor = pygame.transform.scale(mycursor, (40, 40))

# In main loop ~
while running:

  # paint cursor at mouse the current location
  #mycursor.set_alpha(opacity)  
  screen.blit(mycursor, (pygame.mouse.get_pos()))
  pygame.display.flip()
  ev = pygame.event.get()

  # proceed events
  for event in ev:

    # handle MOUSEBUTTONUP
#    if event.type == pygame.MOUSEBUTTONUP:
#      pos = pygame.mouse.get_pos()
#      print("MOUSEBUTTONUP pos=" + str(pos))
    if event.type == pygame.MOUSEBUTTONDOWN:
      pos = pygame.mouse.get_pos()
      print("MOUSEBUTTONDOWN pos=" + str(pos))
#    if event.type == pygame.MOUSEMOTION:
#      pos = pygame.mouse.get_pos()
#      print("MOUSEMOTION pos=" + str(pos))
    if event.type == pygame.QUIT:
      running = False
            
 