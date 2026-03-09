import pygame
from sys import exit

class StaticItem(pygame.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

pygame.init()
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
pygame.display.set_caption("My First RPG")

tileset = pygame.image.load('asset/Block-Land-16x16/World-Tiles.png').convert()
forest_sky = pygame.image.load('asset/background-asset/parallax/forest/forest_sky.png').convert()

tile_surf = tileset.subsurface(pygame.Rect(0, 400, 75, 60))

decor_group = pygame.sprite.Group()


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

    pygame.display.update()
    clock.tick(60)