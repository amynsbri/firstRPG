import pygame
from sys import exit

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = pygame.image.load('asset_1/sprites/characters/player.png').convert_alpha()
        self.width = 48
        self.height = 48
        self.scale_factor = 2.0

        # Create the lists
        self.idle_frames = []
        self.walk_frames = []
        self.attack_frames = []

        # --- STEP: SLICE & SCALE ALL MODES ---
        # Note: You need to check your player.png to see which 'y' belongs to which row!
        self.idle_frames = self.get_animations_frames(y_pos = 0, count = 6)     # Row 0
        self.walk_frames = self.get_animations_frames(y_pos = 48, count = 6)    # Row 1
        self.attack_frames = self.get_animations_frames(y_pos = 96, count = 4)  # Row 2

    # This helper function saves you from writing the same 'for loop' 3 times!
    def get_animations_frames(self, y_pos, count):
        temp_list = []
        for i in range(count):
            x = i * self.width
            cut_rect = pygame.Rect(x, y_pos, self.width, self.height)
            original_frame = self.sprite_sheet.subsurface(cut_rect)
            scaled_frame = pygame.transform.rotozoom(original_frame, 0, self.scale_factor)
            temp_list.append(scaled_frame)
        return temp_list



        # for i in range(4):
        #     x = i * self.width
        #     y = 336
        #     cut_rect = pygame.Rect(x, y, self.width, self.height)

            
        #     original_frame = self.sprite_sheet.subsurface(cut_rect)
        #     scaled_frame = pygame.transform.rotozoom(original_frame, 0, self.scale_factor)
        #     self.walk_frames.append(scaled_frame)
        
        # self.frame_index = 0  # Starts at the first image
        # self.image = self.walk_frames[self.frame_index]
        # self.rect = self.image.get_rect(center = (400, 280))

    def animation_state(self):
        # 1. Pick the correct list based on state
        if self.state == 'WALK':
            current_list = self.walk_frames
        elif self.state == 'ATTACK':
            current_list = self.attack_frames
        else:
            current_list = self.idle_frames

        # 2. Animate
        self.frame_index += 0.1 
        if self.frame_index >= len(current_list):
            self.frame_index = 0
            # If attack finishes, go back to idle
            if self.state == 'ATTACK':
                self.state = 'IDLE'
            
        self.image = current_list[int(self.frame_index)]

    def update(self):
        self.animation_state()

# Initialize pygame before creating the screen or objects
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("My First RPG")

#Background

sky_surf = pygame.image.load('material/graphics/Sky.png').convert()
ground_surf = pygame.image.load('material/graphics/Ground.png').convert()

# Player setup
player = pygame.sprite.GroupSingle()
player.add(Player())

while True:
    # 1. EVENT LOOP (Checking for inputs)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

    # 2. DRAWING (Outside the event loop!)
    screen.fill("gray")        # Clear the previous frame
    player.update()      # Draw the player
    screen.blit(sky_surf,(0,0))
    screen.blit(ground_surf,(0,300))
    
    # 3. UPDATE DISPLAY
    player.draw(screen)
    pygame.display.update()
    clock.tick(60)