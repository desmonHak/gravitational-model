
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
import ctypes

# habilitar el soporte de colores ANSI en la consola de Windows
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# ---------------------- Crear la clase Cuerpo ----------------------------
class Cuerpo:
    # inicializar variables
    def __init__(self, nombre, posicion, velocidad, masa):
        self.nombre = nombre
        self.posicion = posicion
        self.velocidad = velocidad
        self.masa = masa
        # establecer una tag aleatoria
        self.tag = crear_string_random(5)
        # establecer un color aleatorio
        self.color = colorsys.hsv_to_rgb(random.uniform(0,1),1,1)
    
    # funcion para aplicar una fuerza
    def aplicar_fuerza(self, fueza_aplicada):
        # aplicar la formula F = ma
        velocidad_aplicable = fueza_aplicada / self.masa
        # se suma la velocidad a la velocidad previa anterior
        self.velocidad += velocidad_aplicable
    
    # funcion para aplicar la gravedad
    def aplicar_gravedad(self, otro, delta_time):
        # calcular la fuerza usando la formula de newton
        fuerza_total = g*((self.masa * otro.masa) / distancia(self.posicion, otro.posicion))
        
        # calcular el vector de la direccion usando trigonometria
        ang = atan2(self.posicion.y - otro.posicion.y, self.posicion.x - otro.posicion.x)
        fuerza_x = fuerza_total * cos(ang) * 180 / pi
        fuerza_y = fuerza_total * sin(ang) * 180 / pi
        
        # aplicar la fuerza obtenida
        self.aplicar_fuerza(Vector2(fuerza_x, fuerza_y) * delta_time * -1)
    
    # funcion para calcular la posición del objeto en cada momento
    def constante(self, delta_time):
        # mover lo que indica la velocidad que tiene multiplicado por el tiempo que tarda cada frame
        self.posicion += self.velocidad * delta_time
    
    # asignar una nueva posición
    def reposicionar(self, nueva_posicion):
        self.posicion = nueva_posicion

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
        self.ax.set_xlim(-100, 150) # x
        self.ax.set_ylim(-150, 150) # y
        
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
        
        # activar el modo interactivo en el grafico
        plt.ion()
        
        # iniciar la animacion
        self.iniciar_animacion()
        # crear una animacion
        self.ani = FuncAnimation(self.fig, self.actualizar_grafico, interval=16.7 /2, frames=60)

    # agregar un solo cuerpo
    def agregar_punto(self, cuerpo):
        self.cuerpos.append(cuerpo)
        self.actualizar_grafico()
    
    # agregar varios cuerpos
    def agregar_cuerpos(self, cuerpos):
        for item in cuerpos:
            self.cuerpos.append(item)

    # funcion para actualizar el grafico
    def actualizar_grafico(self):
        # establecer las variables que se van a usar en el grafico
        xs, ys, masas, colores = zip(*[(i.posicion.x, i.posicion.y, i.masa, i.color) for i in self.cuerpos])
        # actualizar las posiciones
        self.scatter.set_offsets(list(zip(xs, ys)))
        # actualizar las masas
        self.scatter.set_sizes(list(masas))
        # actualizar el color
        self.scatter.set_color(list(colores))
        # mostrar cambios
        self.fig.canvas.get_tk_widget().update()
        
    def iniciar_animacion(self):
        plt.show()

# -------------------- funcion para pedir datos --------------------------
def pedir_dato(nombre_del_dato, tipo_de_dato, close = "exit"): # los tipos de datos van 0 = int; 1 = float; 2 = vector; 3 = string
    # pedir dato inicial
    dato = input(f'{c["verde"]} {nombre_del_dato} = {c["default"]}')
    
    # si el dato es igual a el comando de salida
    if dato == close:
        # retornar falso
        return False
    
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
    
    elif tipo_de_dato == 2: # si el tipo de dato pedido era un vector 2 
        # separar el input por el ;
        vector = dato.split(";") 
        
        if len(vector) == 2: # si la cantidad de datos es 2
            if es_numero(vector[0]) and es_numero(vector[1]): # si ambos datos son numeros
                # retornar el vector 2
                return Vector2(float(vector[0]),float(vector[1]))
    
    # --- en caso de que nada de eso pase
    # indicar al usuario que el dato no es valido
    print_error(tipos_de_errores[0], mensaje_extra="El tipo de dato otorgado no es valido en este contexto")
    
    # volver a pedir los datos
    a = close
    b = tipo_de_dato
    c = nombre_del_dato
    return pedir_dato(c, close=a, tipo_de_dato=b)

# ------------ funcion para crear un cuerpo ----------------------------------------
def crear_cuerpo():
    # pedir el nombre
    nombre = pedir_dato("Nombre", tipo_de_dato=3)

    if nombre != False and nombre != None: # si el dato tiene un valor
        
        # pedir la masa
        masa = pedir_dato("Masa", tipo_de_dato=1)
        
        if masa != False and masa != None: # si el dato tiene un valor
            
            if masa > 0: # si la masa es mayor a 0
                
                # perdir la posicion 
                posicion = pedir_dato("posicion", tipo_de_dato=2)
                
                if posicion != False and posicion != None: # si el dato tiene un valor
                    
                    # pedir la velocidad
                    velocidad = pedir_dato("velocidad", tipo_de_dato=2)
                    
                    if velocidad != False and velocidad != None: # si el dato tiene un valor
                        
                        # indicar que se creo el cuerpo
                        print(f"se creo el cuerpo {nombre}, masa = {masa}, posicion = {posicion}, velocidad = {velocidad}")
                        
                        # crear cuerpo
                        cuerpo_creado = Cuerpo(nombre, posicion, velocidad, masa)
                        print(cuerpo_creado.tag)
                        # añadir el cuerpo a la variable que contiene a todos
                        todos_los_cuerpos.append(cuerpo_creado)
            else: # si la masa es menor a 0
                # indicar el error
                print_error(tipos_de_errores[2], mensaje_extra="no se puede tener una masa negativa")
                # print("\x1b[1;31merror de input (no se puede tener una masa negativa){c["default"]}")

