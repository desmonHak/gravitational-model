
# ----------------- importar librerias --------------------- 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from math import *
from vectores import *
import time
import random
import colorsys

# ---------------------- Crear la clase Cuerpo ----------------------------
class Cuerpo:
    # inicializar variables
    def __init__(self, nombre, posicion, velocidad, masa):
        self.nombre = nombre
        self.posicion = posicion
        self.velocidad = velocidad
        self.masa = masa
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

# -------------------- funcion para pedir datos de planetas --------------------------
def pedir_dato(nombre_del_dato, close = "exit", tipo_de_dato = 1): # los tipos de datos van 0 = int; 1 = float; 2 = vector; 3 = string
    dato = input(f'{nombre_del_dato} = ')
    
    if tipo_de_dato == 3:
        return dato
    elif dato.isnumeric():
        if tipo_de_dato == 0:
            return int(dato)
        elif tipo_de_dato == 1:
            return float(dato)
    elif tipo_de_dato == 2:
        vector = dato.split(";")
        if len(vector) == 2:
            if vector[0].isnumeric() and vector[1].isnumeric():
                return Vector2(float(vector[0]),float(vector[1]))
        
    elif dato == close:
        return False
    
    print("dato invalido")
    pedir_dato(nombre_del_dato, close = close, tipo_de_dato=tipo_de_dato)

def pedir_datos_del_planeta():
    nombre = pedir_dato("Nombre", tipo_de_dato=3)
    if nombre != False:
            
        masa = pedir_dato("Masa", tipo_de_dato=1)
        if masa != False:
                
            posicion = pedir_dato("posicion", tipo_de_dato=2)
            if posicion != False:
                    
                velocidad = pedir_dato("velocidad", tipo_de_dato=2)
                if velocidad != False:
                        
                    cuerpo_creado = Cuerpo("nombre", posicion, velocidad, masa)
                    todos_los_cuerpos.append(cuerpo_creado)

# Constante de gravitacion universal
g = 0.01

# ------------ crear cuerpos -------------------------
todos_los_cuerpos = list()

sigue = True
while sigue:
    input_del_usuario = input('>>> ')
    input_separado = input_del_usuario.split(" ")
    
    if input_del_usuario == "run":
        sigue = False
        break
    elif input_separado[0] == "add":
        pedir_datos_del_planeta()
    elif input_separado[0] == "G":
        if len(input_separado) == 1:
            print("""Seleccione que quiere hacer con la variable G
            \"=\" para asignar un valor
            \"?\" para ver el valor actual""")
        elif input_separado[1] == "?":
            print(g)
        elif input_separado[1] == "=" and len(input_separado) == 3:
            if input_separado[2].isnumeric():
                g = float(input_separado[2])
            else:
                print("error de input")
        else:
            print("error de input")

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
