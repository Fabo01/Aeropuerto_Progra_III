# 📚 Documentación del Sistema de Gestión de Aeropuerto

## Introducción

Bienvenido a la documentación del Sistema de Gestión de Aeropuerto, una aplicación que implementa un TDA Lista Doblemente Enlazada con Centinelas para la gestión eficiente de vuelos. Este sistema proporciona una API REST completa y una interfaz gráfica de usuario para administrar vuelos, prioridades y la estructura de lista.

## Contenido de la Documentación

- [**Arquitectura**](./arquitectura.md): Descripción de la arquitectura por capas del sistema y su estructura de directorios.
- [**Lista Doblemente Enlazada**](./lista_doble_enlazada.md): Explicación de la estructura de datos principal y su implementación.
- [**Implementación TDA**](./implementacion_tda.md): Detalles técnicos sobre la implementación del TDA Lista Doblemente Enlazada.
- [**Vuelos**](./vuelos.md): Descripción detallada de la entidad Vuelo y su gestión en el sistema.
- [**API Endpoints**](./api_endpoints.md): Documentación de los endpoints de la API REST.
- [**Diagramas UML**](./diagramas_uml.md): Diagramas estructurales (clases, ER, componentes).
- [**Diagramas de Secuencia**](./diagramas_secuencia.md): Diagramas de comportamiento y flujo de información.
- [**Diagramas de Casos de Uso**](./diagramas_casos_uso.md): Diagramas y descripciones de casos de uso.
- [**Patrones de Diseño**](./patrones_diseño.md): Descripción de los patrones de diseño implementados en el sistema.
- [**Modelos de Base de Datos**](./modelos_base_datos.md): Explicación de los modelos ORM utilizados para la persistencia.

## Características Principales

- **API REST completa**: Proporciona endpoints para manipular vuelos y la estructura de lista
- **Interfaz gráfica**: Implementada con CustomTkinter para una experiencia de usuario intuitiva
- **Persistencia**: Base de datos SQLite con SQLAlchemy ORM
- **Lista Doblemente Enlazada**: Implementación eficiente con centinelas
- **Priorización automática**: Sistema inteligente de ordenamiento según múltiples criterios
- **Gestión de emergencias**: Mecanismo para priorizar vuelos en situaciones críticas

## Comenzando

Para comenzar a explorar la arquitectura y funcionamiento del sistema, recomendamos seguir este orden:

1. Revisar la [arquitectura general](./arquitectura.md) para comprender la organización del sistema
2. Explorar la [implementación de la lista doblemente enlazada](./lista_doble_enlazada.md) como estructura central
3. Comprender la [entidad Vuelo](./vuelos.md) y su integración con la estructura de datos
4. Examinar los [diagramas UML](./diagramas_uml.md) para una visión completa del diseño
5. Estudiar los [diagramas de casos de uso](./diagramas_casos_uso.md) para entender las funcionalidades

## Audiencia

Esta documentación está dirigida a:

- **Desarrolladores**: Que necesiten entender o extender el sistema
- **Estudiantes**: Interesados en aprender sobre implementaciones prácticas de TDAs
- **Profesores**: Como referencia para la evaluación del proyecto
- **Usuarios finales**: Para comprender el funcionamiento general del sistema

## Recursos Adicionales

- **Código fuente**: Disponible en el directorio raíz del proyecto
- **API Docs interactiva**: Accesible a través de `/docs` cuando el servidor está en ejecución
- **Ejemplos de uso**: Incluidos en la documentación de cada endpoint

## Contacto

Para consultas o sugerencias relacionadas con esta documentación, contacte al equipo de desarrollo.
