import pygame
from sys import exit
import random

# Game States
MENU = 0
GAME = 1
game_state = MENU

class StaticItem(pygame.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

class SpriteButton():
    def __init__(self, pos, surface):
        self.image = surface
        # Create a hover version by brightening the original image
        self.hover_image = self.image.copy()
        self.hover_image.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_ADD)
        
        self.rect = self.image.get_rect(center = pos)
        self.pressed = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        # Change image on hover
        if self.rect.collidepoint(pos):
            current_img = self.hover_image
            if pygame.mouse.get_pressed()[0] == 1 and not self.pressed:
                self.pressed = True
                action = True
        else:
            current_img = self.image

        if pygame.mouse.get_pressed()[0] == 0:
            self.pressed = False

        surface.blit(current_img, self.rect)
        return action

class Platform(pygame.sprite.Sprite):
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
        self.hitbox = self.rect.inflate(-100, -110)

        # Adding health
        self.max_health = 100
        self.current_health = 100
        self.health_bar_length = 50

        # New variables for knockback
        self.is_knocked_back = False
        self.knockback_start_time = 0
        self.knockback_duration = 300 # 0.3 seconds

    def get_frames(self, x, y, w, h, count):
        """Slices a row of frames from the sheet"""
        frames = []
        for i in range(count):
            sub = self.sheet.subsurface(pygame.Rect(x + (i * w), y, w, h))
            # Optionl: Scale them up here if they are too small
            sub = pygame.transform.rotozoom(sub, 0, 3.0)
            frames.append(sub)
        return frames
    
    def apply_gravity(self, platforms):
        self.on_ground = False
        self.direction.y += self.gravity
        self.hitbox.y += self.direction.y

        # 2. Check for platform collisions
        # This loop checks every platform in the group you pass in
        for platform in platforms:
            if self.hitbox.colliderect(platform.rect):
                # Only stop if we are falling DOWN onto the platfrom
                if self.direction.y  > 0:
                    self.hitbox.bottom = platform.rect.top + 25
                    self.direction.y = 0
                    self.on_ground = True

        # Floor collision
        if self.hitbox.bottom >= 620:
            self.hitbox.bottom = 620
            self.direction.y = 0
            self.on_ground = True

        self.rect.midbottom = self.hitbox.midbottom
    
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
        if not self.on_ground:
            self.state = 'jump'
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

        self.mask = pygame.mask.from_surface(self.image)

    def draw_health(self, surface):
        # Position the bar above the player's head
        bar_rect = pygame.Rect(self.rect.centerx - 25, self.rect.top + 50, self.health_bar_length, 5)
        # Calculate health ratio
        health_ratio = self.current_health / self.max_health
        # Draw background (Red) and foreground (Green)
        pygame.draw.rect(surface, (255, 0, 0), bar_rect)
        pygame.draw.rect(surface, (0, 255, 0), (bar_rect.x, bar_rect.y, self.health_bar_length * health_ratio, 5))

    def take_damage(self, amount, source_pos):
        # Only take damage if not already recovering from knockback
        if not self.is_knocked_back:
            self.current_health -= amount
            self.is_knocked_back = True
            self.knockback_start_time = pygame.time.get_ticks()
            
            # Calculate direction: if slime is to the right, push left.
            if self.rect.centerx < source_pos[0]:
                self.direction.x = -15  # Pushed Left
            else:
                self.direction.x = 15   # Pushed Right
            
            # Add a small vertical hop to the knockback
            self.direction.y = -8
            self.on_ground = False

    def update(self, platforms):
        current_time = pygame.time.get_ticks()
        
        # If knocked back, bypass handle_input so player can't move mid-air
        if self.is_knocked_back:
            # This reduces the horizontal speed by 10% every frame (approx 60fps)
            self.direction.x *= 0.9 
            
            # Stop the knockback if the timer runs out
            if current_time - self.knockback_start_time > self.knockback_duration:
                self.is_knocked_back = False
        else:
            self.handle_input()

        # Apply movement and physics
        self.hitbox.x += self.direction.x
        self.apply_gravity(platforms)
        self.animate()
        self.rect.midbottom = self.hitbox.midbottom

