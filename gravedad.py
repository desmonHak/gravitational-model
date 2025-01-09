
# ----------------- importar librerias --------------------- 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from math import *
from vectores import *
from funciones_extra import *
import time
import random
import colorsys
import json
import os
import sys
import ctypes
import numpy as np
from decimal import Decimal, getcontext

# habilitar el soporte de colores ANSI en la consola de Windows
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# precisión de los datos
getcontext().prec = 250

class Universo:
    def __init__(self, fisica, grid_h, grid_m, grid_l, grid_hh):
        self.fisica = fisica
        self.grid_h = grid_h 
        self.grid_hh = grid_hh
        self.grid_m = grid_m
        self.grid_l = grid_l

class Fisica:
    def __init__(self, g) -> None:
        self.g = g
    
    def gravedad(self, cuerpo_a, cuerpo_b):
        '''devuelve el vector de la fuerza que reciven los cuerpos'''
        # calcular la fuerza usando la formula de newton
        fuerza_total = self.g*((cuerpo_a.masa * cuerpo_b.masa) / (Decimal_distancia(cuerpo_a.posicion, cuerpo_b.posicion) ** 2))
        
        # calcular el vector de la direccion usando trigonometria
        ang = atan2(cuerpo_a.posicion.y - cuerpo_b.posicion.y, cuerpo_a.posicion.x - cuerpo_b.posicion.x)
        fuerza_x = fuerza_total * Decimal(cos(ang))
        fuerza_y = fuerza_total * Decimal(sin(ang))
        
        return Vector2(fuerza_x, fuerza_y)
    
    def calcular_velocidad_orbital(self, cuerpo_central, cuerpo_orbiando):
        v = Decimal(math.sqrt((self.g * cuerpo_central.masa)/ Decimal_distancia(cuerpo_central.posicion, cuerpo_orbiando.posicion)))
        return v
        
    def calcular_aceleracion(self, fueza_aplicada, masa, tiempo):
        '''aplicar la formula F = ma'''
        aceleracion  = fueza_aplicada / masa
        # se suma la velocidad a la velocidad previa anterior
        return aceleracion * tiempo
    
    # ------------- Kepler
    def período_orbital(self, masa, semieje_mayor):
        # print(semieje_mayor)
        T = 2*math.pi * (math.sqrt((float(semieje_mayor) ** 3) / float((self.g * masa))))
        return T
    
    def anomalía_media(self, masa, semieje_mayor, tiempo):
        T = self.período_orbital(masa, semieje_mayor)
        M = ((2 * math.pi) / T) * tiempo
        return M
    
    def resolver_kepler(self, M, e, tol=1e-6):
        E = M  # Primera aproximación
        while True:
            E_new = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
            if abs(E_new - E) < tol:
                break
            E = E_new
        return E
    
    def anomalia_verdadera(self, E, excentricidad):
        tan_nu_2 = math.sqrt((1 + excentricidad) / (1 - excentricidad)) * math.tan(E / 2)
        nu = 2 * math.atan(tan_nu_2) 
        return nu

    def posicion_orbital_simple(self,cuerpo, tiempo):
        masa = cuerpo.cuerpo_que_orbita.masa
        semieje_mayor = cuerpo.semieje_mayor
        excentricidad = cuerpo.excentricidad
        
        M = self.anomalía_media(masa, semieje_mayor, tiempo)
        E = self.resolver_kepler(M, excentricidad)
        r = Decimal(semieje_mayor) * Decimal((1 - excentricidad * math.cos(E)))
        angulo = self.anomalia_verdadera(E, excentricidad)
        
        x = Decimal(r * Decimal(math.cos(angulo + cuerpo.velocidad.y)))
        y = Decimal(r * Decimal(math.sin(angulo + cuerpo.velocidad.y)))
        return Vector2(x,y)

    def posicion_orbital_completa(self, cuerpo, tiempo):
        masa = cuerpo.cuerpo_que_orbita.masa
        semieje_mayor = cuerpo.semieje_mayor
        excentricidad_vectorial = cuerpo.excentricidad  # Ahora es un vector
        e_magnitud = np.linalg.norm(excentricidad_vectorial)  # Magnitud de la excentricidad
        periapsis_direccion = excentricidad_vectorial / e_magnitud  # Vector unitario hacia el periapsis
        mu = self.g * masa  # Parámetro gravitacional estándar
        
        # Anomalía media
        M = self.anomalía_media(masa, semieje_mayor, tiempo)
        
        # Ecuación de Kepler
        E = self.resolver_kepler(M, e_magnitud)
        
        # Anomalía verdadera
        nu = self.anomalia_verdadera(E, e_magnitud)
        
        # Semilatus rectum
        p = semieje_mayor * (1 - e_magnitud ** 2)
        
        # Distancia radial
        r = p / (1 + e_magnitud * math.cos(nu))
        
        # Coordenadas en el plano orbital
        x_orb = r * math.cos(nu)
        y_orb = r * math.sin(nu)
        
        # Rotación al sistema global
        # Ángulo de rotación basado en la dirección del periapsis
        rotacion = np.array([[periapsis_direccion[0], -periapsis_direccion[1]],
                            [periapsis_direccion[1], periapsis_direccion[0]]])
        
        # Posición global
        posicion_global = np.dot(-rotacion, np.array([x_orb, y_orb]))
        
        return Vector2(Decimal(posicion_global[0]), Decimal(posicion_global[1]))
    def posicion_y_velocidad_relativas(self, planeta, luna):
        pos = np.array([float(planeta.posicion.x - luna.posicion.x), float(planeta.posicion.y - luna.posicion.y), 0])
        vel = np.array([float(planeta.velocidad.x - luna.velocidad.x), float(planeta.velocidad.y - luna.velocidad.y), 0])
        return pos, vel
    def pgr(self, luna, planeta):
        return float(self.g * (luna.masa + planeta.masa))
    def momento_angular(self, posicion, velocidad):
        return np.cross(posicion, velocidad)
    def excentricidad(self, velocidad, posicion, momento_angular, pgr):
        # e = (np.cross(velocidad, np.cross(posicion, velocidad))/pgr) - posicion / np.linalg.norm(posicion)
        p = (np.cross(velocidad, momento_angular)) - pgr * ( posicion / np.linalg.norm(posicion) )
        e = (1 / pgr) * p 
        print(f"e = {e}")
        return e
    def energia_especifica(self, velocidad, posicion, pgr):
        ee = ((np.linalg.norm(velocidad) ** 2) / 2) - pgr / np.linalg.norm(posicion)
        return ee
    def semieje_mayor(self,energia_especifica,pgr):
        a = - (pgr /(2*energia_especifica))
        return a
    def velocidad_en_orbita(self,exentricidad, semieje_mayor, pgr):
        pass
        # velocidad = math.sqrt(pgr*((2/distancia)*(1/semieje_mayor)))
        # v_tag = velocidad * 
        # ang = math.atan2(posicion[1], posicion[0])
        # dot_product = np.dot(posicion, velocidad)
        
        # ang2 = np.arccos(dot_product/(np.linalg.norm(posicion)*np.linalg.norm(velocidad)))
        # p = math.sqrt(pgr*(2 / np.linalg.norm(posicion) -1 / semieje_mayor))
        # v_r = p * math.cos(ang2)
        # v_t = p * math.sin(ang2)
        # v_x = v_r * math.cos(ang) - v_t * math.sin(ang)
        # v_y = v_r * math.sin(ang) - v_t * math.cos(ang)
        # return np.array([v_x, v_y])

