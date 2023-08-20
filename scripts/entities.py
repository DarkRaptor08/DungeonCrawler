import pygame
import math
import random

class PhysicsEntity(pygame.sprite.Sprite):
    def __init__(self, game, entityType, pos, size, offset=(0, 0)):
        super().__init__()
        self.game = game
        self.type = entityType
        self.pos = list(pos)
        self.size = size
        self.velocity = 1
        self.collisionns = {'up': False, 'down': False, 'left': False, 'right': False}

        self.action = ''
        self.animOffset = offset
        self.flip = False
        self.setAction('idle')
        self.health = 100

        self.rect1 = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def setAction(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        frameMovement = (movement[0] * self.velocity, movement[1] * self.velocity)

        self.pos[0] += frameMovement[0] * 10
        entityRect = self.rect()
        for rect in tilemap.physicsRectsAround(self.pos):
            if entityRect.colliderect(rect):
                if frameMovement[0] > 0:
                    entityRect.right = rect.left
                if frameMovement[0] < 0:
                    entityRect.left = rect.right
                self.pos[0] = entityRect.x

        self.pos[1] += frameMovement[1] * 10
        entityRect = self.rect()
        for rect in tilemap.physicsRectsAround(self.pos):
            if entityRect.colliderect(rect):
                if frameMovement[1] > 0:
                    entityRect.bottom = rect.top
                if frameMovement[1] < 0:
                    entityRect.top = rect.bottom
                self.pos[1] = entityRect.y

        if movement[0] > 0:
            self.flip = False
        elif movement[0] < 0:
            self.flip = True

        #self.velocity[1] = min(5, self.velocity[1] + 0.1)

        self.animation.update()

    def draw(self, surf, offset):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.animOffset[0], self.pos[1] - offset[1] + self.animOffset[1]))
        # pygame.draw.rect(surf, (255, 0, 0), self.rect(), 2)


class Player(PhysicsEntity):
    def __init__(self, game, pos, size, offset):
        super().__init__(game, 'player', pos, size, offset)
        self.attackRectLeft = pygame.Rect(self.pos[0] - 100, self.pos[1], 75, 150)
        self.attackRectRight = pygame.Rect(self.pos[0] + 100, self.pos[1] + 100, 75, 150)

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.setAction('attack')
        elif keys[pygame.K_v]:
            self.setAction('dash')
        elif movement[0] != 0 or movement[1] != 0:
            self.setAction('run')
        elif not self.action == 'dash':
            self.setAction('idle')

    def draw(self, surface, offset):
        self.attackRectLeft.topleft = (self.pos[0] - offset[0] - 100 + 5 + 10 + 25, self.pos[1] - offset[1] - 25 - 25)
        self.attackRectRight.topright = (self.pos[0] - offset[0] - 100 + 5 + 205 + 2 - 25, self.pos[1] - offset[1] - 25 - 25)
        # pygame.draw.rect(surface, (200, 0, 0), self.attackRectLeft)
        # pygame.draw.rect(surface, (0, 0, 200), self.attackRectRight)
        # pygame.draw.rect(surface, (0, 255, 0), self.rect1)
        self.rect1.x = self.pos[0] - offset[0]
        self.rect1.y = self.pos[1] - offset[1]
        super().draw(surface, offset)


