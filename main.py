import pygame
from sys import exit
import random

class StaticItem(pygame.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

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
    # --- PLAYER ATTACK LOGIC ---
    if player.sprite.state == 'attack':
        # Check if the attacking player touches any slimes using masks
        # False means we don't kill the slime immediately (we wait for HP to hit 0)
        attack_hits = pygame.sprite.spritecollide(
            player.sprite, 
            slimes_group, 
            False, 
            pygame.sprite.collide_mask
        )

        for slime in attack_hits:
            # Reduce slime health
            slime.current_health -= 20 # Adjust damage amount as needed
            
            # If slime health is 0 or less, remove it
            if slime.current_health <= 0:
                slime.kill()

    hit_slimes = pygame.sprite.spritecollide(
    player.sprite, 
    slimes_group, 
    False, 
    pygame.sprite.collide_mask # This checks actual pixels!
)

    if hit_slimes:
        for slime in hit_slimes:
            player.sprite.take_damage(10, slime.rect.center)

    screen.fill('gray')
    screen.blit(forest_sky,(0,0))
    decor_group.draw(screen)
    platforms_group.draw(screen)

    # Slimes Logic
    slimes_group.update()
    slimes_group.draw(screen)
    for slime in slimes_group:
        slime.draw_health(screen) # Manually draw health bars
        
    # Player Logic
    player.update(platforms_group)
    player.draw(screen)
    player.sprite.draw_health(screen) # Draw player health bar

    pygame.display.update()
    clock.tick(60)