# ---------------------- Crear la clase Cuerpo ----------------------------
class Cuerpo:
    # inicializar variables
    def __init__(self, nombre, posicion, velocidad, masa, diam = None, exact = True):
        self.nombre = nombre
        self.posicion = posicion
        self.velocidad = velocidad
        self.masa = Decimal(masa)
        # establecer una tag aleatoria
        self.tag = crear_string_random(5)
        # establecer un color aleatorio
        self.color = colorsys.hsv_to_rgb(random.uniform(0,1),1,1)
        self.diametro = diam
        self.exact = exact
        self.posiciones = []

        if diam != None:
            self.diametro = diam
        else:
            self.diametro = float(masa) * dot_scale
    
    def guardar_pos(self):
        self.posiciones.append(self.posicion)
    
    # funcion para aplicar una fuerza
    def aplicar_fuerza(self, fuerza_aplicada, tiempo):
        # aplicar la formula F = ma
        velocidad_r = universo.fisica.calcular_aceleracion(fuerza_aplicada, self.masa, tiempo)
        # sumar la velocidad
        self.velocidad = self.velocidad + velocidad_r
    
    # funcion para aplicar la gravedad
    def aplicar_gravedad(self, otro, delta_time):
        # calcular la gravedad
        fuerza = universo.fisica.gravedad(self, otro)
        
        # aplicar la fuerza obtenida al otro
        otro.aplicar_fuerza(Vector2(fuerza.x, fuerza.y), delta_time)
        
        # aplicar la fuerza obtenida a el mismo
        self.aplicar_fuerza(Vector2(fuerza.x, fuerza.y) * -1, delta_time)
    
    # funcion para calcular la posición del objeto en cada momento
    def constante(self, delta_time):
        # mover lo que indica la velocidad que tiene multiplicado por el tiempo que tarda cada frame
        self.posicion += self.velocidad * delta_time
        self.guardar_pos()

class Cuerpo_anillo(Cuerpo):
    def __init__(self, nombre, posicion, velocidad, masa, orbita, excentricidad, semieje_mayor, diam=None, exact=True):
        super().__init__(nombre, posicion, velocidad, masa, diam, exact)
        self.cuerpo_que_orbita = orbita
        self.excentricidad = excentricidad
        self.semieje_mayor = semieje_mayor

class Cuerpo_luna(Cuerpo):
    def __init__(self, nombre, posicion, velocidad, masa, cuerpo_que_orbita, diam=None, exact=True):
        super().__init__(nombre, posicion, velocidad, masa, diam, exact)
        self.cuerpo_que_orbita = cuerpo_que_orbita
        self.semieje_mayor = None
        self.excentricidad = None
        self.posicion_inicial = posicion
        self.posicion_relativa_a_orbita = Vector2(0,0)
        self.velocidad_relativa_a_orbita = Vector2(0,0)
    
    def calcular_orbita(self, fisica):
        posicion, velocidad = fisica.posicion_y_velocidad_relativas(self.cuerpo_que_orbita, self)
        pgr = fisica.pgr(self, self.cuerpo_que_orbita)
        energia_especifica = fisica.energia_especifica(velocidad, posicion,pgr)
        momento = fisica.momento_angular(posicion, velocidad)
        self.semieje_mayor = fisica.semieje_mayor(energia_especifica, pgr)
        
        # self.exentricidad = np.linalg.norm(fisica.excentricidad(velocidad,posicion, momento, pgr))
        self.excentricidad = fisica.excentricidad(velocidad,posicion, momento, pgr)
    # funcion para aplicar una fuerza
    def aplicar_fuerza(self, fuerza_aplicada, tiempo):
        # aplicar la formula F = ma
        velocidad_r = universo.fisica.calcular_aceleracion(fuerza_aplicada, self.masa, tiempo)
        # sumar la velocidad
        self.velocidad_relativa_a_orbita += velocidad_r
    # funcion para aplicar la gravedad
    def aplicar_gravedad(self, otro, delta_time, doble):
        # calcular la gravedad
        fuerza = universo.fisica.gravedad(self, otro)
        
        # aplicar la fuerza obtenida a el mismo
        self.aplicar_fuerza(Vector2(fuerza.x, fuerza.y) * -1, delta_time)
        
        if doble:
            # aplicar la fuerza obtenida al otro
            otro.aplicar_fuerza(Vector2(fuerza.x, fuerza.y), delta_time)
            
        
    def constante(self, delta_time):
        # mover lo que indica la velocidad que tiene multiplicado por el tiempo que tarda cada frame
        self.posicion_relativa_a_orbita += self.velocidad_relativa_a_orbita * delta_time
        self.posicion = self.posicion_inicial + self.posicion_relativa_a_orbita
        self.guardar_pos()

# -------------------- Clase para visualizar los puntos --------------------------------
class Puntos:
    # inicializar las variables
    def __init__(self):
        # lista con los cuerpos que tiene que visualizar
        self.cuerpos = []
        # crear las variables para la ventana y los ejes
        self.fig, self.ax = plt.subplots()

        # establecer la variable para el grafico de dispersión
        self.scatter = self.ax.scatter([], [])
        
        # establecer el tamaño que muestran los ejes
        self.ax.set_xlim(view_scale.x * -1, view_scale.x) # x
        self.ax.set_ylim(view_scale.y * -1, view_scale.y) # y
        
        # establecer el color de fondo del grafico a negro
        self.ax.set_facecolor('black')
        # establecer el color de fondo de la ventana a negro
        self.fig.patch.set_facecolor('black')
        
        # ajustar la visualizacion para que 1 unidad en X mida lo mismo en la pantalla que 1 unidad en Y
        self.ax.set_aspect('equal', adjustable='datalim')
        
        # cambiar el color de los ejes a gris
        self.ax.tick_params(axis='x', colors='gray')
        self.ax.tick_params(axis='y', colors='gray')
        
        # cambiar el color del recuadro a gris
        for spine in self.ax.spines.values():
            spine.set_color('gray')
        
        self.multiplicador_de_tiempo = 1
        
        # activar el modo interactivo en el grafico
        plt.ion()
        
        # crear una animacion
        self.ani = FuncAnimation(self.fig, self.actualizar_grafico, interval=16.7 /2, frames=60)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_key(self, event):
        print(f"Tecla presionada: {event.key}")
        
        
        move_factor = 2
        # Lógica para manejar diferentes teclas
        if event.key == 'escape':  # Si se presiona la tecla ESC
            exit()
        elif event.key == '+':  # Mover hacia la izquierda
            if self.multiplicador_de_tiempo < 5:
                self.multiplicador_de_tiempo *= move_factor
                if self.multiplicador_de_tiempo == 0:
                    self.multiplicador_de_tiempo = 0.001
            else:
                self.multiplicador_de_tiempo = 5
                print("--------------------------------- tiempo maximo -------------------------------")
        elif event.key == '-':  # Mover hacia la derecha
            if self.multiplicador_de_tiempo > 0.001:
                self.multiplicador_de_tiempo /= move_factor
            else:
                self.multiplicador_de_tiempo = 0
                print("--------------------------------- tiempo minimo -------------------------------")
                
    # agregar varios cuerpos
    def agregar_cuerpos(self, cuerpos):
        for item in cuerpos:
            self.cuerpos.append(item)

    # funcion para actualizar el grafico
    def actualizar_grafico(self):
        # establecer las variables que se van a usar en el grafico
        xs, ys, nombres, pres = zip(*[(i.posicion.x, i.posicion.y, i.nombre, i.exact) for i in self.cuerpos])
        # actualizar las posiciones
        self.scatter.set_offsets(list(zip(xs, ys)))
        
        # Eliminar etiquetas anteriores
        for annotation in self.ax.texts:
            annotation.remove()
        
        # Mostrar etiquetas en blanco en cada punto
        for x, y, nombre, pre in zip(xs, ys, nombres, pres):
            if pre == True:
                self.ax.annotate(nombre, (x, y), ha='center', va='top', color='white', fontsize=8, xytext=(0, -10), textcoords='offset points')
    
        # mostrar cambios
        self.fig.canvas.get_tk_widget().update()
        
    def iniciar_animacion(self):
        plt.show()
        
        diametros, colores = zip(*[(i.diametro, i.color) for i in self.cuerpos])

        # actualizar las diametros
        self.scatter.set_sizes(list(diametros))
        # actualizar el color
        self.scatter.set_color(list(colores))

