# 📊 Diagramas UML del Sistema

## Diagrama de Clases

```
+------------------+       +---------------------+      +------------------------+
|      Vuelo       |       |   NodoDobleVuelos   |      | ListaDobleEnlazada     |
+------------------+       +---------------------+      +------------------------+
| id: Integer      |<----->| id: Integer         |<---->| id: Integer            |
| numero_vuelo: Str|       | posicion: Integer   |      | nombre: String         |
| origen: String   |       | anterior_id: Integer|      | cabezon_id: Integer    |
| destino: String  |       | siguiente_id:Integer|      | colon_id: Integer      |
| hora_salida: Date|       | vuelo_id: Integer   |      | tamanio: Integer       |
| hora_llegada:Date|       | centinela: Enum     |      +------------------------+
| prioridad: Int   |       | activo: Boolean     |             ^
| estado: Enum     |       | version: Integer    |             |
| emergencia: Bool |       +---------------------+      +----------------------+
+------------------+                ^                   |     Servicios        |
        ^                           |                   +----------------------+
        |                           |                   | VueloServicio        |
+------------------+       +---------------------+      | ListaDobleServicio   |
|    VueloDTO      |       |  NodoDobleVueloDTO  |      +----------------------+
+------------------+       +---------------------+             ^
                                                               |
+------------------+       +---------------------+      +----------------------+
|   Repositorios   |       |      API/Rutas      |      |  Controlador        |
+------------------+       +---------------------+      +----------------------+
| VueloRepo        |       | Vuelo_Rutas         |      | ClienteAPI           |
| ListaDobleRepo   |       | ListaDoble_Rutas    |      | Main Controller      |
+------------------+       +---------------------+      +----------------------+
```

## Diagrama de Entidad-Relación

```
+-------------+       +---------------+       +----------------+
|    Vuelo    |       | NodoDobleVuelo|       |   ListaDoble   |
+-------------+       +---------------+       +----------------+
| PK: id      |<----->| PK: id        |<----->| PK: id         |
| numero_vuelo|       | posicion      |       | nombre         |
| origen      |       | FK: anterior  |       | FK: cabezon    |
| destino     |       | FK: siguiente |       | FK: colon      |
| hora_salida |       | FK: vuelo_id  |       | tamanio        |
| hora_llegada|       | centinela     |       |                |
| prioridad   |       | activo        |       |                |
| estado      |       | version       |       |                |
| emergencia  |       | creado_en     |       |                |
+-------------+       +---------------+       +----------------+
```

## Diagrama de Arquitectura

```
+-----------------------------------+
|            Presentación           |
+-----------------------------------+
|  - API REST (FastAPI)             |
|  - GUI (CustomTkinter)            |
+-----------------------------------+
                 |
+-----------------------------------+
|           Capa de Servicios       |
+-----------------------------------+
|  - VueloServicio                  |
|  - ListaDobleEnlazadaServicio     |
+-----------------------------------+
                 |
+-----------------------------------+
|         Capa de Repositorios      |
+-----------------------------------+
|  - VueloRepo                      |
|  - ListaDobleEnlazadaRepo         |
+-----------------------------------+
                 |
+-----------------------------------+
|          Capa de Modelos          |
+-----------------------------------+
|  - Vuelo                          |
|  - NodoDobleVuelos                |
|  - ListaDobleEnlazadaCentinelas   |
+-----------------------------------+
                 |
+-----------------------------------+
|            Base de Datos          |
+-----------------------------------+
|  - SQLite                         |
+-----------------------------------+
```

## Diagrama de Estados: Vuelo

```
      +-------------+
      |  Creación   |
      +-------------+
             |
             v
      +-------------+
 ---->| Programado  |
|     +-------------+
|            |
|            v
|     +-------------+     +-------------+
|     |  Retrasado  |---->|  Cancelado  |
|     +-------------+     +-------------+
|            |
|            v
|     +-------------+
|     | Completado  |
|     +-------------+
|
|     +-------------+
 -----|  Emergencia |
      +-------------+
      (estado superpuesto)
```

## Diagrama de Componentes

```
+-----------------------------------+
|           Sistema Aeropuerto      |
+-----------------------------------+
         |               |
 +---------------+ +---------------+
 | Frontend (CTk)| | Backend (API) |
 +---------------+ +---------------+
         |               |
 +---------------+ +---------------+
 |    Vistas     | |    Rutas      |
 +---------------+ +---------------+
         |               |
         +---------+---------+
                   |
           +---------------+
           |   Servicios   |
           +---------------+
                   |
           +---------------+
           | Repositorios  |
           +---------------+
                   |
           +---------------+
           |    Modelos    |
           +---------------+
                   |
           +---------------+
           |  TDA / Estr.  |
           +---------------+
                   |
           +---------------+
           |     BBDD      |
           +---------------+
```
