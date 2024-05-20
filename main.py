import pygame
from pygame.locals import *
import pygame.locals
import button
import gsm
import levels.numsort as numsort
import levels.aimtrainer as aimtrainer
import levels.waste as waste
import levels.gameselect as gameselect

things = list()
SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


class Main:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GestureQuest")
        self.clock = pygame.time.Clock()
        self.gameStateManager = gsm.GameStateManager('menu')
        self.numsort = numsort.Numsort(self.screen, self.gameStateManager)
        self.waste = waste.Waste(self.screen, self.gameStateManager)
        self.menu = Menu(self.screen, self.gameStateManager)
        self.aimtrainer = aimtrainer.AimTrainer(self.screen, self.gameStateManager)
        self.gameselect = gameselect.GameSelect(self.screen, self.gameStateManager)
        self.states = {'numsort':self.numsort, 'menu':self.menu, 'aimtrainer':self.aimtrainer, 'waste':self.waste, 'gameselect':self.gameselect}
    
    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                
            self.states[self.gameStateManager.get_state()].run()
            pygame.display.update()
            # print("MAIN RUNNING")
            self.clock.tick(144)

        self.cap.release()
        pygame.quit()

class Menu:
    def __init__(self,screen,gameStateManager):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.bg = pygame.image.load('assets/Menu/bg.png').convert_alpha()
        self.title = pygame.image.load('assets/Menu/title.png').convert_alpha()
        self.title_button = button.Button(self.screen, 85, 220, self.title, 1)
        self.play_img = pygame.image.load('assets/Menu/PLAY.png').convert_alpha()
        self.exit_img = pygame.image.load('assets/Menu/EXIT.png').convert_alpha()
        self.score_img = pygame.image.load('assets/Menu/SCORE.png').convert_alpha()
        self.play_button = button.Button(self.screen, 870, 200, self.play_img, 1.5)
        self.exit_button = button.Button(self.screen, 870, 400, self.exit_img, 1.5)
        self.score_button = button.Button(self.screen, 600, 600, self.score_img, 0.3)
        self.started = True
        self.flag = 0
    def run(self):
        self.screen.blit(self.bg, (-400, -200))
        self.title_button.draw()
        if self.play_button.draw() and self.started == False:
            self.gameStateManager.set_state('gameselect')
            self.flag = 1
        if self.exit_button.draw() and self.started == False:
            pygame.quit()
        # self.score_button.draw()
        self.started = False
        if self.flag == 1:
            self.started = True
            self.flag = 0

if __name__ == "__main__":
    main = Main()
    main.run()