class Anillo:
    def __init__(self, planeta, distancia_min, distancia_max, cantidad, masa):
        self.planeta = planeta
        self.distancia_min = distancia_min
        self.distancia_max = distancia_max
        self.masa = Decimal(masa)
        self.cantidad = cantidad
        # establecer una tag aleatoria
        self.tag = crear_string_random(5)
    
    def crear_cuerpos_anillo(self):
        cuerpos = list()
        for i in range(self.cantidad):
            pos = Vector2(random.uniform(self.distancia_min, self.distancia_max), random.uniform(0, 2 * math.pi))
            cuerpo = Cuerpo_anillo(str(i), Vector2(Decimal(1),Decimal(1)), pos, self.masa, self.planeta, random.uniform(0, 0.1), pos.x, diam=3, exact=False)
            
            print(cuerpo)
            cuerpos.append(cuerpo)
            
        print(cuerpos)
        return cuerpos
    def __str__(self):
        return f"Anillo(tag = '{self.tag}', distancia min = '{self.distancia_min}', distancia max = '{self.distancia_max}', masa de los cuerpos = '{self.masa}', cantida = '{self.cantidad}')"

def simular_aproximados(todos):
    for i, pos in enumerate(todos):
        centro_de_masas = pos.centro_de_masa()
        este = Cuerpo(str(pos.posicion), centro_de_masas, Vector2(0,0), pos.masa)
        
        cantidad = len(pos.valor)
        for otro in todos_los_cuerpos:
            fuerza = universo.fisica.gravedad(este, otro)
            f_real = fuerza * -1 / cantidad
            
            for cuerpo in pos.valor:
                cuerpo.aplicar_fuerza(f_real,delta_time)
                # cuerpo.aplicar_fuerza(fuerza * -1,delta_time)
        # if print_:
        #     print(cantidad)
                
        for cuerpo in pos.valor:
            cuerpo.constante(delta_time)

# -------------------- funcion para pedir datos --------------------------
def pedir_dato(nombre_del_dato, tipo_de_dato, close = "exit", pass_command = False): # los tipos de datos van 0 = int; 1 = float; 2 = vector; 3 = string; 4 = Decimal; 5 = vector Decimal
    # pedir dato inicial
    dato = input(f'{c["verde"]} {nombre_del_dato} = {c["default"]}')
    
    # si el dato es igual a el comando de salida
    if dato == close:
        # retornar falso
        return False
    elif pass_command != False:
        if dato == pass_command:
            return None
    
    if tipo_de_dato == 3: # si el tipo de dato es una string
        # retornar el dato sin modificar
        return dato
    
    elif es_numero(dato): # si el dato otorgado por el usuario es un numero
        
        if tipo_de_dato == 0: # si el tipo de dato pedido es int
            # retornar el int del dato
            return int(dato)
        
        elif tipo_de_dato == 1: # si el tipo de dato pedido es float
            # retornar el float del dato
            return float(dato)
        
        elif tipo_de_dato == 4: # si el tipo de dato pedido es decimal
            # retornar el decimal del dato
            return Decimal(dato)
    
    elif tipo_de_dato == 2: # si el tipo de dato pedido era un vector 2 
        # separar el input por el ;
        vector = dato.split(";") 
        
        if len(vector) == 2: # si la cantidad de datos es 2
            if es_numero(vector[0]) and es_numero(vector[1]): # si ambos datos son numeros
                # retornar el vector 2
                return Vector2(float(vector[0]),float(vector[1]))
    
    elif tipo_de_dato == 5: # si el tipo de dato pedido era un vector 2 
        # separar el input por el ;
        vector = dato.split(";") 
        
        if len(vector) == 2: # si la cantidad de datos es 2
            if es_numero(vector[0]) and es_numero(vector[1]): # si ambos datos son numeros
                # retornar el vector 2
                return Vector2(Decimal(vector[0]),Decimal(vector[1]))

    
    
    # --- en caso de que nada de eso pase
    # indicar al usuario que el dato no es valido
    print_error(tipos_de_errores[0], mensaje_extra="El tipo de dato otorgado no es valido en este contexto")
    
    # volver a pedir los datos
    close_this = close
    tipo_de_dato_this = tipo_de_dato
    nombre_del_dato_this = nombre_del_dato
    return pedir_dato(nombre_del_dato_this, close=close_this, tipo_de_dato=tipo_de_dato_this)

# ------------ funcion para crear un cuerpo ----------------------------------------
def crear_cuerpo():
    # pedir el nombre
    nombre = pedir_dato("Nombre", tipo_de_dato=3)

    if nombre != False and nombre != None: # si el dato tiene un valor
        
        # pedir la masa
        masa = pedir_dato("Masa", tipo_de_dato=4)
        
        if masa != False and masa != None: # si el dato tiene un valor
            
            if masa > 0: # si la masa es mayor a 0
                
                # perdir la posicion 
                posicion = pedir_dato("posicion", tipo_de_dato=5)
                
                if posicion != False and posicion != None: # si el dato tiene un valor
                    
                    # pedir la velocidad
                    velocidad = pedir_dato("velocidad", tipo_de_dato=5)
                    
                    if velocidad != False and velocidad != None: # si el dato tiene un valor
                        
                        diametro = pedir_dato("diametro", tipo_de_dato=1, pass_command="")
                        if diametro != False: # si el dato tiene un valor
                            # indicar que se creo el cuerpo
                            print(f"se creo el cuerpo {nombre}, masa = {masa}, posicion = {posicion}, velocidad = {velocidad}")
                            
                            # crear cuerpo
                            cuerpo_creado = Cuerpo(nombre, posicion, velocidad, masa, diam=diametro)
                            print(cuerpo_creado.tag)
                            # añadir el cuerpo a la variable que contiene a todos
                            todos_los_cuerpos.append(cuerpo_creado)
            else: # si la masa es menor a 0
                # indicar el error
                print_error(tipos_de_errores[2], mensaje_extra="no se puede tener una masa negativa")
                # print("\x1b[1;31merror de input (no se puede tener una masa negativa){c["default"]}")

