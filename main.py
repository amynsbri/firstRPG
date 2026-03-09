import pygame
from sys import exit

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.sprite_sheet = pygame.image.load('asset/asset_1/sprites/characters/player.png').convert_alpha()

        self.width =32
        self.height = 32

        self.walking_frames = []

        for i in range(6):
            x = i * self.width
            y = 0

            cut_rect = pygame.Rect(x, y, self.width, self.height)

            frame = self.sprite_sheet.subsurface(cut_rect)
            self.walking_frames.append(frame)
        
        self.image = self.walking_frames[0]
        self.rect = self.image.get_rect(center = (500, 400))


clock = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption("My First RPG")

# Background

ground_surface = pygame.image.load('asset/asset_1/sprites/tilesets/decor_8x8.png')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

        screen.fill("white")
        

        pygame.display.flip()
    
    pygame.display.update
    clock.tick(60)

