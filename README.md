# Proyecto de Sistema Distribuido de Monitoreo de Incendios

## Introducción

Este proyecto tiene como objetivo desarrollar un sistema distribuido para monitorear el estado de los suelos en zonas boscosas y detectar posibles incendios forestales. Se utilizarán conceptos de Edge, Fog y Cloud Computing para implementar una arquitectura que permita la tolerancia a fallas y la captura de datos de temperatura, humedad y presencia de humo.

## Contexto

Los incendios forestales han aumentado debido al cambio climático y las malas prácticas humanas. Este sistema busca monitorear de forma continua el estado del suelo en zonas boscosas para detectar signos de incendios y prevenir daños mayores.

## Arquitectura del Sistema

El sistema se compone de tres capas principales:

1. **Capa Edge Computing**: Aquí se encuentran los sensores de humo, temperatura y humedad, así como el actuador de aspersor. Los sensores envían datos a la capa de Fog Computing.

2. **Capa Fog Computing**: El proxy en esta capa recibe los datos de los sensores, realiza cálculos y envía información relevante a la capa Cloud Computing.

3. **Capa Cloud Computing**: Esta capa recibe datos procesados desde la capa Fog y almacena alarmas detectadas. También realiza cálculos adicionales sobre los datos recibidos.

## Componentes del Sistema

El sistema consta de varios componentes, incluyendo sensores de humo, temperatura y humedad, así como un actuador de aspersor y un proxy en la capa Fog. Cada componente tiene su función específica en el monitoreo y detección de incendios.

## Implementación

La comunicación entre los componentes se realiza utilizando ZeroMQ con un modelo Pipeline para los sensores y proxies, y un patrón request-reply para la comunicación entre las capas. Se implementa una arquitectura tolerante a fallas para garantizar la continuidad del sistema.

## Rendimiento del Sistema

Se realizarán pruebas de rendimiento para medir la cantidad de mensajes enviados, los tiempos de comunicación y la cantidad de alertas generadas. Se evaluarán diferentes escenarios para determinar la eficiencia del sistema y posibles mejoras en su diseño.

## Entregas y Evaluación

El proyecto se divide en dos entregas principales, donde se evaluará el diseño, implementación y rendimiento del sistema. Se utilizará una rúbrica para evaluar cada componente del proyecto y su cumplimiento con los requisitos establecidos.

Para más detalles sobre la implementación, pruebas y evaluación del sistema, consulte la documentación proporcionada.