# ------------ funcion para crear un anillo ----------------------------------------
def crear_anillo(cuerpo_que_orbita):
    # pedir el nombre
    cantidad = pedir_dato("Cantidad de cuerpos", tipo_de_dato=0)

    if cantidad != False and cantidad != None: # si el dato tiene un valor
        
        # pedir la masa
        masa = pedir_dato("Masa de los cuerpos", tipo_de_dato=4)
        
        if masa != False and masa != None: # si el dato tiene un valor
            
            if masa > 0: # si la masa es mayor a 0
                
                # perdir la posicion 
                distancia_min = pedir_dato("Distancia minima", tipo_de_dato=1)
                
                if distancia_min != False and distancia_min != None: # si el dato tiene un valor
                    if distancia_min > 0: # si la masa es mayor a 0
                    
                        # pedir la velocidad
                        distancia_max = pedir_dato("Distancia maxima", tipo_de_dato=1)
                        
                        if distancia_max != False and distancia_max != None: # si el dato tiene un valor   
                            if distancia_max > distancia_min: # si la masa es mayor a 0
                                return Anillo(cuerpo_que_orbita, distancia_min,distancia_max,cantidad,masa)
                                
                            else: # si la distancia minima es menor a 0
                                # indicar el error
                                print_error(tipos_de_errores[2], mensaje_extra="La distancia maxima no puede ser menor a la minima")
                                # print("\x1b[1;31merror de input (no se puede tener una masa negativa){c["default"]}")
                    else: # si la distancia minima es menor a 0
                        # indicar el error
                        print_error(tipos_de_errores[2], mensaje_extra="no se puede tener una distancia negativa")
                        # print("\x1b[1;31merror de input (no se puede tener una masa negativa){c["default"]}")
            else: # si la masa es menor a 0
                # indicar el error
                print_error(tipos_de_errores[2], mensaje_extra="no se puede tener una masa negativa")
                # print("\x1b[1;31merror de input (no se puede tener una masa negativa){c["default"]}")

# ------------ funcion para crear un anillo ----------------------------------------
def crear_luna(cuerpo_que_orbita):
    # pedir el nombre
    nombre = pedir_dato("Nombre", tipo_de_dato=3)

    if nombre != False and nombre != None: # si el dato tiene un valor
        
        # pedir la masa
        masa = pedir_dato("Masa", tipo_de_dato=4)
        
        if masa != False and masa != None: # si el dato tiene un valor
            
            if masa > 0: # si la masa es mayor a 0
                
                # perdir la posicion 
                posicion = pedir_dato("Posicion Relativa", tipo_de_dato=5)
                
                if posicion != False and posicion != None: # si el dato tiene un valor
                    # pedir la velocidad
                    velocidad = pedir_dato("Velocidad Relativa", tipo_de_dato=5)
                        
                    if velocidad != False and velocidad != None: # si el dato tiene un valor   
                        return Cuerpo_luna(nombre, posicion + cuerpo_que_orbita.posicion, velocidad + cuerpo_que_orbita.velocidad, masa, cuerpo_que_orbita)
                        # return Cuerpo(nombre, posicion, velocidad, masa)
                                
            else: # si la masa es menor a 0
                # indicar el error
                print_error(tipos_de_errores[2], mensaje_extra="no se puede tener una masa negativa")
                # print("\x1b[1;31merror de input (no se puede tener una masa negativa){c["default"]}")


# Constante de gravitacion universal
g = Decimal('0.01')

# Modo de tiempo
time_mode = True # si es True se usa delta_time si es False es constante 
# valor de delta_time si el time_mode es false
uniform_time = 0.1

# escala de los puntos
dot_scale = 1

# escala del campo de vision
view_scale = Vector2(150,150)

# guardado de la simulacion
active_save = False
save_in = ""
ciclos = 1

# ------------ crear cuerpos -------------------------
todos_los_cuerpos = list()
todos_los_aproximados_hh = list()
todos_los_aproximados_h = list()
todos_los_aproximados_m = list()
todos_los_aproximados_l = list()

# ------------ asteroides -------------------------
cantidad_de_asteroides_0 = 0
cantidad_de_asteroides_1 = 0
cantidad_de_asteroides_2 = 0

# ------------ anillos -------------------------
todos_los_anillos = list()

