import math

def distancia(vect1, vect2):
    v = vect1 - vect2
    return math.sqrt(v.x ** 2 + v.y **2)

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
    
    def __add__(self, otro_vector):
        return Vector2(self.x + otro_vector.x, self.y + otro_vector.y)
    
    def __mul__(self, escalar):
        return Vector2(self.x * escalar, self.y * escalar)
    
    def __truediv__(self, escalar):
        return Vector2(self.x / escalar, self.y / escalar)
    
    def __sub__(self, otro_vector):
        return Vector2(float(self.x) - float(otro_vector.x), float(self.y) - float(otro_vector.y))
    
    def __str__(self):
        return f"({self.x}, {self.y})" 

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