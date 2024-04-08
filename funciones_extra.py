
# este codigo contiene algunas funciones y variables extra
import json
from random import *

tipos_de_errores = [
    "Error de tipo de dato", # 0
    "Error de sintaxis", # 1
    "Error de valor", # 2
    "Error de input" # 3
]

c = {
    'negro': '\x1b[1;30m',
    'rojo': '\x1b[1;31m',
    'verde': '\x1b[1;32m',
    'amarillo': '\x1b[1;33m',
    'azul': '\x1b[1;34m',
    'morado': '\x1b[1;35m',
    'cian': '\x1b[1;36m',
    'blanco': '\x1b[1;37m',
    'default': '\x1b[0;37m',
}

letras_numeros = "abcdefghijklmnopqrstuvwxyz0123456789"

def crear_string_random(largo):
    str_random = ""
    for i in range(largo):
        str_random += letras_numeros[randint(0, len(letras_numeros) -1)]
    return str_random

# verificar si una string es combertible a float
def es_numero(cadena):
    try:
        float(cadena)
        return True
    except ValueError:
        return False

def print_error(tipo_de_error, mensaje_extra = ""):
    if mensaje_extra != "":
        print(f"{c["rojo"]}{tipo_de_error}: {mensaje_extra}{c["default"]}")
    else:
        print(f"{c["rojo"]}{tipo_de_error}{c["default"]}")

def crear_archivo_json(lista_de_cuerpos, gravitacion_universal):
    cuerpos = []
    
    for item in lista_de_cuerpos:
        diccionario_para_un_cuerpo = {
            "nombre": item.nombre,
            "posicion": {
                "x": item.posicion.x,
                "y": item.posicion.y
            },
            "velocidad": {
                "x": item.velocidad.x,
                "y": item.velocidad.y
            },
            "masa": item.masa
        }
        cuerpos.append(diccionario_para_un_cuerpo)
    
    archivo = {
        "cuerpos": cuerpos,
        "G": gravitacion_universal
    }
    return archivo