sigue = True
print(f'''{c["azul"]}Este es el bucle de inicialiciacion de datos. Para obtener la informacion de los comandos escriba "help"
o visite https://github.com/pianistandcats/gravitational-model para mas informacion{c["default"]}''')
# ----------- bucle de personalizacion del usuario -----------------------
while sigue:
    # pedir input al usuario
    input_del_usuario = input('>>> ')
    # separar el input por palabras
    input_separado = input_del_usuario.split(" ")
    
    # ~~~~~~~~~~~~~~~~~~~~ si dice "run" ~~~~~~~~~~~~~~~~~~~~
    if input_del_usuario == "run":
        # se finaliza el bucle
        sigue = False
        break
    
    # ~~~~~~~~~~~~~~~~~~~~ si dice "help" ~~~~~~~~~~~~~~~~~~~~
    elif input_del_usuario == "help":
        # dar la informacion
        print(f"""{c["amarillo"]}add:{c["default"]} añadir un cuerpo
 - add moon [nombre del cuerpo] agrega una luna al cuerpo 
{c["amarillo"]}G:{c["default"]} constante de gravitacion universal
    ? muestra su valor actual
    = igualar a (valor siguiente a \"=\")
{c["amarillo"]}run:{c["default"]} empezar simulacion
{c["amarillo"]}cuerpos:{c["default"]} datos de los cuerpos
{c["amarillo"]}load:{c["default"]} cargar un archivo: load [nombre del archivo]
{c["amarillo"]}save:{c["default"]} guardar datos de los cuerpos: save [nombre del archivo]
{c["amarillo"]}time.mode:{c["default"]} asignar el tipo de tiempo que se va a usar
  - delta_time varia dependiendo de cuanto tarda entre frame y frame (automático)
  - uniform un valor constante cada frame
{c["amarillo"]}size:{c["default"]} valores de tamaños
  - dots tamaño automático de los cuerpos
  - view tamaño de visión
{c["amarillo"]}solar_sistem:{c["default"]} valores del sistema solar
  - asteroid_belt cantidad de asteroides en el cinturon
  - kuiper_belt cantidad de asteroides en el cinturon de kuiper
  - asteroids cantidad de asteroides por el sistema solar
{c["amarillo"]}active_save:{c["default"]} Guarda los datos generados durante la simulación en un archivo .json
{c["amarillo"]}rings:{c["default"]} agregar y ver datos de los anillos
  
  mas informacion en https://github.com/pianistandcats/gravitational-model""")
        
    # ~~~~~~~~~~~~~~~~~~~~ si dice "add" ~~~~~~~~~~~~~~~~~~~~
    elif input_separado[0] == "add":
        if len(input_separado) == 1:
            # crear un cuerpo
            crear_cuerpo()
            # dejar un espacio
            print("\n")
        elif len(input_separado) == 3:
            if input_separado[1] == "moon":
                cuerpo_encontrado = next((cuerpo for cuerpo in todos_los_cuerpos if cuerpo.tag == input_separado[2] or cuerpo.nombre == input_separado[2]), None)
                if cuerpo_encontrado:
                    luna = crear_luna(cuerpo_encontrado)
                    if luna != None:
                        todos_los_aproximados_m.append(luna)
                        # todos_los_cuerpos.append(luna)
                        print(f"{c['amarillo']}Se creo la luna: {luna} en el cuerpo {cuerpo_encontrado.nombre} {c["default"]}")
            
        
    # ~~~~~~~~~~~~~~~~~~~~ si dice "G" ~~~~~~~~~~~~~~~~~~~~
    elif input_separado[0] == "G":
        # -- si tiene 1 palabra --
        if len(input_separado) == 1:
            
            # dar instrucciones de uso
            print("""Seleccione que quiere hacer con la variable G
    \"=\" para asignar un valor
    \"?\" para ver el valor actual""")
            
            # dejar un espacio
            print("\n")
        
        # -- si la segunda palabra es "?" --
        elif input_separado[1] == "?":
            # Dar el valor de g
            print(g)
        
        # -- si la segunda palabra es "=" y tiene 3 palabras
        elif input_separado[1] == "=" and len(input_separado) == 3:
            
            # si la tercera palabra es un numero
            if es_numero(input_separado[2]):
                # cambiar el valor de g
                g = Decimal(input_separado[2])
                print(f"{c["amarillo"]}Nuevo valor de G. Ahora es: {g}{c["default"]}")
            else:
                # dar un error de tipo de dato
                print_error(tipos_de_errores[0])
        else:
            # dar un error de sintaxis
            print_error(tipos_de_errores[1])
    
    # ~~~~~~~~~~~~~~~~~~~~ si dice "cuerpos" ~~~~~~~~~~~~~~~~~~~~ 
    elif input_separado[0] == "cuerpos":
        # -- si solo tiene una palabra -- 
        if len(input_separado) == 1:
            # dar instrucciones de uso
            print("""Seleccione que quiere hacer con "cuerpos"
    \"see\" para ver todos los cuerpos actuales
    \"delete\" para ver el valor actual \"cuerpos delete [tag]\"""")
        
        # -- la segunda palabra es "see" --
        elif input_separado[1] == "see":
            
            # si tiene cuerpos
            if (len(todos_los_cuerpos) > 0):
                # iterar los cuerpos
                for i in todos_los_cuerpos:
                    # mostrar datos
                    print(f"{c["amarillo"]}{i.tag}:{c["default"]} nombre: {i.nombre}, masa = {i.masa}, posicion = {i.posicion}, velocidad = {i.velocidad}")
            
            else:
                
                # indicar que no hay datos
                print("todavía no hay ningun cuerpo")
        
        # -- si la segunda palabra es "delete" --
        elif input_separado[1] == "delete":
            # si tiene tres palabras
            if len(input_separado) == 3:
                # recorre todos los cuerpos
                for i in todos_los_cuerpos:
                    # si la tag es igual a la dada por el usuario
                    if i.tag == input_separado[2]:
                        # indicar que se elimino el cuerpo
                        print(f"{c["amarillo"]}Se elimino {i.nombre} (tag: {i.tag}){c["default"]}")
                        # quitar el cuerpo de la lista
                        todos_los_cuerpos.remove(i)
                        # terminar bucle for
                        break
                
                # si no se encuentra
                else:
                    # indicar un error de input al no existir el cuerpo indicado
                    print_error(tipos_de_errores[3], f"no existe ningun cuerpo con la tag \"{input_separado[2]}\"")
            else:
                # indicar un error de sintaxis
                print_error(tipos_de_errores[1])
        else:
            # indicar un error de sintaxis
            print_error(tipos_de_errores[1])
    
    # ~~~~~~~~~~~~~~~~~~~~ si dice "load" ~~~~~~~~~~~~~~~~~~~~ 
    elif input_separado[0] == "load":
        # -- comprobar que sean 2 palabras --
        if len(input_separado) == 2:
            # comprobar que el archivo exista
            if os.path.exists(input_separado[1]):
                # crear una lista para ir agregando los cuerpos del archivo 
                objetos_agregados = []
                # cargar el archivo
                with open(input_separado[1], 'r') as archivo:
                    # guardar los datos en un diccionario
                    DCLD = json.load(archivo)
                
                # iterar los cuerpos
                for dato in DCLD["cuerpos"]:
                    # guardar los datos de la posicion 
                    n_posicion = Vector2(Decimal(dato["posicion"]["x"]), Decimal(dato["posicion"]["y"]))
                    # guardar los datos de la velocidad
                    n_velocidad = Vector2(Decimal(dato["velocidad"]["x"]), Decimal(dato["velocidad"]["y"]))
                    # crear el cuerpo usando el nombre, la posicon, la velocidad y la masa que indica el archivo
                    cuerpo_cargado = Cuerpo(dato["nombre"],n_posicion,n_velocidad,Decimal(dato["masa"]), float(dato["diametro"]))
                    
                    # se agrega el cuerpo a las listas que contienen los cuerpos
                    todos_los_cuerpos.append(cuerpo_cargado)
                    objetos_agregados.append(cuerpo_cargado)
                    
                    # mostrar el cuerpo que se añadio
                    print(f"{c["amarillo"]}Se añadio {cuerpo_cargado.nombre} (tag: {cuerpo_cargado.tag}){c["default"]}")
                
                if "lunas" in DCLD and isinstance(DCLD["lunas"], list):
                    for dato in DCLD["lunas"]:
                        # guardar los datos de la posicion 
                        n_posicion = Vector2(Decimal(dato["posicion relativa"]["x"]), Decimal(dato["posicion relativa"]["y"]))
                        # guardar los datos de la velocidad
                        n_velocidad = Vector2(Decimal(dato["velocidad relativa"]["x"]), Decimal(dato["velocidad relativa"]["y"]))
                        # guardar datos del planeta
                        planeta = next((cuerpo for cuerpo in todos_los_cuerpos if cuerpo.tag == dato["cuerpo central"] or cuerpo.nombre == dato["cuerpo central"]), None)
                        
                        # crear el cuerpo usando el nombre, la posicon, la velocidad y la masa que indica el archivo
                        cuerpo_cargado = Cuerpo_luna(dato["nombre"],n_posicion,n_velocidad,Decimal(dato["masa"]),planeta, float(dato["diametro"]))
                        
                        # se agrega el cuerpo a las listas que contienen los cuerpos
                        todos_los_aproximados_m.append(cuerpo_cargado)
                        objetos_agregados.append(cuerpo_cargado)
                        
                        # mostrar el cuerpo que se añadio
                        print(f"{c["amarillo"]}Se añadio la luna: {cuerpo_cargado.nombre} al cuerpo: {dato["cuerpo central"]} (tag: {cuerpo_cargado.tag}){c["default"]}")
                else:
                    print_error("el archivo no contiene la lista \"lunas\"")
                    
                if "anillos" in DCLD and isinstance(DCLD["anillos"], list):
                    for dato in DCLD["anillos"]:
                        # guardar los datos de la posicion 
                        distancia_min = dato["distancia"]["min"]
                        distancia_max = dato["distancia"]["max"]
                        planeta = next((cuerpo for cuerpo in todos_los_cuerpos if cuerpo.tag == dato["planeta"] or cuerpo.nombre == dato["planeta"]), None)
                        cantidad_de_asteroides = dato["cantidad de cuerpos"]
                        masa = dato["masa"]
                        
                        # crear el cuerpo usando el nombre, la posicon, la velocidad y la masa que indica el archivo
                        cuerpo_cargado = Anillo(planeta,distancia_min,distancia_max, cantidad_de_asteroides, masa)
                        
                        # se agrega el cuerpo a las listas que contienen los cuerpos
                        todos_los_anillos.append(cuerpo_cargado)
                        
                        # mostrar el cuerpo que se añadio
                        print(f"{c["amarillo"]}Se añadio un anillo a {dato["planeta"]} (tag: {cuerpo_cargado.tag}){c["default"]}")
                else:
                    print_error("el archivo no contiene la lista \"anillos\"")
                    
                # mostrar el numero de cuerpos que se añadieron
                print(f"se añadieron {len(objetos_agregados)} cuerpos")
                
                # si el valor de G es diferente al del archivo
                if (DCLD["G"] != g):
                    g = Decimal(DCLD["G"])
                    print(f"{c["verde"]}Se actualizo el valor de G{c["default"]}")
                    print(f"{c["verde"]}Nuevo valor de G es: {g}{c["default"]}")
                    
                if "asteroides" in DCLD and isinstance(DCLD["asteroides"], int):
                    cantidad_de_asteroides_0 = DCLD["asteroides"]
                    print(f"{c["verde"]}Nueva cantidad de asteroides es: {cantidad_de_asteroides_0}{c["default"]}")
                else:
                    print_error("el archivo no contiene el valor \"asteroides\"")
                    
                if "cinturon" in DCLD and isinstance(DCLD["cinturon"], int):
                    cantidad_de_asteroides_1 = DCLD["cinturon"]
                    print(f"{c["verde"]}Nueva cantidad de asteroides en el cinturon es: {cantidad_de_asteroides_1}{c["default"]}")
                else:
                    print_error("el archivo no contiene el valor \"cinturon\"")
                    
                if "kuiper" in DCLD and isinstance(DCLD["kuiper"], int):
                    cantidad_de_asteroides_2 = DCLD["kuiper"]
                    print(f"{c["verde"]}Nueva cantidad de asteroides en el cinturon de kuiper es: {cantidad_de_asteroides_2}{c["default"]}")
                else:
                    print_error("el archivo no contiene el valor \"kuiper\"")
                
            else:
                print_error(tipos_de_errores[3], "el archivo dado no existe")
        else:
            print_error(tipos_de_errores[1])

    # ~~~~~~~~~~~~~~~~~~~~ si dice "save" ~~~~~~~~~~~~~~~~~~~~ 
    elif input_separado[0] == "save":
        # -- si la cantidad de palabras es igual a 2 --
        if len(input_separado) == 2:
            # se crea la variable con los datos
            datos = crear_archivo_json(todos_los_cuerpos, todos_los_aproximados_m, todos_los_anillos, cantidad_de_asteroides_0, cantidad_de_asteroides_1, cantidad_de_asteroides_2, g)
            # se crea el archivo
            sitio = input_separado[1]
            if input_separado[1].endswith(".json") != True:
                sitio += ".json"
            with open(sitio, 'w') as archivo:
                # se añaden los datos
                json.dump(datos, archivo, indent=4)
            print(f"{c["verde"]}se guardaron los datos en {sitio}{c["default"]}")
        else:
            print_error(tipos_de_errores[1])
    
    # ~~~~~~~~~~~~~~~~~~~~ si dice "time.mode" ~~~~~~~~~~~~~~~~~~~~ 
    elif input_separado[0] == "time.mode":
        # -- si la cantidad de palabras son 2 --
        if len(input_separado) == 2:
            # si la segunda palabra es delta_time
            if input_separado[1] == "delta_time":
                # se activa el modo delta_time
                time_mode = True
            else:
                # dar un error de sintaxis
                print_error(tipos_de_errores[1])
        
        # -- si tiene 3 palabras
        elif len(input_separado) == 3:
            # si la segunda palabra es uniform 
            if input_separado[1] == "uniform":
                # si la 3 palabra es un numero
                if es_numero(input_separado[2]) :
                    # si la 3 palabra es mayor a 0
                    if float(input_separado[2]) > 0:
                        # se activa el modo uniform
                        time_mode = False
                        uniform_time = float(input_separado[2])
                    else:
                        print_error(tipos_de_errores[0], "el tiempo tiene que ser mayor a 0")
                else:
                    print_error(tipos_de_errores[0], "el tiempo tiene que ser un valor float mayor a 0")
            else:
                print_error(tipos_de_errores[1])
        else:
            print_error(tipos_de_errores[1])
    
    # ~~~~~~~~~~~~~~~~~~~~ si dice "size" ~~~~~~~~~~~~~~~~~~~~
    elif input_separado[0] == "size":
        if len(input_separado) == 3:
            if input_separado[1] == "dots":
                if es_numero(input_separado[2]):
                    dot_scale = float(input_separado[2])
                    print(f"{c["amarillo"]}La nueva escala de los puntos. Ahora es: masa * {dot_scale}{c["default"]}")
                else:
                    print_error(tipos_de_errores[0])
            if input_separado[1] == "view":
                xy = input_separado[2].split(";")
                if len(xy) == 2:
                    if es_numero(xy[0]) and es_numero(xy[1]):
                        if float(xy[0]) > 0 and float(xy[1]) > 0:
                            view_scale = Vector2(float(xy[0]),float(xy[1]))
                            print(f"{c["amarillo"]}La nueva escala de vision. Ahora es: {view_scale}{c["default"]}")
                        else:
                            print_error(tipos_de_errores[0])
                    else:
                        print_error(tipos_de_errores[0])
                else:
                    print_error(tipos_de_errores[1])
            else:
                print_error(tipos_de_errores[3], "")
        else:
            print_error(tipos_de_errores[1])
    
    # ~~~~~~~~~~~~~~~~~~~~ si dice "solar_sistem" ~~~~~~~~~~~~~~~~~~~~
    elif input_separado[0] == "solar_sistem":
        if len(input_separado) == 3:
            if input_separado[1] == "asteroid_belt":
                if es_numero_int(input_separado[2]):
                    cantidad_de_asteroides_1 = int(input_separado[2])
                    print(f"{c['amarillo']}La cantidad de asteroides en el cinturon ahora es de: {cantidad_de_asteroides_1} {c["default"]}")
                else:
                    print_error(tipos_de_errores[0], "La cantidad de asteroides tiene que ser compatible con int")
            
            elif input_separado[1] == "kuiper_belt":
                if es_numero_int(input_separado[2]):
                    cantidad_de_asteroides_2 = int(input_separado[2])
                    print(f"{c['amarillo']}La cantidad de asteroides en el cinturon de kuiper ahora es de: {cantidad_de_asteroides_2} {c["default"]}")
                else:
                    print_error(tipos_de_errores[0], "La cantidad de asteroides tiene que ser compatible con int")
            
            elif input_separado[1] == "asteroids":
                if es_numero_int(input_separado[2]):
                    cantidad_de_asteroides_0 = int(input_separado[2])
                    print(f"{c['amarillo']}La cantidad de asteroides ahora es de: {cantidad_de_asteroides_0} {c["default"]}")
                else:
                    print_error(tipos_de_errores[0], "La cantidad de asteroides tiene que ser compatible con int")
            
            else:
                print_error(tipos_de_errores[3], f"El dato {input_separado[1]} no exite")
        else:
            print_error(tipos_de_errores[1], "La sintaxis deve ser: \"solar_sistem {valor a modificar} {cantidad}\"")
        
    # ~~~~~~~~~~~~~~~~~~~~ si dice "active_save" ~~~~~~~~~~~~~~~~~~~~
    elif input_separado[0] == "active_save":
        print(f"""{c["amarillo"]}Este comando gruarda los datos generados durante la simulacion, no los datos proporcionados en esta instancia
si lo que decea es guardar los datos iniciales proporcionados utilice el comando \"save\"
si decea cancelar este comando deje la casilla vacia{c["default"]}""")
        
        si = input('Ruta de guardado: ')
        if si != "":
            active_save = True
            save_in = si
            cic = input('Ciclos: ')
            while es_numero_int(cic) == False:
                print_error(tipos_de_errores[2],"la cantidad de ciclos debe de ser un valor int")
                cic = input('Ciclos: ')
                if cic == "":
                    break
            
            if cic != "":
                active_save = True
                ciclos = int(cic)
        
    # ~~~~~~~~~~~~~~~~~~~~ si dice "rings" ~~~~~~~~~~~~~~~~~~~~
    elif input_separado[0] == "rings":
        if len(input_separado) == 2:
            if input_separado[1] == 'see':
                if (len(todos_los_anillos) > 0):
                    # iterar los cuerpos
                    for i in todos_los_anillos:
                        # mostrar datos
                        print(f"{c["amarillo"]}{i.planeta.nombre}:{c["default"]} {i}")
                else:
                    # indicar que no hay datos
                    print("todavía no hay ningun anillo")
            
        elif len(input_separado) == 3:
            if input_separado[1] == 'delete':
                cuerpo_encontrado = next((anillo for anillo in todos_los_anillos if anillo.tag == input_separado[2]), None)
                if cuerpo_encontrado:
                    print(f"{c['amarillo']}Se elimino el anillo: {n_anillo} en el cuerpo {cuerpo_encontrado.nombre} {c["default"]}")
                    todos_los_anillos.remove(n_anillo)
                    
                else:
                    print_error(tipos_de_errores[3], f"El anillo {input_separado[2]} no exite. Consulte con 'rings see'")
        
        elif len(input_separado) == 4:
            if input_separado[1] == 'add' and  input_separado[2] == "to":
                cuerpo_encontrado = next((cuerpo for cuerpo in todos_los_cuerpos if cuerpo.tag == input_separado[3] or cuerpo.nombre == input_separado[3]), None)
                
                if cuerpo_encontrado:
                    n_anillo = crear_anillo(cuerpo_encontrado)
                    if n_anillo != None:
                        todos_los_anillos.append(n_anillo)
                        print(f"{c['amarillo']}Se creo el anillo: {n_anillo} en el cuerpo {cuerpo_encontrado.nombre} {c["default"]}")
                    
                else:
                    print_error(tipos_de_errores[3], f"El cuerpo {input_separado[3]} no exite. Consulte con 'cuerpos see'")
            else:
                print_error(tipos_de_errores[1], "La sintaxis deve ser: \"ring add to {(tag / nombre) del cuerpo}\"")
        else:
            print_error(tipos_de_errores[1], "La sintaxis deve ser: \"ring {add to / see / delete}\"")
        
    else:
        # indicar un error al no ser un comando valido
        print_error(f"\"{input_del_usuario}\"", mensaje_extra="no es un comando valido. Para ayuda escriba: help")

