import zmq
import time
import random
import threading
import argparse

#Porcentajes de funcionalidad de los sensores
correcto = 0
fuera_rango = 0
error = 0

cont_total=0
cont_correcto = 0
cont_fuera_rango = 0
cont_error = 0

#Lectura del archivo de configuración
def Config_Sensor_Archivo(file_path):
    with open(file_path, 'r') as file:
        correcto = float(file.readline().strip())
        fuera_rango = float(file.readline().strip())
        error = float(file.readline().strip())
    return correcto, fuera_rango, error

#Meter todos los senosores

#Sensor de humo
def Sensor_Humo(sensor_id):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:5555")

    while True:
        detecta_humo = random.choice([True, False])  # Simula la detección de humo de manera aleatoria
        timestamp = time.time()
        mensaje = f"sensor_id: {sensor_id}, tipo: humo, valor: {detecta_humo}, timestamp: {timestamp}"
        socket.send_string(mensaje)
        print(f"Enviado: {mensaje}")
        time.sleep(random.randint(3, 6))  # Simula un intervalo aleatorio entre detecciones

#Sensor de temperatura
def Sensor_Temperatura(sensor_id):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:5555")
    global cont_total
    global cont_correcto
    global cont_fuera_rango
    global cont_error

    while True:
        temperatura = 0
        #Cambiar de acuerdo a los procentajes      
        if cont_total == 0:
            temperatura = random.uniform(11, 38)
            cont_total += 1
            if temperatura >= 11 and temperatura <= 29.4:
                cont_correcto += 1
            else:
                cont_fuera_rango += 1
        else:
            if cont_total*correcto >= cont_correcto:
                temperatura = random.uniform(11, 29.4)
                cont_total += 1
                cont_correcto += 1
            elif cont_total*fuera_rango >= cont_fuera_rango:
                temperatura = random.uniform(29.5, 38)
                cont_total += 1
                cont_fuera_rango += 1
            elif cont_total*error >= cont_error:
                temperatura = random.uniform(-10,-1)
                cont_total += 1
                cont_error += 1
        
        print(f"Temperatura: {temperatura}")
        print(f"Total: {cont_total}")
        print(f"Correcto: {cont_correcto}, Fuera de rango: {cont_fuera_rango}, Error: {cont_error}")
        #Se deja normal
        timestamp = time.time()
        mensaje = f"sensor_id: {sensor_id}, tipo: temperatura, valor: {temperatura}, timestamp: {timestamp}"
        socket.send_string(mensaje)
        print(f"Enviado: {mensaje}")
        time.sleep(6)  # Cada 6 segundos según el documento

#Sensor de humedad
def Sensor_Humedad(sensor_id):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:5555")
    global cont_total
    global cont_correcto
    global cont_fuera_rango
    global cont_error

    while True:
        humedad = 0
        #Cambiar de acuerdo a los procentajes      
        if cont_total == 0:
            humedad = random.uniform(40, 100)
            cont_total += 1
            if humedad >= 70 and humedad <= 100:
                cont_correcto += 1
            else:
                cont_fuera_rango += 1
        else:
            if cont_total*correcto >= cont_correcto:
                humedad = random.uniform(70, 100)
                cont_total += 1
                cont_correcto += 1
            elif cont_total*fuera_rango >= cont_fuera_rango:
                humedad = random.uniform(40, 69)
                cont_total += 1
                cont_fuera_rango += 1
            elif cont_total*error >= cont_error:
                humedad = random.uniform(-10,-1)
                cont_total += 1
                cont_error += 1
        
        print(f"Humedad: {humedad}")
        print(f"Total: {cont_total}")
        print(f"Correcto: {cont_correcto}, Fuera de rango: {cont_fuera_rango}, Error: {cont_error}")
        timestamp = time.time()
        mensaje = f"sensor_id: {sensor_id}, tipo: humedad, valor: {humedad}, timestamp: {timestamp}"
        socket.send_string(mensaje)
        print(f"Enviado: {mensaje}")
        time.sleep(5)  # Cada 5 segundos según el ejemplo

#Meter en un condicional de acuerdo al sensor
def Tipo_Sensor(tipo):
    if tipo == 0:
        #Sensor de humo
        for i in range(0, 10):  # Usando IDs 0-10 para los sensores de humo
            threading.Thread(target=Sensor_Humo, args=(i+1,)).start()
    elif tipo == 1:
        #Sensor de temperatura
        for i in range(10, 20):  # Usando IDs 11-20 para los sensores de temperatura
            threading.Thread(target=Sensor_Temperatura, args=(i+1,)).start()
    elif tipo == 2:
        #Sensor de humedad
        for i in range(20, 30):  # Usando IDs 21-30 para los sensores de humedad
            threading.Thread(target=Sensor_Humedad, args=(i+1,)).start()

if __name__ == "__main__":
    argumentos = argparse.ArgumentParser("Inicializar sensor")
    argumentos.add_argument("-t", "--tipo", choices=[0,1,2], type=int, help="Tipo de sensor")
    argumentos.add_argument("-f", "--file", type=str, help="Archivo de configuración")
    args = argumentos.parse_args()
    correcto, fuera_rango, error = Config_Sensor_Archivo(args.file)
    Tipo_Sensor(args.tipo)
    