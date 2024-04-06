
# este codigo contiene algunas funciones extra

# verificar si una string es combertible a float
def es_numero(cadena):
    try:
        float(cadena)
        return True
    except ValueError:
        return False