grid_hh = Grid(4000,4000, view_scale.x/200)
grid_h = Grid(250,250, view_scale.x)
grid_m = Grid(50,50, view_scale.x)
grid_l = Grid(10,10, view_scale.x)

fisica = Fisica(g)
universo = Universo(fisica,grid_h, grid_m, grid_l, grid_hh)

# <- colocar funciones de generacion de cuerpos aqui
for i in todos_los_anillos:
    cuerpos = i.crear_cuerpos_anillo()
    todos_los_aproximados_hh.extend(cuerpos)

print(todos_los_aproximados_hh)

for i in todos_los_aproximados_m:
    i.calcular_orbita(fisica)

# ---------- crear asteroides aleatorios en todo el sistema solar ---------- 
for i in range(cantidad_de_asteroides_0):
    n_posicion = Vector2(Decimal(random.uniform(-4558857000000, 4558857000000)), Decimal(random.uniform(-4558857000000, 4558857000000)))
    n_velocidad = Vector2(0,0)
    
    cuerpo_temp = Cuerpo(str(i), n_posicion, n_velocidad, Decimal(2.8e21))
    M_velocidad = universo.fisica.calcular_velocidad_orbital(todos_los_cuerpos[0], cuerpo_temp)
    # calcular el vector de la direccion usando trigonometria
    ang = atan2(n_posicion.y, n_posicion.x)
    n_velocidad.x = M_velocidad * Decimal(cos(ang + 1.57079632679))
    n_velocidad.y = M_velocidad * Decimal(sin(ang + 1.57079632679))
    
    cuerpo = Cuerpo(str(i), n_posicion, n_velocidad, Decimal(2.8e21), 3, exact=False)
    todos_los_aproximados_l.append(cuerpo)

