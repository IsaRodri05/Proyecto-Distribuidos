import zmq
import time
from collections import deque
import threading

# Configuración inicial de ZeroMQ para recibir datos del proxy
context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5556")  # Este puerto debe coincidir con el puerto de conexión del proxy

# Configuración para enviar alertas al sistema de calidad
sender_calidad = context.socket(zmq.PUSH)
sender_calidad.connect("tcp://localhost:5558")  # Sistema de calidad en la capa Cloud

# Buffers para mantener las humedades recibidas del proxy
humedades_recibidas = deque()
humedades_diarias = deque(maxlen=4)  # Mantiene las humedades promedio diarias
humedades_mensuales = []

# Umbral para la humedad mensual
UMBRAL_HUMEDAD_MENSUAL = 30.0  # Este es el umbral de ejemplo

def guardar_dato(mensaje):
    """Guarda el dato recibido en un archivo de texto."""
    with open("datos_cloud.txt", "a") as archivo:
        archivo.write(mensaje + "\n")

def procesar_mensaje(mensaje):
    """Procesa el mensaje recibido del proxy."""
    try:
        if "Promedio de humedad" in mensaje:
            print("humedad\n")
            partes = mensaje.split(": ")
            promedio_humedad = float(partes[1].replace("%", ""))
            humedades_recibidas.append(promedio_humedad)
            guardar_dato(mensaje)
        else:
            print("temperatura/humo\n")
            guardar_dato(mensaje)  # Guardar cualquier otro mensaje recibido
    except ValueError as e:
        print(f"Error al procesar el mensaje: {e}")
        guardar_dato(f"Error al procesar el mensaje: {mensaje}")

def calcular_humedad_mensual():
    """Calcula la humedad mensual cada 20 segundos."""
    while True:
        time.sleep(20)
        print("Calculando humedad mensual...")  # Debugging
        if humedades_recibidas:
            print(f"Humedades recibidas: {list(humedades_recibidas)}")  # Debugging
            promedio_mensual = sum(humedades_recibidas) / len(humedades_recibidas)
            humedades_recibidas.clear()
            print(f"Promedio mensual de humedad: {promedio_mensual}")  # Debugging
            guardar_dato(f"Promedio mensual de humedad: {promedio_mensual}%")
            if promedio_mensual < UMBRAL_HUMEDAD_MENSUAL:
                alerta = f"Alerta de baja humedad mensual: {promedio_mensual}%"
                sender_calidad.send_string(alerta)
                guardar_dato(alerta)
                print(alerta)
        else:
            print("No se recibieron humedades en este intervalo.")  # Debugging

def recibir_mensajes():
    """Recibe y procesa mensajes de manera continua."""
    while True:
        try:
            mensaje = receiver.recv_string()  # Intentar recibir sin bloquear
            print("\nMensaje recibido de tipo: ")
            procesar_mensaje(mensaje)
        except zmq.Again:
            time.sleep(1)  # Esperar un segundo antes de intentar nuevamente
            continue

if __name__ == "__main__":
    print("Iniciando servicio Cloud...")  # Debugging
    # Iniciar el cálculo de humedad mensual en un hilo separado
    threading.Thread(target=calcular_humedad_mensual, daemon=True).start()

    # Iniciar la recepción de mensajes
    try:
        recibir_mensajes()
    except KeyboardInterrupt:
        print("\nFinalizando el servicio Cloud...")
    except Exception as e:
        print(f"Error: {e}")
