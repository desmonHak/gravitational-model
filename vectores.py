import math
from decimal import Decimal, getcontext
import numpy as np

def distancia(vect1, vect2):
    v = vect1 - vect2
    return math.sqrt(v.x ** 2 + v.y **2)

def Decimal_distancia(vect1, vect2):
    v = vect1 - vect2
    return Decimal(math.sqrt(v.x ** 2 + v.y **2))

def verificar_cercania(vect_comprovar, vect2, discrepancia):
    if float(vect_comprovar.x) - discrepancia <= float(vect2.x) and float(vect_comprovar.x) + discrepancia >= float(vect2.x):
        if float(vect_comprovar.y) - discrepancia <= float(vect2.y) and float(vect_comprovar.y) + discrepancia >= float(vect2.y):
            return True
        else:
            return False
    else:
        return False

class Vector2:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    
    def magnitud(self):
        return Decimal(math.sqrt(self.x ** 2 + self.y ** 2))
    
    def __add__(self, otro_vector):
        return Vector2(Decimal(self.x) + Decimal(otro_vector.x), Decimal(self.y) + Decimal(otro_vector.y))
    
    def __mul__(self, escalar):
        return Vector2(Decimal(self.x) * Decimal(escalar), Decimal(self.y) * Decimal(escalar))
    
    def __truediv__(self, escalar):
        return Vector2(self.x / Decimal(escalar), self.y / Decimal(escalar))
    
    def __sub__(self, otro_vector):
        return Vector2(Decimal(self.x) - Decimal(otro_vector.x), Decimal(self.y) - Decimal(otro_vector.y))
    
    def __str__(self):
        return f"({self.x}, {self.y})" 

class Casillero:
    '''Contiene los datos de un casillero'''
    
    def __init__(self, posicion, valor, masa):
        self.posicion = posicion
        self.valor = valor
        self.masa = masa
        
    def centro_de_masa(self):
        # Inicializar variables para el numerador en 2D
        numerador_x = 0
        numerador_y = 0
        
        # Calcular el numerador en 2D
        for i in self.valor:
            numerador_x += i.masa * i.posicion.x
            numerador_y += i.masa * i.posicion.y

        # Calcular el centro de masa en 2D
        masas = [a.masa for a in self.valor]
        denominador = sum(masas)
        centro_de_masa = Vector2(numerador_x / denominador, numerador_y / denominador)

        return centro_de_masa

class Grid:
    '''Una grid infinita
    =====
    
    la grid funciona de la siguiente manera:
    grid = {
        (pos_x,pos_y): valor_en_ese_punto,
        (pos_x2,pos_y2): valor_en_ese_punto2,
        (pos_x3,pos_y3): valor_en_ese_punto3
    }
    
    ------
    get_value:
    ------
    retornar el valor en la posicion (si no hay un valor asignado para la posicion se devuelve None)
    
    ------
    set_value:
    ------
    el valor en una posicion va ser igual a el valor otorgado
    
    ------
    calcular_posicion:
    ------
    Devuelve la posicion en la grid teniendo en cuenta el tamaño de cada cuadrado
    
    ------
    añadir_un_valor_a_la_posicion:
    ------
    Esta funcion te permite hacer un .append a una lista que se encuentre en la posicion
    si no existe la posicion se crea esa posicion y se le asigna el valor
    
    Usar solo si el tipo de valor asignado es una lista o no existe ningun valor en la posicion
    '''
    
    def __init__(self, filas, columnas, tamaño):
        self.filas = filas
        self.columnas = columnas
        
        # el tamaño de cada cuadrado va ser igual al la cantidad de columnas que hay en una porcion determinada
        # (en el caso de la gravedad se usa el rango de vicion inical)
        self.tamaño = tamaño / columnas
        
        # crear la cuadricula vacia
        self.grid = {}
        
        # la grid funciona de la siguiente manera:
        # grid = {
        #    (pos_x,pos_y): valor_en_ese_punto,
        #    (pos_x2,pos_y2): valor_en_ese_punto2,
        #    (pos_x3,pos_y3): valor_en_ese_punto3
        # }
        
        # para acceder a un valor y modificarlo se 
    
    # funcion para obtener el valor de la grid en una posicion
    def get_value(self, posicion):
        '''retornar el valor en la posicion (si no hay un valor asignado para la posicion se devuelve None)'''
        return self.grid.get((posicion.x, posicion.y), None)
    
    # asignar el valor a una posicion
    def set_value(self, posicion, value):
        '''el valor en una posicion va ser igual a el valor otorgado'''
        self.grid[(posicion.x, posicion.y)] = value
    
    def actualizar(self, objetos):
        self.grid.clear()
        
        for objeto in objetos:
            posicion = self.calcular_posicion(objeto.posicion)
            self.añadir_un_valor_a_la_posicion(posicion,objeto)
    
    
    # hacer un .append
    def añadir_un_valor_a_la_posicion(self, posicion, valor):
        '''Esta funcion te permite hacer un .append a una lista que se encuentre en la posicion
        si no existe la posicion se crea esa posicion y se le asigna el valor
        
        Usar solo si el tipo de valor asignado es una lista o no existe ningun valor en la posicion
        ----
        '''
        if (posicion.x,posicion.y) in self.grid:
            self.grid[(posicion.x,posicion.y)].append(valor)
        else:
            self.set_value(posicion,[valor])
    
    # devolver todas las posiciones de un modo iterable
    def get_all(self):
        '''retornar una lista iterable de todas las posiciones'''
        todos = []
        for key, value in self.grid.items():
            masa = 0
            for i in self.get_value(Vector2(key[0],key[1])):
                masa += i.masa
                
        for key, value in self.grid.items():
            nuevo = Casillero(Vector2(key[0], key[1]), value, masa)
            todos.append(nuevo)
        
        return todos
    
    def calcular_posicion(self,posicion):
        '''Devuelve la posicion en la grid teniendo en cuenta el tamaño de cada cuadrado'''
        tamaño_decimal = Decimal(str(self.tamaño))
        # Calcular el índice de la fila y columna en la que se encuentra el objeto
        fila = int(posicion.y.to_integral_value() // tamaño_decimal)
        columna = int(posicion.x.to_integral_value() // tamaño_decimal)
        return Vector2(columna, fila)

class plano_vectorial:
    def __init__(self,x_min,y_min, x_max, y_max):
        self.x = (x_min, x_max)
        self.y = (y_min, y_max)
    
    def dividir_en_chuncks(self, cantidad):
        tamaño_x = abs(self.x[0] - self.x[1]) / cantidad[0]
        tamaño_y = abs(self.x[0] - self.x[1]) / cantidad[1]
        
        return Vector2(tamaño_x, tamaño_y)
    
    def __str__(self):
        return f"P[x = {self.x}, y = {self.y}]" 