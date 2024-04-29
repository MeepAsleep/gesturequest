import pygame
from pygame.locals import *
import pygame.locals
import button
import gsm
import levels.numsort as numsort

things = list()
SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 786

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SortQuest")
        self.clock = pygame.time.Clock()
        self.gameStateManager = gsm.GameStateManager('menu')
        self.numsort = numsort.Numsort(self.screen, self.gameStateManager)
        self.menu = Menu(self.screen, self.gameStateManager)
        self.states = {'numsort':self.numsort, 'menu':self.menu}
    
    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                
            self.states[self.gameStateManager.get_state()].run()
            pygame.display.update()
            self.clock.tick(144)

        self.cap.release()
        pygame.quit()

class Menu:
    def __init__(self,screen,gameStateManager):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.play_img = pygame.image.load('assets/PLAY.png').convert_alpha()
        self.exit_img = pygame.image.load('assets/EXIT.png').convert_alpha()
        self.score_img = pygame.image.load('assets/SCORE.png').convert_alpha()
    def run(self):
        self.screen.fill('black')
        play_button = button.Button(self.screen, 600, 300, self.play_img, 0.3)
        exit_button = button.Button(self.screen, 600, 450, self.exit_img, 0.3)
        score_button = button.Button(self.screen, 600, 600, self.score_img, 0.3)
        if play_button.draw():
            self.gameStateManager.set_state('numsort')
        if exit_button.draw():
            self.cap.release()
            pygame.quit()
        # score_button.draw()

if __name__ == "__main__":
    main = Main()
    main.run()