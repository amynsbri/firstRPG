import pygame
from sys import exit

class StaticItem(pygame.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

class Player(pygame.sprite.Sprite): # editing rn
    def __init__(self):
        super().__init__()
        self.sheet = pygame.image.load('asset/asset_1/sprites/characters/player.png')

        # 1. Define Animations (x, y, width. height)
        # Adjust these coordinates to match your actual PNG
        self.animations = {
            'idle': self.get_frames(0, 48, 48, 48, 1),   # 1 frame
            'walk': self.get_frames(0, 48, 48, 48, 6),   # 6 frames in a row
            'attack': self.get_frames(0, 336, 48, 48, 4),  # 4 frames in a row
            'jump': self.get_frames(0, 432, 48, 48, 3) # Add this!
        }

        # Physics variables
        self.direction = pygame.math.Vector2(0, 0)
        self.gravity = 0.8      # Pulling force
        self.jump_speed = -16   # Initial upward burst (negative is UP in Pygame)
        self.on_ground = False  # To check if we can jump

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
    
    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

        # Floor collision
        if self.rect.bottom >= 620:
            self.rect.bottom = 620
            self.direction.y = 0
            self.on_ground = True
        else:
            self.on_ground = False
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        # Attack takes priority
        if keys[pygame.K_d]:
            self.direction.x = 5
            self.flip = False
            if self.on_ground and self.state != 'attack': self.state = 'walk'
        elif keys[pygame.K_a]:
            self.direction.x = -5
            self.flip = True
            if self.on_ground and self.state != 'attack': self.state = 'walk'
        else:
            self.direction.x = 0
            if self.on_ground and self.state not in ['attack', 'jump']:
                self.state = 'idle'

        # Jump Logic
        if keys[pygame.K_SPACE] and self.on_ground:
            self.direction.y = self.jump_speed
            self.state = 'jump'
            self.frame_index = 0
            self.on_ground = False

        # Attack Logic
        if mouse[0]:
            self.state = 'attack'
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

        # Apply horizontal movement
        self.rect.x += self.direction.x

        # Apply vertical movement and gravity
        self.apply_gravity()

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