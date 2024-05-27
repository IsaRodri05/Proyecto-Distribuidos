import zmq
import time
from collections import deque
import threading

# Configuración inicial de ZeroMQ para recibir datos del proxy
context = zmq.Context()

# Lista de direcciones a las que se puede conectar
direcciones = ["tcp://*:5556", "tcp://*:5559"]

def configurar_receiver(direccion):
    """Configura el receiver para recibir datos del proxy en la dirección dada."""
    receiver = context.socket(zmq.PULL)
    receiver.bind(direccion)
    return receiver

def inicializar_receiver():
    """Intenta bind el receiver a diferentes direcciones."""
    for direccion in direcciones:
        try:
            receiver = configurar_receiver(direccion)
            print(f"Conectado al proxy en {direccion}")
            return receiver, direccion
        except zmq.ZMQError as e:
            print(f"Error al conectar a {direccion}: {e}")
    raise Exception("No se pudo conectar a ningún proxy")

def reconectar_receiver(direccion_index):
    """Intenta reconectar el receiver a diferentes direcciones de forma cíclica."""
    while True:
        try:
            direccion = direcciones[direccion_index]
            receiver = configurar_receiver(direccion)
            print(f"Re-conectado al proxy en {direccion}")
            return receiver, direccion_index
        except zmq.ZMQError as e:
            print(f"Error al conectar a {direccion}: {e}")
            direccion_index = (direccion_index + 1) % len(direcciones)
            print("Reintentando conexión a los proxies en 5 segundos...")
            time.sleep(5)  # Esperar antes de intentar reconectar

# Inicialización del receiver
receiver, direccion_actual = inicializar_receiver()

# Configuración para enviar alertas al sistema de calidad
sender_calidad = context.socket(zmq.REQ)
sender_calidad.connect("tcp://localhost:5560")  # Sistema de calidad en la capa Cloud

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
    global receiver, direccion_actual
    direccion_actual_index = direcciones.index(direccion_actual)
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
                enviar_alerta_calidad(alerta)
        else:
            print("No se recibieron humedades en este intervalo.")  # Debugging
            # Intentar reconectar si no se recibieron datos
            receiver.close()
            direccion_actual_index = (direccion_actual_index + 1) % len(direcciones)
            receiver, direccion_actual_index = reconectar_receiver(direccion_actual_index)
            direccion_actual = direcciones[direccion_actual_index]

def enviar_alerta_calidad(alerta):
    """Envía una alerta al Sistema de Calidad y espera una respuesta."""
    sender_calidad.send_string(alerta)
    respuesta = sender_calidad.recv_string()
    print(f"Respuesta del sistema de calidad: {respuesta}")

def recibir_mensajes():
    """Recibe y procesa mensajes de manera continua."""
    global receiver, direccion_actual
    direccion_actual_index = direcciones.index(direccion_actual)
    while True:
        try:
            mensaje = receiver.recv_string(zmq.NOBLOCK)  # Intentar recibir sin bloquear
            print("\nMensaje recibido de tipo: ")
            procesar_mensaje(mensaje)
        except zmq.Again:
            time.sleep(1)  # Esperar un segundo antes de intentar nuevamente
            continue
        except zmq.ZMQError as e:
            print(f"Error al recibir mensaje: {e}")
            receiver.close()
            direccion_actual_index = (direccion_actual_index + 1) % len(direcciones)
            receiver, direccion_actual_index = reconectar_receiver(direccion_actual_index)
            direccion_actual = direcciones[direccion_actual_index]

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
