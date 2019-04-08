# Buscador para la lista de mails de PyAr

Este proyecto nace con el propósito de que usuarios o personas que no están
subscriptos a la lista de Python Argentina puedan encontrar recursos valiosos
que alguna vez se trataron en la misma. Ademas de hacer accesible la búsqueda
a principiantes y evitar tener que grepear los archivos o usar los hacks de google
podemos elegir nuestra propia lógica de indexación y búsqueda con libertad.

## Ejemplo
![demo](https://dl.dropboxusercontent.com/s/37mi0h8bbe7i02m/ejemplo.gif?dl=0)


## Iniciar proyecto con Docker

### Correr la aplicación Flask

```
make up
```

### Crear índice de búsqueda

Crea un indice de búsqueda con todos los mails desde el año 2011 al 2019 de la lista de PyAr,
aproximadamente de 40.000 mails, para crear un indice reducido usar el comando `make build_test_index`

```
make build_index
```

# Construir índice de búsqueda para desarrollo
```
make build_test_index:
```
