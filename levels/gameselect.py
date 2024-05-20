import pygame
from pygame.locals import *
import button

BLACK = (50, 50, 50)

class GameSelect:
    def __init__(self, screen, gameStateManager):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.at_image = pygame.image.load("assets/Gameselect/aimtrainer.png").convert_alpha()
        self.ws_image = pygame.image.load("assets/Gameselect/waste.png").convert_alpha()
        self.ns_image = pygame.image.load("assets/Gameselect/numsort.png").convert_alpha()
        self.back_image = pygame.image.load("assets/Gameselect/back.jpg").convert_alpha()
        self.aimtrainer = button.Button(self.screen, 180, 200, self.at_image, 1)
        self.waste = button.Button(self.screen, 580, 200, self.ws_image, 1)
        self.numsort = button.Button(self.screen, 980, 200, self.ns_image, 0.648)
        self.back = button.Button(self.screen, 20, 20, self.back_image, 0.1)
        self.headfont = pygame.font.SysFont("Roboto", 68)
        self.font = pygame.font.SysFont("Impact", 36)
        self.at_text = self.font.render("AIM-TRAINER", True, (255, 255, 255))
        self.ws_text = self.font.render("RECYCLE-RIGHT", True, (255, 255, 255))
        self.ns_text = self.font.render("NUMBER-SORT", True, (255, 255, 255))
        self.main_text = self.headfont.render("CHOOSE A GAME", True, (255, 255, 255))
        self.started = True
        self.flag = 0

    def run(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.main_text, (500, 80))
        self.screen.blit(self.at_text, (220, 500))
        self.screen.blit(self.ws_text, (610, 500))
        self.screen.blit(self.ns_text, (1010, 500))
        if self.aimtrainer.draw() and self.started == False:
            self.gameStateManager.set_state('aimtrainer')
            self.flag = 1
        if self.waste.draw() and self.started == False:
            self.gameStateManager.set_state('waste')
            self.flag = 1
        if self.numsort.draw() and self.started == False:
            self.gameStateManager.set_state('numsort')
            self.flag = 1
        self.started = False
        if self.flag == 1:
            self.flag = 0
            self.started = True
        if self.back.draw() and self.started == False:
            self.started = True
            self.gameStateManager.set_state('menu')