import zmq
import time
from collections import deque
import threading
import statistics

# Configuración inicial de ZeroMQ para recibir datos de los sensores
context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5555")

# Configuración para enviar datos procesados a la capa Cloud y al Actuador Aspersor
sender_cloud = context.socket(zmq.PUSH)
sender_cloud.connect("tcp://localhost:5556")  # Capa Cloud
sender_aspersor = context.socket(zmq.PUSH)
sender_aspersor.connect("tcp://localhost:5557")  # Actuador Aspersor


# Buffers para mantener las últimas N temperaturas y humedades
temperaturas = deque(maxlen=10)
humedades = deque(maxlen=10)

# Estadísticas
mensajes_enviados = 0
tamaño_mensajes_enviados = 0  # Tamaño total en bytes (sin usar)
alertas_generadas = {"temperatura": 0, "humo": 0}
datos_mal_formados = 0  # Contador de datos con formato incorrecto
tiempos_comunicacion = []  # Para almacenar los tiempos de comunicación

def guardar_dato(mensaje):
    """Guarda el dato recibido en un archivo de texto."""
    with open("datos_sensores.txt", "a") as archivo:
        archivo.write(mensaje + "\n")

def enviar_mensaje(socket, mensaje):
    """Envía un mensaje y actualiza las estadísticas."""
    global mensajes_enviados, tamaño_mensajes_enviados
    mensajes_enviados += 1
    mensaje_bytes = mensaje.encode('utf-8')
    tamaño_mensajes_enviados += len(mensaje_bytes)
    
    # Medir el tiempo de envío
    inicio = time.time()
    socket.send_string(mensaje)
    fin = time.time()
    tiempos_comunicacion.append(fin - inicio)

def procesar_mensaje(mensaje):
    """Procesa el mensaje recibido de un sensor."""
    global mensajes_enviados, alertas_generadas, datos_mal_formados
    
    try:
        partes = mensaje.split(', ')
        if len(partes) != 4:  # Validar la cantidad correcta de partes
            raise ValueError("Formato incorrecto")
        sensor_id, tipo, valor, timestamp = [parte.split(': ')[1] for parte in partes]

        if tipo not in ["temperatura", "humedad", "humo"]:  # Validar tipo de sensor
            raise ValueError("Tipo de sensor desconocido")
        
        # Validación para evitar valores negativos en temperatura y humedad
        if tipo in ["temperatura", "humedad"]:
            valor = float(valor)
            if valor < 0:
                raise ValueError("Valor negativo")
        
        # Guardar cada medición recibida para persistencia
        guardar_dato(mensaje)
        
        if tipo == "temperatura":
            temperatura = float(valor)
            temperaturas.append(temperatura)
            if temperatura > 29.4:  # Umbral de alerta de temperatura
                alerta = f"Alerta alta temperatura: {temperatura}° sensor: {sensor_id} a las {time.ctime(float(timestamp))}"
                print(alerta)
                alertas_generadas["temperatura"] += 1
                enviar_mensaje(sender_cloud, alerta)
                guardar_dato(alerta)

        elif tipo == "humedad":
            humedad = float(valor)
            humedades.append(humedad)

        elif tipo == "humo" and valor == "True":
            alerta = f"Actuador aspersor activado por sensor {sensor_id} a las {time.ctime(float(timestamp))}\n"
            print(alerta)
            alertas_generadas["humo"] += 1
            enviar_mensaje(sender_aspersor, alerta)

    except ValueError as e:
        print(f"Error al procesar el mensaje: {e}")
        datos_mal_formados += 1
        return  # No procesar este mensaje

def calcular_publicar_promedios():
    """Calcula y publica el promedio de temperaturas y humedades."""
    while True:
        if temperaturas:
            promedio_temp = sum(temperaturas) / len(temperaturas)
            print(f"\n----------------Promedio de temperatura: {promedio_temp}°----------------\n")
        if humedades:
            promedio_hum = sum(humedades) / len(humedades)
            print(f"\n----------------Promedio de humedad: {promedio_hum}%----------------\n")
            mensaje_promedio_hum = f"Promedio de humedad: {promedio_hum}%"
            enviar_mensaje(sender_cloud, mensaje_promedio_hum)
        time.sleep(5)  # Calcular cada 5 segundos

def mostrar_estadisticas_comunicacion():
    """Muestra las estadísticas de tiempos de comunicación."""
    if tiempos_comunicacion:
        promedio = statistics.mean(tiempos_comunicacion)
        desviacion = statistics.stdev(tiempos_comunicacion) if len(tiempos_comunicacion) > 1 else 0
        print(f"\nPromedio de tiempos de comunicación: {promedio:.6f} segundos")
        print(f"Desviación estándar de tiempos de comunicación: {desviacion:.6f} segundos\n")
    else:
        print("No hay tiempos de comunicación registrados.")

# Iniciar el cálculo y publicación de promedios en un hilo separado
threading.Thread(target=calcular_publicar_promedios, daemon=True).start()

try:
    while True:
        mensaje = receiver.recv_string()
        print(f"Recibido: {mensaje}")
        procesar_mensaje(mensaje)
except KeyboardInterrupt:
    print("\nFinalizando el proxy...")
    print(f"-Total de mensajes enviados: {mensajes_enviados}")
    print(f"-Tamaño total de mensajes enviados: {tamaño_mensajes_enviados} bytes")
    for tipo, cantidad in alertas_generadas.items():
        print(f"-Alertas de {tipo}: {cantidad}")
    print(f"*Datos con mal formato recibidos: {datos_mal_formados}")
    mostrar_estadisticas_comunicacion()
except Exception as e:
    print(f"Error: {e}")
