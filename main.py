import sys
import pygame

from scripts.entities import Player, Enemy, Entities
from scripts.utils import loadImage, loadImages, Animation
from scripts.tilemap import Tilemap, dungeonGeneration


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()

        self.movement = {'left': False, 'right': False, 'up': False, 'down': False}

        self.assets = {
            'grass': loadImages('tiles/grass'),
            'bricks': loadImages('tiles/brick'),
            'walls': loadImages('tiles/walls'),
            'floorTiles': loadImages('tiles/floorTiles'),
            'props': loadImages('tiles/props'),
            'player': loadImage('entities/player.png'),
            'player/idle': Animation(loadImages('entities/player/idle'), imgDur=6),
            'player/run': Animation(loadImages('entities/player/run'), imgDur=4),
            'player/attack': Animation(loadImages('entities/player/attack'), imgDur=3),
            'player/hurt': Animation(loadImages('entities/player/hurt'), imgDur=5),
            'player/death': Animation(loadImages('entities/player/death'), imgDur=4),
            'player/dash': Animation(loadImages('entities/player/dash'), imgDur=10, loop=False),
            'enemy1/idle': Animation(loadImages('entities/enemy1/idle'), imgDur=4),
            'enemy1/run': Animation(loadImages('entities/enemy1/run'), imgDur=3),
            'enemy1/attack': Animation(loadImages('entities/enemy1/attack'), imgDur=2),
            'enemy1/death': Animation(loadImages('entities/enemy1/death'), imgDur=4),
            'enemy1/hurt': Animation(loadImages('entities/enemy1/hurt'), imgDur=4)
        }


        self.player1 = Player(self, (95 - 280, 8464 + 320), (28, 62), (-48, -30))

        self.enemy1 = Enemy(self, 'enemy1', (500, 500), (128, 100), 500, 100, 1, (-55, -105))
        self.enemys = Entities(self.enemy1)

        self.enemys.add(self.enemy1)

        self.tilemap = Tilemap(self, tileSize=32)

        self.scroll = [0, 0]

        self.running = True

        self.dungeonGenerator = dungeonGeneration((1920 // 2, 1080 // 2), 25, 100, self.tilemap)

    def main(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            # Sets caption to FPS to help visualize
            pygame.display.set_caption(str(self.clock.get_fps()))

            # goes through every event.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Get key presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player1.setAction('attack')
                    if event.key == pygame.K_v:
                        self.player1.setAction('dash')
                    if self.player1.action != 'attack':
                        if event.key == pygame.K_w:
                            self.movement['up'] = True
                        if event.key == pygame.K_s:
                            self.movement['down'] = True
                        if event.key == pygame.K_a:
                            self.movement['left'] = True
                        if event.key == pygame.K_d:
                            self.movement['right'] = True


                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.movement['up'] = False
                    if event.key == pygame.K_s:
                        self.movement['down'] = False
                    if event.key == pygame.K_a:
                        self.movement['left'] = False
                    if event.key == pygame.K_d:
                        self.movement['right'] = False

            # Updates
            self.player1.update(self.tilemap, (self.movement['right'] - self.movement['left'], self.movement['down'] - self.movement['up']))

            self.scroll[0] += (self.player1.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player1.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) / 30
            renderScroll = (int(self.scroll[0]), int(self.scroll[1]))

            for i in self.enemys.sprites():
                if i.death and i.action != 'death':
                    self.enemys.remove(i)
                self.enemys.update(i, self.tilemap, renderScroll, self.player1, dt)
            # self.enemy1.update(self.tilemap, renderScroll, self.player, dt)

            # Draw to the Screen
            self.screen.fill((0, 0, 0))

            self.tilemap.draw(self.screen, renderScroll)

            self.enemys.draw(self.screen, renderScroll)
            # self.enemy1.draw(self.screen, renderScroll)

            self.player1.draw(self.screen, renderScroll)

            for rect in self.tilemap.physicsRectsAround(self.player1.pos):
                pygame.draw.rect(self.screen, (255, 0, 0), rect, 1)

            pygame.draw.rect(self.screen, (0, 0, 0), (8, 8, 204, 29))
            pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, 2 * self.player1.health, 25))

            # self.dungeonGenerator.draw(self.screen)

            pygame.display.update()

            # print(self.player.pos[0] // self.tilemap.tileSize, self.player.pos[1] // self.tilemap.tileSize)

            # Caps Frames to 60
            self.clock.tick(60)


game = Game()
game.main()