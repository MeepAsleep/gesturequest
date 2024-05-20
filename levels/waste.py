import pygame
import mediapipe as mp
import cv2
import random
import button

things = []

LIGHT_SKY_BLUE = (135, 206, 250)

class Things:
    def __init__(self, screen, id, x, y, image, scale, type):
        self.id = id
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = self.image = pygame.transform.scale(image, (int(self.width * scale), int(self.height * scale)))
        self.screen = screen
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.type = type
        
    def draw(self):
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

class Waste:
    def __init__(self, screen, gameStateManager):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.images = [pygame.image.load(f"assets/Waste/{i}.jpg").convert_alpha() for i in range(6, 10)]
        self.organic = pygame.image.load("assets/Waste/organic.png").convert_alpha()
        self.plastic = pygame.image.load("assets/Waste/plastic.png").convert_alpha()
        self.submit = pygame.image.load("assets/Waste/submit.png").convert_alpha()
        self.replay = pygame.image.load("assets/Waste/replay.jpg").convert_alpha()
        self.exit = pygame.image.load("assets/Waste/exit.jpg").convert_alpha()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 786)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1366)

        self.start_time = pygame.time.get_ticks()
        self.pointer_pos = [1366 // 2, 768 // 2]
        self.pointer_velocity = [0, 0]
        self.pointer_smoothing_factor = 0.5
        self.score = 0
        self.temptype = None
        
        self.organic_instance = Things(self.screen, 1, 350, 450, self.organic, 0.6, None)
        self.plastic_instance = Things(self.screen, 2, 900, 450, self.plastic, 0.6, None)
        l = [6, 7, 8, 9]
        count = 0
        for i, img in enumerate(self.images, 1):
            j = random.choice(l)
            k=j-5
            if count == 0 or count == 1:
                self.temptype = "plastic"
            else:
                self.temptype = "organic"
            thing = Things(self.screen, i, k*280 - 50, 145, img, 0.8, self.temptype)
            things.append(thing)
            l.remove(j)
            count+=1

        self.replay_button = button.Button(self.screen, 620, 550, self.replay, 0.33)
        self.exit_button = button.Button(self.screen, 630, 640, self.exit, 0.25)
        self.submit_button = button.Button(self.screen, 1220, 20, self.submit, 0.25)

        self.selected = False
        self.running = True
        self.started = True


    def is_pinching(self,hand_landmarks):
        self.thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        self.index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        self.thumb_tip_x, self.thumb_tip_y = self.thumb_tip.x, self.thumb_tip.y
        self.index_tip_x, self.index_tip_y = self.index_tip.x, self.index_tip.y
        
        self.distance = ((self.thumb_tip_x - self.index_tip_x) ** 2 + (self.thumb_tip_y - self.index_tip_y) ** 2) ** 0.5
        
        return self.distance < 0.1
    

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
                                
                                if abs(self.selected.rect.x - self.organic_instance.rect.x) < self.organic_instance.width//2 and \
                                    abs(self.selected.rect.y - self.organic_instance.rect.y) < self.organic_instance.height//2:
                                    if self.selected.type == "organic":
                                        self.score += 100
                                        print(self.selected.type)
                                    else:
                                        self.score -= 50
                                        print(self.selected.type)
                                    self.selected.rect.x = 2000
                                    self.selected.rect.y = 2000

                                if abs(self.selected.rect.x - self.plastic_instance.rect.x) < self.plastic_instance.width//2 and \
                                    abs(self.selected.rect.y - self.plastic_instance.rect.y) < self.plastic_instance.height//2:
                                    if self.selected.type == "plastic":
                                        self.score += 100
                                        print(self.selected.type)
                                    else:
                                        self.score -= 50
                                        print(self.selected.type)
                                    self.selected.rect.x = 2000
                                    self.selected.rect.y = 2000

                                break

            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame = pygame.image.frombuffer(self.frame.tobytes(), self.frame.shape[1::-1], "RGB")
            
            self.frame = pygame.transform.scale(self.frame, (1366, 768))
            
            self.screen.fill(LIGHT_SKY_BLUE)

            pygame.draw.circle(self.screen, (0, 255, 0), self.pointer_pos, 5)
            
            for thing in things:
                thing.draw()

            self.organic_instance.draw()
            self.plastic_instance.draw()

            if self.submit_button.draw():
                self.end_time = pygame.time.get_ticks()
                self.score = max(self.score-(self.end_time - self.start_time)//800, 0)
                self.gameover()
        
            pygame.draw.circle(self.screen, (0, 255, 0), self.pointer_pos, 5)
        else:
            self.gameover()

    def gameover(self):
        self.running = False
        self.screen.fill((LIGHT_SKY_BLUE))
        self.font = pygame.font.SysFont("Impact", 66)
        self.g_over = self.font.render("GAME OVER", True, (255, 255, 255))
        self.s_dis = self.font.render("SCORE:"+str(self.score), True, (255, 255, 255))
        self.screen.blit(self.g_over, (540, 220))
        self.screen.blit(self.s_dis, (545, 320))
        if self.replay_button.draw():
            self.reset()
        if self.exit_button.draw():
            self.gameStateManager.set_state("menu")
            self.started = True

    def reset(self):
        self.screen.fill((255, 255, 255))
        while things:
            things.pop()
        self.__init__(self.screen, self.gameStateManager)