class Slime(pygame.sprite.Sprite):
    def __init__(self, platform, player_group):
        super().__init__()
        self.sheet = pygame.image.load('asset/asset_1/sprites/characters/slime.png').convert_alpha()

        # Define animations
        self.animations = {
            'walk': self.get_frames(0, 0, 32, 32, 4),   # Row 0, 4 frames
            'jump': self.get_frames(0, 192, 32, 32, 7),   # Row 1, 4 frames
        }

        self.platform = platform
        self.player_group = player_group # To find the player

        self.state = 'walk'
        self.frame_index = 0
        self.image = self.animations[self.state][self.frame_index]

        # Spawn at a random X position within the platform width
        start_x = random.randint(self.platform.rect.left, self.platform.rect.right - 64)
        self.rect = self.image.get_rect(bottom = self.platform.rect.top + 25)

        # AI & Speed Settings
        self.walk_speed = 1.5 # Slower patrol speed
        self.jump_speed = 4.0 # Speed during attack
        self.speed = random.choice([-self.walk_speed, self.walk_speed]) # random initial direction
        self.flip = False

        # Cooldown Logic
        self.can_jump = True
        self.attack_time = 0
        self.attack_cooldown = 2000 # 2 seconds delay

        # adding health
        self.max_health = 30
        self.current_health = 30
        self.health_bar_length = 40

    def get_frames(self, x, y, w, h, count):
        frames = []
        for i in range(count):
            sub = self.sheet.subsurface(pygame.Rect(x + (i * w), y, w, h))
            sub = pygame.transform.rotozoom(sub, 0, 2.0) # Scale it up
            frames.append(sub)
        return frames
    
    def cooldown_timer(self):
        # Check if enough time as passed to jump again
        if not self.can_jump:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_jump = True
    
    def animate(self):
        self.frame_index += 0.1

        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
            # If it finished a jump it goes back to walking
            if self.state == 'jump':
                self.state = 'walk'
                self.speed = self.walk_speed if not self.flip else -self.walk_speed
                # Start cooldown
                self.can_jump = False
                self.attack_time = pygame.time.get_ticks()
        
        self.image = self.animations[self.state][int(self.frame_index)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

        self.mask = pygame.mask.from_surface(self.image)

    def check_player(self):
        # Find the player object from the group
        player_sprite = self.player_group.sprite

        # Only jump if not on cooldown
        if player_sprite and self.can_jump:
            # Calculate distance betwen slime and player
            distance_x = abs(self.rect.centerx - player_sprite.rect.centerx)
            distance_y = abs(self.rect.centery - player_sprite.rect.centery)

            # If player is within 150 pixels horizontally and roughly same height
            if distance_x < 200 and distance_y < 80:
                if self.state == 'walk':
                    self.state = 'jump'
                    self.frame_index = 0
                    # Move slightly towards player when jumping
                    if self.rect.centerx > player_sprite.rect.centerx:
                        self.speed = -self.jump_speed
                        self.flip = True
                    else:
                        self.speed = self.jump_speed
                        self.flip = False

    def draw_health(self, surface):
        # Position the bar above the slime's head
        bar_rect = pygame.Rect(self.rect.centerx - 20, self.rect.top + 5, self.health_bar_length, 4)
        health_ratio = self.current_health / self.max_health
        pygame.draw.rect(surface, (255, 0, 0), bar_rect)
        pygame.draw.rect(surface, (0, 255, 0), (bar_rect.x, bar_rect.y, self.health_bar_length * health_ratio, 4))

    def update(self):
        self.cooldown_timer()
        self.check_player()
        self.animate()

        # Movement logic
        self.rect.x += self.speed

        # If we hit the right edge, force speed to be negative
        if self.rect.right > self.platform.rect.right:
            self.rect.right = self.platform.rect.right
            self.speed = -abs(self.speed)
            self.flip = True
        elif self.rect.left < self.platform.rect.left:
            self.rect.left = self.platform.rect.left
            self.speed = abs(self.speed)
            self.flip = False


pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
pygame.display.set_caption("My First RPG")

# Load the full UI sheet
ui_sheet = pygame.image.load('asset/FreeDemo.png').convert_alpha()

def get_ui_element(x, y, w, h):
    sheet_rect = ui_sheet.get_rect()
    requested_rect = pygame.Rect(x, y, w, h)
    safe_rect = requested_rect.clip(sheet_rect)

    surf = ui_sheet.subsurface(safe_rect)
    return pygame.transform.rotozoom(surf, 0, 3.5)

# --- Safe Coordinates for your 300x300 sheet ---
# Board: Starting a bit further in from the top-left
bamboo_board = get_ui_element(10, 100, 120, 145)
board_rect = bamboo_board.get_rect(center=(640, 360))

# Buttons: Narrower width to ensure they don't pop out of the sheet
play_surf     = get_ui_element(45, 146, 53, 15)
settings_surf = get_ui_element(45, 166, 48, 15)
exit_surf     = get_ui_element(58, 235, 48, 15)

# Initialize Buttons
play_button     = SpriteButton((643, 298), play_surf)
settings_button = SpriteButton((643, 365), settings_surf)
exit_button     = SpriteButton((643, 455), exit_surf)

forest_sky = pygame.image.load('asset/background-asset/parallax/forest/forest_sky.png').convert()

# Floor
tileset = pygame.image.load('asset/Block-Land-16x16/World-Tiles.png').convert()
tile_surf = tileset.subsurface(pygame.Rect(0, 400, 75, 60))
decor_group = pygame.sprite.Group()

for i in range(25):
    x_pos = i * 50
    y_pos = 540
    
    scaled_surf = pygame.transform.rotozoom(tile_surf, 0, 3.0)

    new_tile = StaticItem((x_pos, y_pos), scaled_surf)

    decor_group.add(new_tile)

# Platform
tileset_pf = pygame.image.load('asset/asset_1/sprites/tilesets/plains.png').convert()
plat_tile_surf = tileset_pf.subsurface(pygame.Rect(15, 112, 48, 16))

plat_tile_surf = pygame.transform.scale(plat_tile_surf, (288, 48))

platforms_group = pygame.sprite.Group()

platform_coords = [(100, 400), (100, 100), (450, 250), (800, 400), (900, 150)]

for pos in platform_coords:
    # Pass the 'plat_tile_surf' we just created into the class
    new_platform = Platform(pos, plat_tile_surf)
    platforms_group.add(new_platform)

player = pygame.sprite.GroupSingle(Player())

# Slime

slimes_group = pygame.sprite.Group()

# For every platform, decide if a slime should spawn there
for plat in platforms_group:
    # 50% chance to spawn a slime on this platform
    for _ in range(random.randint(1, 2)):
        new_slime = Slime(plat, player)
        slimes_group.add(new_slime)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if game_state == MENU:
        # 1. Background color
        screen.fill('#2d3b2d') 
        
        # 2. Draw the Bamboo Board background FIRST
        screen.blit(bamboo_board, board_rect)
        
        # 3. Draw and check buttons (They appear on top of the board)
        if play_button.draw(screen):
            game_state = GAME
        
        if settings_button.draw(screen):
            print("Settings Clicked!")
            
        if exit_button.draw(screen):
            pygame.quit()
            exit()

    elif game_state == GAME:
        # 1. PLAYER ATTACK LOGIC
        if player.sprite.state == 'attack':
            attack_hits = pygame.sprite.spritecollide(
                player.sprite, 
                slimes_group, 
                False, 
                pygame.sprite.collide_mask
            )
            for slime in attack_hits:
                slime.current_health -= 20 
                if slime.current_health <= 0:
                    slime.kill()

        # 2. HIT DETECTION (SLIME HIT PLAYER)
        hit_slimes = pygame.sprite.spritecollide(
            player.sprite, 
            slimes_group, 
            False, 
            pygame.sprite.collide_mask
        )

        if hit_slimes:
            for slime in hit_slimes:
                player.sprite.take_damage(10, slime.rect.center)

        # 3. DRAWING & UPDATES
        screen.fill('gray')
        screen.blit(forest_sky,(0,0))
        decor_group.draw(screen)
        platforms_group.draw(screen)

        slimes_group.update()
        slimes_group.draw(screen)
        for slime in slimes_group:
            slime.draw_health(screen)
            
        player.update(platforms_group)
        player.draw(screen)
        player.sprite.draw_health(screen)

    # Always update display and tick the clock at the very end of the loop
    pygame.display.update()
    clock.tick(60)