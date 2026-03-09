import pygame
from sys import exit

class StaticItem(pygame.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sheet = pygame.image.load('asset/asset_1/sprites/characters/player.png')

        # 1. Define Animations (x, y, width. height)
        # Adjust these coordinates to match your actual PNG
        self.animations = {
            'idle': self.get_frames(0, 48, 48, 48, 1),   # 1 frame
            'walk': self.get_frames(0, 48, 48, 48, 6),   # 6 frames in a row
            'attack': self.get_frames(0, 336, 48, 48, 4),  # 4 frames in a row
        }

        self.state = 'idle'
        self.frame_index = 0
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center = (640, 535))
        self.flip = False

    def get_frames(self, x, y, w, h, count):
        """Slices a row of frames from the sheet"""
        frames = []
        for i in range(count):
            sub = self.sheet.subsurface(pygame.Rect(x + (i * w), y, w, h))
            # Optionl: Scale them up here if they are too small
            sub = pygame.transform.rotozoom(sub, 0, 3.0)
            frames.append(sub)
        return frames
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        # Default state
        new_state = 'idle'
        
        # Attack takes priority
        if mouse[0]: #Left Click
            new_state = 'attack'
        elif keys[pygame.K_d]:
            new_state = 'walk'
            self.flip = False
            self.rect.x += 5
        elif keys[pygame.K_a]:
            new_state = 'walk'
            self.flip = True
            self.rect.x -= 5

        # if we changed state, reset the animation timer
        if new_state != self.state:
            self.state = new_state
            self.frame_index = 0

        
    def animate(self):
        # Update frame index
        self.frame_index += 0.1 # Adjust this number for speed
        if self.frame_index >= len(self.animations[self.state]):
            # If we finished attacking, go back to idle
            if self.state == 'attack':
                self.state = 'idle'
            self.frame_index = 0

        # Set the image and flip it if moving left
        image = self.animations[self.state][int(self.frame_index)]
        self.image = pygame.transform.flip(image, self.flip, False)

    def update(self):
        self.handle_input()
        self.animate()

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
pygame.display.set_caption("My First RPG")

tileset = pygame.image.load('asset/Block-Land-16x16/World-Tiles.png').convert()
forest_sky = pygame.image.load('asset/background-asset/parallax/forest/forest_sky.png').convert()

tile_surf = tileset.subsurface(pygame.Rect(0, 400, 75, 60))

decor_group = pygame.sprite.Group()
player = pygame.sprite.GroupSingle(Player())


for i in range(25):
    x_pos = i * 50
    y_pos = 540
    
    scaled_surf = pygame.transform.rotozoom(tile_surf, 0, 3.0)

    new_tile = StaticItem((x_pos, y_pos), scaled_surf)

    decor_group.add(new_tile)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    screen.fill('gray')

    screen.blit(forest_sky,(0,0))
    decor_group.draw(screen)

    player.update() # This calls handle_input and animate automatically
    player.draw(screen)

    pygame.display.update()
    clock.tick(60)