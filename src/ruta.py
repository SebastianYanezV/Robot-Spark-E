from heapq import heappop, heappush
import math
from utils import *

# Clase de utilidad para el algoritmo de ruta A*
class Nodo:
    def __init__(self, x, y, g=0, h=0, padre=None):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = g + h
        self.padre = padre

    def __lt__(self, otro):
        return self.f < otro.f

# Clase con el mapa del robot
class Ruta():
    posX: int
    posY: int
    dir: tuple
    dimension: int
    mapa: list

    def __init__(self):
        self.dimension = 5
        self.posX = self.dimension // 2
        self.posY = self.dimension // 2
        self.dir = Direcciones.U.value
        self.mapa = [None] * self.dimension
        for i in range(self.dimension):
            self.mapa[i] = [Marca.D] * self.dimension
        self.mapa[self.posX][self.posY] = Marca.C

    def print_mapa(self):
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.posX == i and self.posY == j:
                    print("X", end=" ")
                elif self.mapa[i][j] in [Marca.C, Marca.T_M, Marca.G_M]:
                    print("O", end=" ")
                elif self.mapa[i][j] in [Marca.O, Marca.T_A, Marca.G_A] :
                    print("0", end=" ")
                else:
                    print("U", end=" ")
            print() 
                

    def redimensionar(self):
        new_dimension = self.dimension * 5
        new_mapa = [None] * new_dimension
        for i in range(new_dimension):
            new_mapa[i] = [Marca.D] * new_dimension

        desplazamiento = (new_dimension//2) - (self.dimension//2)
        for i in range(self.dimension):
            for j in range(self.dimension):
                new_mapa[i+desplazamiento][j+desplazamiento] = self.mapa[i][j]
        self.posX += desplazamiento
        self.posY += desplazamiento

        self.mapa = new_mapa
        self.dimension = new_dimension
    
    def mover(self, direccion: tuple):
        self.posX += direccion[0]
        self.posY += direccion[1]
        self.dir = direccion
        if self.posX == 1 or self.posX == self.dimension-2 or self.posY == 1 or self.posY == self.dimension-2:
            self.redimensionar()
    
    def marcar(self, marca, posX = None, posY = None):
        if posX == None:
            posX = self.posX
        if posY == None:
            posY = self.posY
        self.mapa[posX][posY] = marca

    def casillas_cercanas(self):
        casillas_cercanas = []
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.mapa[i][j] == Marca.D:
                    distancia = self.heuristica(self.posX, self.posY, i, j)
                    heappush(casillas_cercanas, (distancia, (i, j)))
        return casillas_cercanas

    def heuristica(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    
    def es_valido(self, x, y, objetivo):
        if 0 <= x < self.dimension and 0 <= y < self.dimension:
            if (objetivo == "explorar"): # restringir los vecinos que quedan atrás del robot
                return (self.mapa[x][y] != Marca.O and
                         self.mapa[x][y] != Marca.G_A and 
                         self.mapa[x][y] != Marca.T_A)
            if (objetivo == "volver"):
                return (self.mapa[x][y] == Marca.C or
                         self.mapa[x][y] == Marca.G_M or 
                         self.mapa[x][y] == Marca.T_M)
        return False
    
    def vecinos(self, nodo, objetivo):
        movimientos = [
            #(-1, -1), (-1, 1), (1, -1), (1, 1),  # Movimientos diagonales
            (-1, 0), (1, 0), (0, -1), (0, 1)  # Movimientos rectos
        ]
        resultado = []
        for mov in movimientos:
            nx, ny = nodo.x + mov[0], nodo.y + mov[1]
            if self.es_valido(nx, ny, objetivo):
                resultado.append((nx, ny))
        return resultado
    
    def reconstruir_camino(self, nodo):
        camino = []
        actual = nodo
        while actual is not None:
            camino.append((actual.x, actual.y))
            actual = actual.padre
        return camino[::-1]
        
    def A_star(self, posX_destino, posY_destino, posX_origen = None, posY_origen = None, objetivo = "volver"):
        if posX_origen == None:
            posX_origen = self.posX
        if posY_origen == None:
            posY_origen = self.posY
        open_list = []
        closed_list = set()
        nodo_inicial = Nodo(posX_origen, posY_origen, 0, self.heuristica(posX_origen, posY_origen, posX_destino, posY_destino))
        heappush(open_list, nodo_inicial)

        while open_list:
            nodo_actual = heappop(open_list)
            if (nodo_actual.x, nodo_actual.y) in closed_list:
                continue

            if nodo_actual.x == posX_destino and nodo_actual.y == posY_destino:
                return self.reconstruir_camino(nodo_actual)

            closed_list.add((nodo_actual.x, nodo_actual.y))
            for vecino in self.vecinos(nodo_actual, objetivo):
                vecino_x, vecino_y = vecino
                if (vecino_x, vecino_y) in closed_list:
                    continue

                costo_movimiento = math.sqrt(2) if abs(vecino_x - nodo_actual.x) == 1 and abs(vecino_y - nodo_actual.y) == 1 else 1
                g_nuevo = nodo_actual.g + costo_movimiento
                h_nuevo = self.heuristica(vecino_x, vecino_y, posX_destino, posY_destino)
                nodo_vecino = Nodo(vecino_x, vecino_y, g_nuevo, h_nuevo, nodo_actual)
                heappush(open_list, nodo_vecino)

        return None  # No se encontró una ruta
    
    def ruta_casilla_cercana(self):
        cercanas = self.casillas_cercanas()
        while(len(cercanas) > 0):
            mas_cercana = heappop(cercanas)[1]
            ruta_mas_cercana = self.A_star(mas_cercana[0], mas_cercana[1], objetivo = "explorar")
            if ruta_mas_cercana != None:
                return ruta_mas_cercana
        
        return None # No se encontró una ruta
        
