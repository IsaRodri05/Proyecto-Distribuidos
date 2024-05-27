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

## Guia para ejecutarlo

Primero debe disponer de un pc con python y zeroMQ instalado, para posteriormente correr los siguientes comandos cada uno en una terminal distinta:
- python Sensor.py -t <0, 1  ó 2 dependiendo de que tipo de sensor quiere ejecutar> -f <archivo de configuracion (el que se provee de ejemplo se llama Configuration.txt>
- python Proxy.py
- python Cloud.py

