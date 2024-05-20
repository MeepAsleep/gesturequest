import pygame
import mediapipe as mp
import cv2
import random
import button

things = []
slots = []

class Things:
    def __init__(self, screen, id, x, y, image, scale):
        self.id = id
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = self.image = pygame.transform.scale(image, (int(self.width * scale), int(self.height * scale)))
        self.screen = screen
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def draw(self):
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

class Numsort:
    def __init__(self, screen, gameStateManager):
        self.screen = screen
        self.gameStateManager = gameStateManager

        self.submit = pygame.image.load("assets/Numsort/submit.png").convert_alpha()
        self.images = [pygame.image.load(f"assets/Numsort/{i}.jpg").convert_alpha() for i in range(1, 6)]
        self.restart = pygame.image.load("assets/Numsort/replay.jpg").convert_alpha()
        self.exit = pygame.image.load("assets/Numsort/exit.jpg").convert_alpha()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 786)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1366)

        self.pointer_pos = [1366 // 2, 768 // 2]
        self.pointer_velocity = [0, 0]
        self.pointer_smoothing_factor = 0.5

        self.font = pygame.font.Font(None, 60)
        self.smallfont = pygame.font.Font(None, 40)
        self.win_text = self.font.render("SORT SUCCESS", True, (0, 0, 0))
        self.loss_text = self.font.render("SORT FAILED", True, (0, 0, 0))

        self.restart_button = button.Button(self.screen, 620, 550, self.restart, 0.32)
        self.exit_button = button.Button(self.screen, 630, 640, self.exit, 0.25)
        
        self.score = 0
        
        l = [1, 2, 3, 4, 5]
        for i, img in enumerate(self.images, 1):
            j = random.choice(l)
            thing = Things(self.screen, j, j * 200, 200, img, 0.6)
            things.append(thing)
            l.remove(j)

        self.greyimg = pygame.image.load("assets/Numsort/grey.jpg").convert_alpha()

        for i in range(5):
            slot = Things(self.screen, i, (i+1)*200, 400, self.greyimg, 0.6)
            slots.append(slot)

        self.submit_button = button.Button(self.screen, 1220, 20, self.submit, 0.25)
        
        self.selected = False
        self.running = True
        self.started = True
        self.checked = False


    def is_pinching(self,hand_landmarks):
        self.thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        self.index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        self.thumb_tip_x, self.thumb_tip_y = self.thumb_tip.x, self.thumb_tip.y
        self.index_tip_x, self.index_tip_y = self.index_tip.x, self.index_tip.y
        
        self.distance = ((self.thumb_tip_x - self.index_tip_x) ** 2 + (self.thumb_tip_y - self.index_tip_y) ** 2) ** 0.5
        
        return self.distance < 0.1
    
    def check_win(self):
        checklist = list()
        sortlist = list()

        for i in range(5):
            self.score += ((things[i].rect.x - slots[i].rect.x)**2 + (things[i].rect.y - slots[i].rect.y)**2)**0.5

        self.score = self.score // 3
        print(self.score)
        self.score = max(1000 - self.score, 0)

        for thing in things:
            checklist.append(thing.rect.x)
        for item in checklist:
            sortlist.append(item)
        sortlist.sort()
        if sortlist == checklist:
            return True
        return False

    def run(self):

        if self.started == True:
            self.reset()
            self.started = False
        if self.running == True:
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                print("Failed to capture frame.")
                return
            
            self.frame = cv2.flip(self.frame, 1)
            self.frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.results = self.hands.process(self.frame_rgb)
            
            if self.results.multi_hand_landmarks:
                for hand_landmarks in self.results.multi_hand_landmarks:
                    self.index_finger = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    self.ix, self.iy = int(self.index_finger.x * self.frame.shape[1]), int(self.index_finger.y * self.frame.shape[0])
                    
                    self.pointer_velocity[0] = (self.ix - self.pointer_pos[0]) * self.pointer_smoothing_factor
                    self.pointer_velocity[1] = (self.iy - self.pointer_pos[1]) * self.pointer_smoothing_factor
                    
                    self.pointer_pos[0] += int(self.pointer_velocity[0])
                    self.pointer_pos[1] += int(self.pointer_velocity[1])
                    
                    cv2.circle(self.frame, (self.ix, self.iy), 5, (0, 255, 0), -1)
                    self.selected = False
                    if self.is_pinching(hand_landmarks):
                        for thing in things:
                            if (thing.rect.x < self.ix < thing.rect.x + thing.width) and \
                            (thing.rect.y < self.iy < thing.rect.y + thing.height):
                                self.selected = thing
                                self.selected.rect.x = self.pointer_pos[0] - (self.selected.width // 2)
                                self.selected.rect.y = self.pointer_pos[1] - (self.selected.height // 2)
                                break

            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame = pygame.image.frombuffer(self.frame.tobytes(), self.frame.shape[1::-1], "RGB")
            
            self.frame = pygame.transform.scale(self.frame, (1366, 768))
            
            self.screen.fill((136, 205, 250))

            pygame.draw.circle(self.screen, (0, 255, 0), self.pointer_pos, 5)
            
            for slot in slots:
                slot.draw()
            
            for thing in things:
                thing.draw()

            pygame.draw.circle(self.screen, (0, 255, 0), self.pointer_pos, 5)

            if self.submit_button.draw():
                self.gameover()

        else:
                self.gameover()
    
    def gameover(self):
        self.running = False
        self.screen.fill((136, 205, 250))
        
        if self.checked == False:
            if self.check_win():
                self.cond = True
            else:
                self.cond = False
                self.score = 0
            self.checked = True
        if self.cond:
                self.screen.blit(self.win_text, (600, 200))
        else:
                self.screen.blit(self.loss_text, (600, 200))


        self.score = max(self.score, 0)
        self.score_text = self.smallfont.render("SCORE: "+str(self.score), True, (255, 255, 255))
        self.screen.blit(self.score_text, (660, 300))

        if self.restart_button.draw():
            self.reset()
        if self.exit_button.draw():
            self.gameStateManager.set_state("menu")
            self.started = True
            self.checked = False

            

    def reset(self):
        self.screen.fill((136, 205, 250))
        while things:
            things.pop()
        while slots:
            slots.pop()
        self.score = 0
        self.__init__(self.screen, self.gameStateManager)