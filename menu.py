# menu.py

import pygame
import sys

class Menu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        # 动画帧列表（3张帧图片）
        self.background_frames = [pygame.image.load(f"{i}.png") for i in range(1, 4)]
        self.current_frame = 0
        self.frame_count = len(self.background_frames)
        self.frame_timer = 0
        self.frame_duration = 4000000  # 每一帧持续时间 (毫秒)

        self.play_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 3 + 40, 200, 70)
        self.quit_button_rect = pygame.Rect(self.width // 2 - 100, self.height // 2 + 40, 200, 70)
        self.font = pygame.font.Font(None, 60)

    def draw_text(self, text, color, rect):
        text_obj = self.font.render(text, True, color)
        text_rect = text_obj.get_rect(center=rect.center)
        self.screen.blit(text_obj, text_rect)

    def draw_button(self, mouse_pos):
        # Play button with border

        if self.play_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (46, 139, 87), self.play_button_rect)
            pygame.draw.rect(self.screen, (0, 100, 0), self.play_button_rect.inflate(15, 15), 5)  # 黄色边框
        else:
            pygame.draw.rect(self.screen, (170, 72, 46), self.play_button_rect)
            pygame.draw.rect(self.screen, (140, 54, 28), self.play_button_rect.inflate(15, 15), 5)  # 黄色边框
        self.draw_text("PLAY", (255, 255, 255), self.play_button_rect)

        # Quit button with border

        if self.quit_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (46, 139, 87), self.quit_button_rect)
            pygame.draw.rect(self.screen, (0, 100, 0), self.quit_button_rect.inflate(15, 15), 5)  # 红色边框
        else:
            pygame.draw.rect(self.screen, (170, 72, 46), self.quit_button_rect)
            pygame.draw.rect(self.screen, (140, 54, 28), self.quit_button_rect.inflate(15, 15), 5)  # 红色边框
        self.draw_text("QUIT", (255, 255, 255), self.quit_button_rect)

    def update_background(self):
        # 控制帧的变化，逐帧循环显示
        self.frame_timer += pygame.time.get_ticks() % self.frame_duration
        if self.frame_timer > self.frame_duration:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % self.frame_count

    def draw_background(self):
        # 绘制当前帧作为背景
        current_background = self.background_frames[self.current_frame]
        self.screen.blit(pygame.transform.scale(current_background, (self.width, self.height)), (0, 0))

    def run_menu(self, start_game_callback):
        while True:
            self.update_background()

            self.screen.fill((170, 170, 170))
            self.draw_background()

            mouse_pos = pygame.mouse.get_pos()

            self.draw_button(mouse_pos)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button_rect.collidepoint(mouse_pos):
                        start_game_callback()  # Call the game loop
                    if self.quit_button_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
