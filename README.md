# Modelo gravitacional en 2 dimensiones

## Funcionalidad del código:
En este programa puedes hacer simulaciones de gravedad en 2 dimensiones.

## instrucciones de uso del programa:
1. help: Ver todas las acciones posibles

2. add: añadir un cuerpo

3. G: constante de gravitación universal
	
  - ? muestra su valor actual
  - = igualar a (valor siguiente a \"=\")

4. run: empezar simulacion

5. cuerpos: datos de los cuerpos

6. load: cargar un archivo: load [nombre del archivo]

7. save: guardar datos de los cuerpos y el valor de G: save [nombre del archivo]

8. time.mode: asignar el tipo de tiempo que se va a usar
  
  - delta_time varia dependiendo de cuanto tarda entre frame y frame (automático)
  - uniform un valor constante cada frame

Para asignación de vectores 2 se escribe x;y separando los valores con un punto y coma

ej: 5;8 indica la posición 5 en X, 8 en Y

## Recomendaciones:
- Se pueden crear funciones dentro del código gravedad.py que creen muchos cuerpos de forma automática (preferentemente justo después del bucle de personalización del usuario)
- En simulaciones de muchos cuerpos la simulación puede ir a pocos FPS
- Si se busca precisión se recomeienda usar el time.mode en uniform ya que la velocidad de procesameniento no influye en la simulacion
- se pude simular el sistema solar de la siguiente manera:
```
>>> load solar_sistem.json
>>> time.mode uniform 100000
```

el valor de time.mode uniform se puede cambiar para variar la velocidad