class Enemy(PhysicsEntity):
    def __init__(self, game, name, pos, size, sightRadius, attackRadius, speed , offset):
        super().__init__(game, name, pos, size, offset)
        self.sightRadius = sightRadius
        self.playerMask = pygame.mask.Mask((0, 0))
        self.enemyMask = pygame.mask.Mask((0, 0))
        self.sightRect = pygame.Rect(pos[0]-sightRadius//2, pos[1]-sightRadius//2, sightRadius, sightRadius)
        self.velocity = speed
        self.attackRadius = attackRadius
        self.status = 'idle'
        self.attackSpeed = 5
        self.canAct = 0
        self.death = False
        self.timeSinceLastAttack = 0
        self.health = 5000


        self.rect1.inflate(-200, -100)

    def update(self, aasfs, tilemap, offset, player, dt, movement=(0, 0)):

        # Check collision with player's rectangle

        self.canAct -= 1 * dt
        if self.canAct < 0:
            self.canAct = 0

        self.getStatus(player)


        if self.health <= 0 and self.action != 'death':
            self.setAction('death')
            self.death = True

        elif (self.rect1.colliderect(player.attackRectLeft) and player.flip and player.action == 'attack') or (self.rect1.colliderect(player.attackRectRight) and  not player.flip and player.action == 'attack'):
            self.health -= 10
            self.setAction('hurt')

        elif self.status == 'attack':
            if self.canAct == 0:
                self.setAction('attack')
                self.canAct = 1
                self.timeSinceLastAttack -= 1 * dt * 2
                if self.timeSinceLastAttack <= 0:
                    player.health -= 10
                    self.timeSinceLastAttack = 5
                else:
                    self.setAction('idle')

        elif self.status == 'move':
            var = self.getPlayerDistance(player)
            dx = player.pos[0] - self.pos[0]
            dy = player.pos[1] - self.pos[1]
            angle = math.atan2(dy, dx)
            movement = (self.velocity * math.cos(angle) * dt * 2, self.velocity * math.sin(angle) * dt * 2)

        elif self.action != 'death' or self.animation.frame == 0:
            self.setAction('idle')

        super().update(tilemap, movement=movement)


    def getStatus(self, player):
        distance = self.getPlayerDistance(player)[0]
        if distance <= self.attackRadius:
            self.status = 'attack'

        elif distance <= self.sightRadius:
            self.status = 'move'
            self.setAction('run')
        else:
            self.status = 'idle'

    def getPlayerDistance(self, player):
        enemyVec = pygame.math.Vector2(self.rect1.center)
        playerVec = pygame.math.Vector2(player.rect1.center)
        distance1 = (playerVec - enemyVec)
        distance = (playerVec - enemyVec).magnitude()
        return (distance, distance1)

    def draw(self, surface, offset):
        pygame.draw.rect(surface, (255, 0, 0), self.rect1)
        self.rect1.x = self.pos[0] - offset[0]
        self.rect1.y = self.pos[1] - offset[1]
        super().draw(surface, offset)


class RaccoonThingyMajigy(PhysicsEntity):
    def __init__(self, game, name, pos, size, sightRadius, attackRadius, speed, offset):
        super().__init__(game, name, pos, size, offset)
        self.sightRadius = sightRadius
        self.playerMask = pygame.mask.Mask((0, 0))
        self.enemyMask = pygame.mask.Mask((0, 0))
        self.sightRect = pygame.Rect(pos[0] - sightRadius // 2, pos[1] - sightRadius // 2, sightRadius, sightRadius)
        self.velocity = speed
        self.attackRadius = attackRadius
        self.status = 'idle'
        self.attackSpeed = 5
        self.canAct = 0
        self.death = False
        self.timeSinceLastAttack = 0
        self.attack = 0
        self.jumpLoc = [-100, -100]
        self.time_to_jump = 0

        self.rect1.inflate(-200, -100)
        self.health = 10000

    def update(self, afasf, tilemap, offset, player, dt, movement=(0, 0)):

        self.canAct -= 1 * dt
        if self.canAct < 0:
            self.canAct = 0

        self.getStatus(player)

        if self.health <= 0 and self.action != 'death':
            self.setAction('death')
            self.death = True

        elif (self.rect1.colliderect(player.attackRectLeft) and player.flip and player.action == 'attack') or (
                self.rect1.colliderect(player.attackRectRight) and not player.flip and player.action == 'attack'):
            self.health -= 10
            self.setAction('charge')

        elif self.status == 'attack':
            if self.canAct == 0:
                self.setAction('attack')
                self.canAct = 1
                if self.timeSinceLastAttack <= 0:
                    player.health -= 10
                    self.timeSinceLastAttack = 7


        elif self.status == 'move':
            var = self.getPlayerDistance(player)

            dx = player.pos[0] - self.pos[0]
            dy = player.pos[1] - self.pos[1]
            angle = math.atan2(dy, dx)
            movement = (self.velocity * math.cos(angle) * dt * 2, self.velocity * math.sin(angle) * dt * 2)

        elif self.action != 'death' or self.animation.frame == 0:
            self.setAction('idle')

        self.timeSinceLastAttack -= 1 * dt

        super().update(tilemap, movement=movement)

    def getStatus(self, player):
        distance = self.getPlayerDistance(player)[0]
        if distance <= self.attackRadius:
            self.status = 'attack'

        elif distance <= self.sightRadius:
            self.status = 'move'
            self.setAction('run')
        else:
            self.status = 'idle'

    def getPlayerDistance(self, player):
        enemyVec = pygame.math.Vector2(self.rect1.center)
        playerVec = pygame.math.Vector2(player.rect1.center)
        distance1 = (playerVec - enemyVec)
        distance = (playerVec - enemyVec).magnitude()
        return (distance, distance1)
    def getDistance(self, point):
        enemyVec = pygame.math.Vector2(self.rect1.center)
        playerVec = pygame.math.Vector2(point)
        distance1 = (playerVec - enemyVec)
        distance = (playerVec - enemyVec).magnitude()
        return (distance, distance1)

    def getStatus(self, player):
        distance = self.getPlayerDistance(player)[0]
        if distance <= self.attackRadius:
            self.status = 'attack'

        elif distance <= self.sightRadius:
            self.status = 'move'
            self.setAction('charge')
        else:
            self.status = 'idle'

    def draw(self, surface, offset):
        pygame.draw.circle(surface, (255, 0, 0), self.jumpLoc, 10)
        pygame.draw.rect(surface, (255, 0, 0), self.rect1)
        self.rect1.x = self.pos[0] - offset[0]
        self.rect1.y = self.pos[1] - offset[1]
        super().draw(surface, offset)


class Entities(pygame.sprite.Group):
    def __init__(self, *enemys):
        super().__init__(*enemys)

    def draw(self, surface, offset):
        for i in self.sprites():
            i.draw(surface, offset)