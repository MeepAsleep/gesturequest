import pygame
import random
import math
import button
import cv2
import mediapipe as mp


class AimTrainer:
    def __init__(self, screen, gameStateManager):
        self.screen = screen
        self.gameStateManager = gameStateManager
        self.WIDTH, self.HEIGHT = 1366, 768
        self.clock = pygame.time.Clock()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 786)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1366)

        self.pointer_pos = [1366 // 2, 768 // 2]
        self.pointer_smoothing_factor = 0.5
        self.pointer_speed = 0.1

        self.GREY = (128, 128, 128)
        self.LIGHT_BLUE = (173, 216, 245)
        self.GREEN = (0, 255, 0)

        self.target_radius = 30
        self.score = 0
        self.font = pygame.font.Font(None, 36)

        self.timer_font = pygame.font.Font(None, 48)
        self.end_font = pygame.font.SysFont("Roboto", 80)
        self.time_limit = 30
        self.start_time = None

        self.target_x = random.randint(self.target_radius + 200, self.WIDTH - self.target_radius - 200)
        self.target_y = random.randint(self.target_radius + 200, self.HEIGHT - self.target_radius - 200)

        self.restart_image = pygame.image.load("assets/Aimtrainer/replay.jpg").convert_alpha()
        self.exit_image = pygame.image.load("assets/Aimtrainer/exit.jpg").convert_alpha()
        self.restart_button = button.Button(self.screen, 620, 550, self.restart_image, 0.32)
        self.exit_button = button.Button(self.screen, 630, 640, self.exit_image, 0.25)

        self.ix = self.WIDTH//2
        self.iy = self.HEIGHT//2

        self.pinching = False
        self.running = True
        self.game_over = False
        self.temp = False


    def is_pinching(self,hand_landmarks):
        self.thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        self.index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        self.thumb_tip_x, self.thumb_tip_y = self.thumb_tip.x, self.thumb_tip.y
        self.index_tip_x, self.index_tip_y = self.index_tip.x, self.index_tip.y
        
        self.distance = ((self.thumb_tip_x - self.index_tip_x) ** 2 + (self.thumb_tip_y - self.index_tip_y) ** 2) ** 0.5
        
        if self.distance < 0.1:
            if not self.pinching:
                self.pinching = True
                return True
        else:
            self.pinching = False
        return False

    def handle_events(self):
        self.ret, self.frame = self.cap.read()
        self.frame = cv2.flip(self.frame, 1)
        self.frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(self.frame_rgb)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]

            self.index_finger = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            self.ix, self.iy = int(self.index_finger.x * self.frame.shape[1]), int(self.index_finger.y * self.frame.shape[0])
            
            desired_pos = (self.ix, self.iy)

            self.pointer_pos[0] += int((desired_pos[0] - self.pointer_pos[0]) * self.pointer_smoothing_factor)
            self.pointer_pos[1] += int((desired_pos[1] - self.pointer_pos[1]) * self.pointer_smoothing_factor)

            if self.is_pinching(hand_landmarks) and not self.game_over:
                distance = math.sqrt((self.pointer_pos[0] - self.target_x) ** 2 + (self.pointer_pos[1] - self.target_y) ** 2)
                if distance < self.target_radius:
                    if self.start_time is None:
                        self.start_time = pygame.time.get_ticks()
                    self.score += 1
                    self.target_x = random.randint(self.target_radius + 200, self.WIDTH - self.target_radius - 200)
                    self.target_y = random.randint(self.target_radius + 200, self.HEIGHT - self.target_radius - 200)
            

    def update(self):
        self.screen.fill(self.GREY)

        if not self.game_over:
            pygame.draw.circle(self.screen, self.LIGHT_BLUE, (self.target_x, self.target_y), self.target_radius)

        pygame.draw.circle(self.screen, self.GREEN, (self.ix, self.iy), 5)

        score_text = self.font.render("Score: " + str(self.score), True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        if self.start_time is not None:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.start_time) // 2000
            remaining_time = max(self.time_limit - elapsed_time, 0)
            timer_text = self.timer_font.render("Time: " + str(remaining_time), True, (0, 0, 0))
            self.screen.blit(timer_text, (self.WIDTH - 130, 10))

            if remaining_time <= 0:
                self.game_over = True
                self.show_final_score()
                self.running = False
                
        pygame.display.flip()

    def show_final_score(self):
        self.screen.fill(self.GREY)
        final_score_text = self.end_font.render("SCORE: " + str(self.score), True, (0, 0, 0))
        self.screen.blit(final_score_text, (self.WIDTH // 2 - 70, self.HEIGHT // 2 - 100))

    def restart_game(self):
        self.running = True
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.target_x = random.randint(self.target_radius + 200, self.WIDTH - self.target_radius - 200)
        self.target_y = random.randint(self.target_radius + 200, self.HEIGHT - self.target_radius - 200)
        self.game_over = False

    def run(self):
        if self.running == False and self.temp == True:
            self.__init__(self.screen, self.gameStateManager)
            self.temp = False
        while self.running:
            self.handle_events()
            self.update()
        if self.restart_button.draw():
            self.restart_game()
        if self.exit_button.draw():
            self.gameStateManager.set_state("menu")
            self.temp = True
        