# Constante de gravitacion universal
g = 0.01

# ------------ crear cuerpos -------------------------
todos_los_cuerpos = list()

sigue = True
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
{c["amarillo"]}G:{c["default"]} constante de gravitacion universal
    ? muestra su valor actual
    = igualar a (valor siguiente a \"=\")
{c["amarillo"]}run:{c["default"]} empezar simulacion
{c["amarillo"]}cuerpos:{c["default"]} datos de los cuerpos
{c["amarillo"]}load:{c["default"]} cargar un archivo: load [nombre del archivo]
{c["amarillo"]}save:{c["default"]} guardar datos de los cuerpos: save [nombre del archivo]""")
        
    # ~~~~~~~~~~~~~~~~~~~~ si dice "add" ~~~~~~~~~~~~~~~~~~~~
    elif input_separado[0] == "add":
        # crear un cuerpo
        crear_cuerpo()
        # dejar un espacio
        print("\n")
    
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
                g = float(input_separado[2])
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
    
    # ~~~~~~~~~~~~~~~~~~~~ is dice "load" ~~~~~~~~~~~~~~~~~~~~ 
    elif input_separado[0] == "load":
        if len(input_separado) == 2:
            if os.path.exists(input_separado[1]):
                objetos_agregados = []
                with open(input_separado[1], 'r') as archivo:
                    DCLD = json.load(archivo)
                for dato in DCLD["cuerpos"]:
                    n_posicion = Vector2(dato["posicion"]["x"], dato["posicion"]["y"])
                    n_velocidad = Vector2(dato["velocidad"]["x"], dato["velocidad"]["y"])
                    cuerpo_cargado = Cuerpo(dato["nombre"],n_posicion,n_velocidad,dato["masa"])
                    todos_los_cuerpos.append(cuerpo_cargado)
                    objetos_agregados.append(cuerpo_cargado)
                    print(f"{c["amarillo"]}Se añadio {cuerpo_cargado.nombre} (tag: {cuerpo_cargado.tag}){c["default"]}")
                print(f"se añadieron {len(objetos_agregados)} cuerpos")
                
                if (DCLD["G"] != g):
                    g = DCLD["G"]
                    print()
                
            else:
                print_error(tipos_de_errores[3], "el archivo dado no existe")
        else:
            print_error(tipos_de_errores[1])

    elif input_separado[0] == "save":
        if len(input_separado) == 2:
            datos = crear_archivo_json(todos_los_cuerpos, g)
            with open(input_separado[1], 'w') as archivo:
                json.dump(datos, archivo, indent=4)
        else:
            print_error(tipos_de_errores[1])
    
    else:
        # indicar un error al no ser un comando valido
        print_error(f"\"{input_del_usuario}\"", mensaje_extra="no es un comando valido. Para ayuda escriba: help")


# Uso de la clase para tener la ventana
puntos = Puntos()

# Agregar los puntos para cada cuerpo
puntos.agregar_cuerpos(todos_los_cuerpos)
# variable para el delta time
last_time = time.perf_counter()

# ---------------- empezando el bucle infinito ---------------------------
while True:
    
    # ~~~~~~~~~~~~~~~~~~~ calcular el delta time ~~~~~~~~~~~~~~~~~~~~
    # guardar el tiempo actual
    current_time = time.perf_counter()
    
    # crear el delta time (tiempo que tarda en hacer un frame)
    # haciendo la diferencia entre el tiempo actual y el del frame anterior
    delta_time = current_time - last_time
    
    
    # ~~~~~~~~~~~ aplicar la fuerza de gravedad entre cada objeto~con todos los demas ~~~~~~~~~~~~~~~~
    # iterar la lista de cuerpos
    for objeto in todos_los_cuerpos:
        # iterar de nuevo la lista de cuerpos
        for otros_objetos in todos_los_cuerpos:
            # si el otro objeto es distinto del objeto al que se le aplicara la fuerza
            if otros_objetos != objeto:
                # aplicar la gravedad entre estos objetos
                objeto.aplicar_gravedad(otros_objetos, delta_time)
    
    # ~~~~~~~~~~~~~~~ calcular la inercia de cada objeto ~~~~~~~~~~~~~~~~~~~~~~
    # iterar la lista de todos los cuerpos
    for i in todos_los_cuerpos:
        # realizar su funcion constante
        i.constante(delta_time)
    
    # actualizar el grafico
    puntos.actualizar_grafico()
    
    # imprimir cuanto tarda entre cada frame
    print(delta_time)
    
    # guardar el tiempo actual (para el delta time del siguiente frame)
    last_time = current_time
