import math
import random
import pygame
import scripts.rooms
from scipy.spatial import Delaunay
from scipy.spatial import distance
import numpy as np
import networkx as nx

from scripts.spawnRoom import *

NEIGHBOR_OFFSETS = [(-1, 0), (0, 0), (1, 0), (-1, 1), (1, 1), (-1, 2), (0, 2), (1, 2)]
PHYSICS_TILES = {'bricks'}

class Tilemap:
    def __init__(self, game, tileSize=32):
        self.game = game
        self.tileSize = tileSize
        self.tileMap = {}
        self.otherTiles = {}

        # for i in range(100):
        #     self.tileMap[str( i) + ';0'] = {'type': 'bricks', 'variant': 1, 'rotation': , 'pos': (i, 0)}
        #
        #     self.tileMap[str( i) + ';10'] = {'type': 'grass', 'variant': 1, 'pos': (i, 10)}
        #     self.tileMap['0;' + str(i + 1)] = {'type': 'bricks', 'variant': 2, 'pos': (0, i)}
        #     for y in range(15):
        #         self.tileMap[str(i) + ';' + str(y + 11)] = {'type': 'grass', 'variant': 4, 'pos': (i, y + 11)}
        # self.tileMap['0;0'] = {'type': 'bricks', 'variant': 3, 'pos': (0, 0)}


    def tilesAround(self, pos):
        tiles = []
        tileLoc = (int(pos[0] // self.tileSize), int(pos[1] // self.tileSize))
        for offset in NEIGHBOR_OFFSETS:
            checkLoc = str(tileLoc[0] + offset[0]) + ';' + str(tileLoc[1] + offset[1])
            if checkLoc in self.tileMap:
                tiles.append(self.tileMap[checkLoc])
        return tiles

    def physicsRectsAround(self, pos):
        rects = []
        for tile in self.tilesAround(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tileSize, tile['pos'][1] * self.tileSize, self.tileSize, self.tileSize))

        return rects

    def draw(self, surf, offset):
        amount = 0

        for x in range(offset[0] // self.tileSize, (offset[0] + surf.get_width()) // self.tileSize + 8):
            for y in range(offset[1] // self.tileSize, (offset[1] + surf.get_height()) // self.tileSize + 8):
                loc = str(x) + ';' + str(y)
                if loc in self.tileMap:
                    tile = self.tileMap[loc]
                    if 'flip' in tile:
                        surf.blit(pygame.transform.flip(pygame.transform.rotate(self.game.assets[tile['type']][tile['variant']], tile['rotation']), tile['flip'], False), (tile['pos'][0] * self.tileSize - offset[0], tile['pos'][1] * self.tileSize - offset[1]))
                    else:
                        surf.blit(pygame.transform.rotate(self.game.assets[tile['type']][tile['variant']], tile['rotation']), (tile['pos'][0] * self.tileSize - offset[0], tile['pos'][1] * self.tileSize - offset[1]))

                    #pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(tile['pos'][0] * self.tileSize - offset[0], tile['pos'][1] * self.tileSize - offset[1], self.tileSize, self.tileSize), 1)
                    amount += 1

        amount = 0
        for x in range(offset[0] // self.tileSize, (offset[0] + surf.get_width()) // self.tileSize + 1):
            for y in range(offset[1] // self.tileSize, (offset[1] + surf.get_height()) // self.tileSize + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.otherTiles:
                    tile = self.otherTiles[loc]

                    surf.blit(
                        pygame.transform.rotate(self.game.assets[tile['type']][tile['variant']], tile['rotation']),
                        (tile['pos'][0] * self.tileSize - offset[0], tile['pos'][1] * self.tileSize - offset[1] - self.game.assets[tile['type']][tile['variant']].get_height())
                    )
                    #pygame.draw.rect(surf, (255, 0, 0), pygame.Rect(tile['pos'][0] * self.tileSize - offset[0],
                                                                        #tile['pos'][1] * self.tileSize - offset[1],
                                                                       # self.tileSize, self.tileSize), 1)
                    amount += 1

        # for loc in self.tileMap:
        #     tile = self.tileMap[loc]
        #     surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tileSize - offset[0], tile['pos'][1] * self.tileSize - offset[1]))


class dungeonGeneration:
    def __init__(self, dungeonSize, mainRooms, medRooms, tileMap):
        self.dungeonSize = tuple(dungeonSize)
        self.mainRoomsAmount = mainRooms
        self.medRoomsAmount = medRooms
        self.mainRooms = []
        self.mainRoomRects = []
        self.medRoomsRects = []
        self.medRooms = []

        self.hallwaysGraph = []
        self.hallwaysHoriz = []
        self.hallwaysVert = []

        self.tilemap = tileMap

        self.generate()

    # Randomly generate a random point in an ellipse
    def getRandomPointInEllipse(self, ellipseWidth, ellipseHeight):
        t = 2 * math.pi * random.random()
        u = random.random() + random.random()
        r = None
        if u > 1:
            r = 2 - u
        else:
            r = u

        return round(ellipseWidth * r * math.cos(t) / 2) + ellipseWidth // 2, round(ellipseHeight * r * math.sin(t) / 2) + ellipseHeight // 2

    def checkCollision(self, rectList, rect):
        for other_rect in rectList:
            if rect.colliderect(other_rect):
                return True
        return False

    def generateRooms(self, amount, collisionRects, roomList):
        rooms = random.choices(roomList, k=amount)

        roomRects = []  # List to store the generated room rects

        for room in rooms:
            x, y = self.getRandomPointInEllipse(self.dungeonSize[0], self.dungeonSize[1])

            width = len(room[0])

            height = len(room)

            roomRect = pygame.Rect(x, y, width, height)
            while self.checkCollision(collisionRects, roomRect):

                x, y = self.getRandomPointInEllipse(self.dungeonSize[0], self.dungeonSize[1])

                width = len(room[0])

                height = len(room)

                roomRect = pygame.Rect(x , y , width, height)

            roomRects.append(roomRect)
            collisionRects.append(roomRect)

        return roomRects, rooms

    def generate(self):

        spawn = spawnRoom
        spawnRect = [pygame.Rect(-20, 264, 22, 24)]

        self.mainRoomRects, self.mainRooms = self.generateRooms(self.mainRoomsAmount, spawnRect, scripts.rooms.mainRoomList)

        self.medRoomsRects, self.medRooms = self.generateRooms(self.medRoomsAmount, self.mainRoomRects + spawnRect, scripts.rooms.medRoomList)

        points = []

        points.append((spawnRect[0].midright[0], spawnRect[0].midright[1]))

        for rect in self.mainRoomRects:
            # points.append(rect.midleft)
            # points.append(rect.midright)
            # points.append(rect.midtop)
            # points.append(rect.midbottom)
            points.append(rect.center)

        tri = Delaunay(points)

        G = nx.Graph()
        for simp in tri.simplices:
            for i, j in zip(simp, np.roll(simp, -1)):
                G.add_edge(points[i], points[j], weight=distance.euclidean(points[i], points[j]))


        mst = nx.minimum_spanning_tree(G)

        mergedTreeDiagram = nx.Graph()

        for u, v in mst.edges:
            x1, y1 = u
            x2, y2 = v
            if distance.euclidean(u, v) < 100:
                mergedTreeDiagram.add_edge((x1, y1), (x2, y2))
            else:
                mergedTreeDiagram.add_edge((x1, y1), (x1, y2))
                mergedTreeDiagram.add_edge((x1, y2), (x2, y2))

        points = []
        for rect in self.mainRoomRects + self.medRoomsRects + spawnRect:
            points.append(rect.center)

        tri = Delaunay(points)

        C = nx.Graph()
        for simp in tri.simplices:
            for i, j in zip(simp, np.roll(simp, -1)):
                C.add_edge(points[i], points[j], weight=distance.euclidean(points[i], points[j]))

        mstAll = nx.minimum_spanning_tree(C)
        mstAll1 = nx.Graph()
        for u, v in mstAll.edges:
            x1, y1 = u
            x2, y2 = v
            mstAll1.add_edge((x1, y1), (x1, y2))
            mstAll1.add_edge((x1, y2), (x2, y2))

        self.hallwaysGraph = nx.compose(mstAll1, mergedTreeDiagram)

        # Create hallways for the edges in mstAll and ensure they all connect

        for u, v in self.hallwaysGraph.edges:
            x1, y1 = u
            x2, y2 = v
            if x1 == x2:  # Vertical line
                if y1 < y2:
                    rect = pygame.Rect(x1 - 3, y1, 1 * 6, y2 - y1 + 1 * 3)
                else:
                    rect = pygame.Rect(x1 - 3, y2, 1 * 6, y1 - y2 + 1 * 3)
                self.hallwaysVert.append(rect)
            elif y1 == y2:  # Horizontal line
                if x1 < x2:
                    rect = pygame.Rect(x1 - 3, y1 - 4, x2 - x1 + 1 * 6, 1 * 8)
                else:
                    rect = pygame.Rect(x2 - 3, y1 - 4, x1 - x2 + 1 * 6, 1 * 8)
                self.hallwaysHoriz.append(rect)

        tileDict = {
            1: ['grass', 1],
            2: ['grass', 2],
            3: ['grass', 3],
            4: ['grass', 4],
            5: ['grass', 0],
            6: ['walls', 0],
            7: ['bricks', 1],
            8: ['bricks', 2],
            9: ['bricks', 3],
            10: ['bricks', 0],
            11: ['floorTiles', 0],
            12: ['bricks', 4],
            13: ['bricks', 6],
            14: ['bricks', 7]
        }


        props = {
            30: ['props', 27],
            35: ['props', 29],
        }

        for y, row in enumerate(spawn):
            for x, tile in enumerate(row):
                string = f'{x + spawnRect[0].x};{y + spawnRect[0].y}'
                point = round((tile - int(tile)) * 10)
                if tile == 8.2:
                    tile = 12
                    point = 0
                tile = int(tile)

                if spawnRoomProps[y][x] != -1:
                    self.tilemap.otherTiles[string] = {'type': props[spawnRoomProps[y][x]][0], 'variant': props[spawnRoomProps[y][x]][1],
                                                    'rotation': 90 * point,
                                                    'pos': (x + spawnRect[0].x, y + spawnRect[0].y)}

                if string in self.tilemap.tileMap and (
                        self.tilemap.tileMap[string]['type'] == 'floorTiles' or tile == 7):
                    tile = 11
                else:

                    if string in self.tilemap.tileMap and (
                            self.tilemap.tileMap[string]['type'] == 'floorTiles' or tile == 7):
                        tile = 6
                    elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and \
                            self.tilemap.tileMap[string]['variant'] == 1 and tile == 7:
                        tile = 13
                    self.tilemap.tileMap[string] = {'type': tileDict[tile][0], 'variant': tileDict[tile][1],
                                                    'rotation': 90 * point,
                                                    'pos': (x + spawnRect[0].x, y + spawnRect[0].y)}

        for i, room in enumerate(self.mainRooms):
            for y, row in enumerate(room):
                for x, tile in enumerate(row):
                    string = f'{x + self.medRoomsRects[i].x};{y + self.medRoomsRects[i].y}'
                    point = round((tile - int(tile)) * 10)
                    if tile == 8.2:
                        tile = 12
                        point = 0
                    tile = int(tile)
                    if string in self.tilemap.tileMap and (self.tilemap.tileMap[string]['type'] == 'floorTiles' or tile == 7):
                        tile = 11
                    else:
                        if string in self.tilemap.tileMap and (self.tilemap.tileMap[string]['type'] == 'floorTiles' or tile == 7):
                            tile = 6
                        elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 1 and tile == 7:
                            tile = 13
                        self.tilemap.tileMap[string] = {'type': tileDict[tile][0], 'variant': tileDict[tile][1], 'rotation': 90 * point, 'pos': (x + self.medRoomsRects[i].x, y + self.medRoomsRects[i].y)}

        for i, room in enumerate(self.medRooms):
            for y, row in enumerate(room):
                for x, tile in enumerate(row):
                    string = f'{x + self.medRoomsRects[i].x};{y + self.medRoomsRects[i].y}'
                    point = round((tile - int(tile)) * 10)
                    if tile == 8.2:
                        tile = 12
                        point = 0
                    tile = int(tile)
                    if string in self.tilemap.tileMap and (self.tilemap.tileMap[string]['type'] == 'floorTiles' or tile == 7):
                        tile = 11
                    else:
                        # if string in self.tilemap.tileMap and tile == 1:
                        if string in self.tilemap.tileMap and (self.tilemap.tileMap[string]['type'] == 'floorTiles' or tile == 7):
                            tile = 6
                        elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 1 and tile == 7:
                            tile = 13
                        self.tilemap.tileMap[string] = {'type': tileDict[tile][0], 'variant': tileDict[tile][1], 'rotation': 90 * point, 'pos': (x + self.medRoomsRects[i].x, y + self.medRoomsRects[i].y)}

        for rect in self.hallwaysHoriz:
            for x in range(1, rect.width):

                for y in range(1, rect.height):

                    string = str(x + rect.x) + ';' + str(y + rect.y)
                    if (string in self.tilemap.tileMap and (self.tilemap.tileMap[string]['type'] == 'floorTiles' or self.tilemap.tileMap[string]['type'] == 'walls')):
                        pass
                    elif y == 1:

                        if (string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 1 and self.tilemap.tileMap[string]['rotation'] == 180):
                            self.tilemap.tileMap[string] = {'type': 'bricks',
                                                            'variant': 5,
                                                            'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y),
                                                            'flip': True
                                                            }

                        if (string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 4):
                            self.tilemap.tileMap[string] = {'type': 'bricks',
                                                            'variant': 0,
                                                            'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y),
                                                            'flip': False
                                                            }

                        elif (string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 1 and self.tilemap.tileMap[string]['rotation'] == 0):
                            self.tilemap.tileMap[string] = {'type': 'bricks',
                                                            'variant': 5,
                                                            'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y),
                                                            'flip': False
                                                            }

                        elif x == 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 2,
                                                                                             'rotation': 0, 'pos': (x + rect.x, y + rect.y)}
                        elif x == rect.width - 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 2,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y), 'flip': True}
                        else:
                            if str(x + rect.x) + ';' + str(y + rect.y + 1):
                                pass
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 0,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                    elif y == 2:

                        if x == 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 1,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                        elif x == rect.width - 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 1,
                                                                                             'rotation': 180, 'pos': (
                                x + rect.x, y + rect.y)}
                        else:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'walls',
                                                                                             'variant': 0,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                    elif y == 3:
                        if x == 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 1,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                        elif x == rect.width - 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 1,
                                                                                             'rotation': 180, 'pos': (
                                x + rect.x, y + rect.y)}
                        else:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'walls',
                                                                                             'variant': 0,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                    elif y == 7:
                        if string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 1:
                            self.tilemap.tileMap[string] = {'type': 'bricks',
                                                            'variant': 6,
                                                            'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y),
                                                            }
                        elif x == 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 3,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                        elif x == rect.width - 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 7,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                        else:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 6,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                    else:
                        if f'{x};{y}' in self.tilemap.tileMap:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'floorTiles',
                                                                                             'variant': 0,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}

                        elif x == 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 1,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}
                        elif x == rect.width - 1:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'bricks',
                                                                                             'variant': 1,
                                                                                             'rotation': 180, 'pos': (
                                x + rect.x, y + rect.y)}
                        else:
                            self.tilemap.tileMap[str(x + rect.x) + ';' + str(y + rect.y)] = {'type': 'floorTiles',
                                                                                             'variant': 0,
                                                                                             'rotation': 0, 'pos': (
                                x + rect.x, y + rect.y)}

        for rect in self.hallwaysVert:
            for y in range(1, rect.height):
                for x in range(1, rect.width):
                    string = str(x + rect.x) + ';' + str(y + rect.y)
                    if (string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'floorTiles'):
                        pass
                    elif x == 1:

                        if string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'walls' and \
                                self.tilemap.tileMap[string]['variant'] == 0:
                            pass
                        elif (string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 0):
                              self.tilemap.tileMap[string] = {'type': 'bricks',
                                                            'variant': 5,
                                                            'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y),
                                                            'flip': False
                                                            }
                        elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and \
                                self.tilemap.tileMap[string]['variant'] == 1:
                            pass
                        elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and \
                                self.tilemap.tileMap[string]['variant'] == 0:
                            self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 5, 'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y), 'flip': False}
                        elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and \
                                self.tilemap.tileMap[string]['variant'] == 1:
                            self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 6, 'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y), 'flip': False}
                        elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and \
                                self.tilemap.tileMap[string]['variant'] == 6:
                            pass
                        elif y == 0:
                            if string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'walls' and self.tilemap.tileMap[string]['variant'] == 0:
                                pass
                            else:
                                if string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 0:
                                    self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 5, 'rotation': 0, 'pos': (x + rect.x, y + rect.y)}
                                if y == rect.height - 1:
                                    self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 2, 'rotation': 180, 'pos': (x + rect.x, y + rect.y)}
                                else:
                                    self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 1, 'rotation': 0, 'pos': (x + rect.x, y + rect.y)}

                        elif y == rect.height - 1:
                            self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 1, 'rotation': 0, 'pos': (x + rect.x, y + rect.y)}
                        else:
                            self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 1, 'rotation': 0, 'pos': (x + rect.x, y + rect.y)}
                    elif x == 5:


                        if string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'walls' and self.tilemap.tileMap[string]['variant'] == 0:
                            pass

                        elif string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 0:
                            self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 5, 'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y), 'flip': True}

                        elif (string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 1 and 'flip' in self.tilemap.tileMap[string] and self.tilemap.tileMap[string]['flip']):
                            self.tilemap.tileMap[string] = {'type': 'bricks',
                                                            'variant': 8,
                                                            'rotation': 0,
                                                            'pos': (x + rect.x, y + rect.y),
                                                            'flip': False
                                                            }
                        elif (string in self.tilemap.tileMap and self.tilemap.tileMap[string]['type'] == 'bricks' and self.tilemap.tileMap[string]['variant'] == 6):
                            pass
                        else:
                            if y == rect.height - 1:
                                self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 1, 'rotation': 180, 'pos': (x + rect.x, y + rect.y)}
                            else:
                                self.tilemap.tileMap[string] = {'type': 'bricks', 'variant': 1, 'rotation': 180, 'pos': (x + rect.x, y + rect.y)}
                    else:
                        self.tilemap.tileMap[string] = {'type': 'floorTiles', 'variant': 0, 'rotation': 0, 'pos': (x + rect.x, y + rect.y)}




    def draw(self, surf):
        for rect in self.medRoomsRects:
            pygame.draw.rect(surf, (0, random.randint(0, 255), 0), rect)
        for rect in self.mainRoomRects:
            pygame.draw.rect(surf, (random.randint(0, 255), 0, 0), rect)

        for rect in self.hallwaysVert:
            pygame.draw.rect(surf, (0, 255, 255), rect)
        for rect in self.hallwaysHoriz:
            pygame.draw.rect(surf, (0, 255, 255), rect)

        for u, v in self.hallwaysGraph.edges:
            pygame.draw.line(surf, (0, 0, 255), u, v, 2)