# ---------- crear asteroides en el cinturon de asteroides ---------- 
for i in range(cantidad_de_asteroides_1):
    n_posicion = Vector2(Decimal(random.uniform(-508632758000, 508632758000)), Decimal(random.uniform(-508632758000, 508632758000)))
    while Decimal(3.291e+11) > Decimal_distancia(Vector2(0,0), n_posicion) or Decimal_distancia(Vector2(0,0), n_posicion) > Decimal(4.787e+11):
        n_posicion = Vector2(Decimal(random.uniform(-508632758000, 508632758000)), Decimal(random.uniform(-508632758000, 508632758000)))

    # print(str(Decimal_distancia(Vector2(0,0), n_posicion)))

    n_velocidad = Vector2(0,0)
    
    cuerpo_temp = Cuerpo(str(i), n_posicion, n_velocidad, Decimal(2.8e21))
    M_velocidad = universo.fisica.calcular_velocidad_orbital(todos_los_cuerpos[0], cuerpo_temp)
    # calcular el vector de la direccion usando trigonometria
    ang = atan2(n_posicion.y, n_posicion.x)
    n_velocidad.x = M_velocidad * Decimal(cos(ang + 1.57079632679))
    n_velocidad.y = M_velocidad * Decimal(sin(ang + 1.57079632679))
    
    # print(str(n_velocidad))
    # print(str(n_velocidad.magnitud()))
    
    cuerpo_nuevo = Cuerpo(str(i) + " Cinturon", n_posicion, n_velocidad, Decimal(2.8e21), diam=3, exact=False)
    todos_los_aproximados_h.append(cuerpo_nuevo)

