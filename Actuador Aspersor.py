import zmq

def actuador_aspersor():
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:5557")  # Asume que se conecta a este puerto para escuchar señales de los sensores de humo

    print("Actuador aspersor listo para recibir señales.")

    while True:
        mensaje = receiver.recv_string()
        print(f"Recibido: {mensaje}")
       #partes = mensaje.split(', ')
        #tipo = partes[1].split(': ')[1]
        #valor = partes[2].split(': ')[1]

        #if tipo == "humo" and valor == "True":
        print("Actuador aspersor activado debido a la detección de humo.")

# Iniciar el actuador aspersor
actuador_aspersor()
