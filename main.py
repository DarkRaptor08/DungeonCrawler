import sys
import time

import pygame

from scripts.entities import *
from scripts.utils import loadImage, loadImages, Animation
from scripts.tilemap import Tilemap, dungeonGeneration
from scripts.button import Button
from pygame import mixer

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()

        self.movement = {'left': False, 'right': False, 'up': False, 'down': False}

        # Loads all the assets
        self.assets = {
            'playButton': loadImage('buttons/play.png', 6),
            'quitButton': loadImage('buttons/quit.png', 6),
            'menuButton': loadImage('buttons/menu.png', 4.5),

            'logoButton': loadImage('buttons/logo.png', 5),
            'background': loadImage('background/1.png', 1),
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
            'enemy1/idle': Animation(loadImages('entities/enemy1/idle'), imgDur=6),
            'enemy1/run': Animation(loadImages('entities/enemy1/run'), imgDur=3),
            'enemy1/attack': Animation(loadImages('entities/enemy1/attack'), imgDur=2),
            'enemy1/death': Animation(loadImages('entities/enemy1/death'), imgDur=4),
            'enemy1/hurt': Animation(loadImages('entities/enemy1/hurt'), imgDur=4),
            'enemy2/idle': Animation(loadImages('entities/enemy2/idle'), imgDur=4),
            'boss/idle': Animation(loadImages('entities/boss/idle', 3), imgDur=4),
            'boss/charge': Animation(loadImages('entities/boss/charge', 3), imgDur=3),
            'boss/attack': Animation(loadImages('entities/boss/attack', 3), imgDur=4, loop=False),
            'boss/jump': Animation(loadImages('entities/boss/jump', 3), imgDur=5),
            'boss/death': Animation(loadImages('entities/boss/death', 3),imgDur=3),

        }


        # Loads The fonts
        self.font = pygame.font.Font('data/font/alagard.ttf', 120)
        self.font1 = pygame.font.Font('data/font/alagard.ttf', 50)
        self.winText = self.font.render('You Win', False, (255, 0, 0))

        # Initializes The player class
        self.player1 = Player(self, (95 - 280, 8464 + 320), (28, 62), (-48, -30))

        # Used to store the enemies
        self.enemys = []

        # Makes a Tilemap class
        self.tilemap = Tilemap(self, tileSize=32)

        self.scroll = [0, 0]

        self.running = True

        # Start dungeon Generation
        self.dungeonGenerator = dungeonGeneration((1920 // 2, 1080 // 2), 10, 40, self.tilemap, self)

        self.scroll[0] += (self.player1.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) - 1000
        self.scroll[1] += (self.player1.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) - 1000


        self.enemies = Entities(self.enemys)

        # Initialize the boss at the right position
        self.boss = RaccoonThingyMajigy(self, 'boss', ((1086 + 17) * 32, (264 + 17) * 32), (180, 180), 700, 125, .6, (0, 0))

        self.enemies.add(self.boss)

        # Button classes for menu
        self.playButton = Button((self.screen.get_width() - 180) / 2, 450, self.assets['playButton'], 1)
        self.quitButton = Button((self.screen.get_width() - 180) / 2, 750, self.assets['quitButton'], 1)
        self.menuButton = Button((self.screen.get_width() - 180) / 2, 600, self.assets['menuButton'], 1)
        self.logoButton = Button((self.screen.get_width() - 365) / 2, 100, self.assets['logoButton'], 1)

        self.startTime = 0
        self.endTime = 0

        # Loads the best time
        with open("data/data.txt", "r") as file1:
            # Writing data to a file
            self.bestTime = float(file1.readline())
        print(self.bestTime)

    def menu(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False


            # Draws the backgound object
            self.screen.blit(self.assets['background'], (0, 0))

            # Draws the buttons
            self.logoButton.draw(self.screen)
            self.playButton.draw(self.screen)
            self.quitButton.draw(self.screen)

            # Starts the game loop
            if self.playButton.clicked:
                self.player1 = Player(self, (95 - 280, 8464 + 320), (28, 62), (-48, -30))

                self.enemy1 = Enemy(self, 'enemy1', (95 - 280, 8464 + 320), (80, 100), 500, 100, 1, (-55, -105))
                self.enemys = []

                self.tilemap = Tilemap(self, tileSize=32)

                self.scroll = [0, 0]

                self.running = True

                self.dungeonGenerator = dungeonGeneration((1920 // 2, 1080 // 2), 10, 40, self.tilemap, self)

                self.scroll[0] += (self.player1.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) - 1000
                self.scroll[1] += (self.player1.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) - 1000

                self.enemies = Entities(self.enemys)

                self.boss = RaccoonThingyMajigy(self, 'boss', ((1086 + 17) * 32, (264 + 17) * 32), (180, 180), 700, 125,
                                                .6, (0, 0))

                self.enemies.add(self.boss)

                self.main()

            pygame.display.update()

        # Caps Frames to 60
            self.clock.tick(60)

        # Save the best time
        with open("data/data.txt", "w") as file1:
            # Writing data to a file
            file1.write(str(game.bestTime))

    # Win menu
    def winMenu(self):
        # Makes best time and your time text
        bestTimeText = self.font1.render(f'Best Time: {self.bestTime}', False, (255, 0, 0))
        timeText = self.font1.render(f'Time: {self.endTime}', False, (255, 0, 0))

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Draws all the buttons and text
            self.screen.blit(self.winText, ((self.screen.get_width() - self.winText.get_width()) / 2, 100))
            self.screen.blit(timeText, ((self.screen.get_width() - self.winText.get_width()) / 2, 250))
            self.screen.blit(bestTimeText, ((self.screen.get_width() - self.winText.get_width()) / 2, 350))
            self.playButton.draw(self.screen)
            self.menuButton.draw(self.screen)
            self.quitButton.draw(self.screen)

            # Switches to main menu
            if self.menuButton.clicked:
                self.running = False

            pygame.display.update()

            # Caps Frames to 60
            self.clock.tick(60)

        self.menu()

    def main(self):

        # Plays Music
        mixer.music.load('data/sound/Jairdebn_metal.wav')
        mixer.music.play(-1)
        pygame.mixer.music.set_volume(1)

        # Start time to calcuate end time
        self.startTime = time.process_time()

        while self.running:
            dt = self.clock.tick(60) / 1000

            # Sets caption to FPS to help visualize
            pygame.display.set_caption(str(self.clock.get_fps()))

            # goes through every event.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Get key presses
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player1.setAction('attack')
                    if event.key == pygame.K_v:
                        self.player1.setAction('dash')
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

            # Checks if the player is dead then go to menu
            if self.player1.health <= 0:
                self.running = False

            # Checks if the player won
            if self.boss not in self.enemies:
                self.endTime = time.process_time() - self.startTime
                if self.endTime < self.bestTime:
                    self.bestTime = self.endTime
                self.winMenu()
                self.running = False

            # Updates the player
            self.player1.update(self.tilemap, (self.movement['right'] - self.movement['left'], self.movement['down'] - self.movement['up']))

            # Changes Music volume to be louder the lower you are on health 
            mixer.music.set_volume(1 - self.player1.health / 2 / 100)


            # Updates scroll based on player position
            self.scroll[0] += (self.player1.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player1.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) / 30
            renderScroll = (int(self.scroll[0]), int(self.scroll[1]))


            # Updates enemies 
            for i in self.enemies.sprites():
                if i.death and i.action != 'death':
                    self.enemies.remove(i)
                self.enemies.update(i, self.tilemap, renderScroll, self.player1, dt)


            # Draw to the Screen
            self.screen.fill((0, 0, 0))

            #Draws Tile Map
            self.tilemap.draw(self.screen, renderScroll)

            # Draws Enemies
            self.enemies.draw(self.screen, renderScroll)

            # Draws Player
            self.player1.draw(self.screen, renderScroll)

            # Draws health
            pygame.draw.rect(self.screen, (0, 0, 0), (8, 8, 204, 29))
            pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, 2 * self.player1.health, 25))

            pygame.display.update()

            # Caps Frames to 60
            self.clock.tick(60)

        self.running = True

        self.menu()


game = Game()
game.menu()

pygame.quit()
sys.exit()