# ---------- crear asteroides en el cinturon de kuiper ---------- 
for i in range(cantidad_de_asteroides_2):
    n_posicion = Vector2(Decimal(random.uniform(-7.48e+12, 7.48e+12)), Decimal(random.uniform(-7.48e+12, 7.48e+12)))
    while Decimal(4488000000000) > Decimal_distancia(Vector2(0,0), n_posicion) or Decimal_distancia(Vector2(0,0), n_posicion) > Decimal(7480000000000):
        n_posicion = Vector2(Decimal(random.uniform(-7.48e+12, 7.48e+12)), Decimal(random.uniform(-7.48e+12, 7.48e+12)))
        
    # print(str(Decimal_distancia(Vector2(0,0), n_posicion)))
    n_velocidad = Vector2(0,0)
    
    cuerpo_temp = Cuerpo(str(i), n_posicion, n_velocidad, Decimal(2.8e21))
    M_velocidad = universo.fisica.calcular_velocidad_orbital(todos_los_cuerpos[0], cuerpo_temp)
    # calcular el vector de la direccion usando trigonometria
    ang = atan2(n_posicion.y, n_posicion.x)
    n_velocidad.x = M_velocidad * Decimal(cos(ang + 1.57079632679))
    n_velocidad.y = M_velocidad * Decimal(sin(ang + 1.57079632679))
    
    # print(str(n_velocidad))
    # print(str(n_velocidad.magnitud()))
    
    cuerpo_nuevo = Cuerpo(str(i) + " Cinturon", n_posicion, n_velocidad, Decimal(2.8e21), diam=3, exact=False)
    todos_los_aproximados_l.append(cuerpo_nuevo)

universo.grid_h.actualizar(todos_los_aproximados_h)
universo.grid_m.actualizar(todos_los_aproximados_m)
universo.grid_l.actualizar(todos_los_aproximados_l)

# Uso de la clase para tener la ventana
puntos = Puntos()

# Agregar los puntos para cada cuerpo
puntos.agregar_cuerpos(todos_los_cuerpos)

puntos.agregar_cuerpos(todos_los_aproximados_hh)
puntos.agregar_cuerpos(todos_los_aproximados_h)
puntos.agregar_cuerpos(todos_los_aproximados_m)
puntos.agregar_cuerpos(todos_los_aproximados_l)

# establecer posicion inicial de las lunas
for cuerpo in todos_los_aproximados_m:
    cuerpo.posicion = fisica.posicion_orbital_completa(cuerpo, 0) + cuerpo.cuerpo_que_orbita.posicion
    cuerpo.posicion_inicial = fisica.posicion_orbital_completa(cuerpo, 0) + cuerpo.cuerpo_que_orbita.posicion

for i in puntos.cuerpos:
    print(i.nombre)
# iniciar la animacion
puntos.iniciar_animacion()

# variable para el delta time
last_time = time.perf_counter()

UPT = time.perf_counter()

tiempo_inicial = time.perf_counter()
tiempo_transcurrido = 0 

ciclos_transcurridos = 0
# ---------------- empezando el bucle infinito ---------------------------
while True:
    # verificar el modo de tiempo que se esta usando
    if time_mode == True:
        # ~~~~~~~~~~~~~~~~~~~ calcular el delta time ~~~~~~~~~~~~~~~~~~~~
        # guardar el tiempo actual
        current_time = time.perf_counter()
        
        # crear el delta time (tiempo que tarda en hacer un frame)
        # haciendo la diferencia entre el tiempo actual y el del frame anterior
        delta_time = current_time - last_time
        delta_time *= puntos.multiplicador_de_tiempo
    else:
        # ~~~~~~~~~~~~~~~~~~~ usar un valor fijo ~~~~~~~~~~~~~~~~~~~~
        delta_time = uniform_time * puntos.multiplicador_de_tiempo
    
    CPT = time.perf_counter()
    DTPT = CPT - UPT
    # ~~~~~~~~~~~ aplicar la fuerza de gravedad entre cada objeto~con todos los demas ~~~~~~~~~~~~~~~~
    # iterar la lista de cuerpos
    for i, objeto in enumerate(todos_los_cuerpos):
        for otros_objetos in todos_los_cuerpos[i+1:]:
            # aplicar la gravedad entre estos objetos
            objeto.aplicar_gravedad(otros_objetos, delta_time)
    
    
    # iterar la lista de aproximados
    todos = universo.grid_h.get_all()
    simular_aproximados(todos)
      
    # iterar la lista de aproximados
    todos = universo.grid_l.get_all()
    simular_aproximados(todos)
    
    
    universo.grid_h.actualizar(todos_los_aproximados_hh)
    universo.grid_h.actualizar(todos_los_aproximados_h)
    universo.grid_m.actualizar(todos_los_aproximados_m)
    universo.grid_l.actualizar(todos_los_aproximados_l)

    
    # ~~~~~~~~~~~~~~~ calcular la inercia 9de cada objeto ~~~~~~~~~~~~~~~~~~~~~~
    # iterar la lista de todos los cuerpos
    for i in todos_los_cuerpos:
        # realizar su funcion constante
        i.constante(delta_time)
    
    for i, cuerpo in enumerate(todos_los_aproximados_m):
        # for j in todos_los_cuerpos:
        #     if cuerpo.cuerpo_que_orbita != j:
        #         cuerpo.aplicar_gravedad(j, delta_time, False)
                
        # for j in todos_los_aproximados_m[i+1:]:
        #     cuerpo.aplicar_gravedad(j, delta_time, True)
        cuerpo.posicion = fisica.posicion_orbital_completa(cuerpo, tiempo_transcurrido) + cuerpo.cuerpo_que_orbita.posicion
        
            
        # cuerpo.constante(delta_time)
        
    
    # iterar la lista de aproximados
    for cuerpo in todos_los_aproximados_hh:
        cuerpo.posicion = fisica.posicion_orbital_simple(cuerpo, tiempo_transcurrido) + cuerpo.cuerpo_que_orbita.posicion
    
    
    tiempo_transcurrido += delta_time
    
    # actualizar el grafico
    puntos.actualizar_grafico()
    if time_mode == True:
        # imprimir cuanto tarda entre cada frame
        print(delta_time)
        
        # guardar el tiempo actual (para el delta time del siguiente frame)
        last_time = current_time
    
    UPT = CPT
    print(f"---------------------> {DTPT}")
    
    # indicar la cantidad de dias
    print(str(tiempo_transcurrido /60/60/24) + " dias")
    
    if active_save == True:
        ciclos_transcurridos += 1
        
        for i in todos_los_cuerpos:
            i.guardar_pos()
            
        if(ciclos_transcurridos >= ciclos):
            break
if active_save == True:
    # se crea la variable con los datos
    datos = crear_archivo_json_de_sim(todos_los_cuerpos,ciclos)
    # se crea el archivo
    with open(save_in, 'w') as archivo:
        # se añaden los datos
        json.dump(datos, archivo, indent=4)
    