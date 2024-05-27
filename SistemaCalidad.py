import zmq

def sistema_calidad(puerto):
    context = zmq.Context()
    receiver = context.socket(zmq.REP)
    receiver.bind(f"tcp://*:{puerto}")

    print(f"Sistema de Calidad en el puerto {puerto} listo para recibir alertas.")

    while True:
        mensaje = receiver.recv_string()
        print(f"Alerta recibida: {mensaje}")
        receiver.send_string("Alerta recibida y publicada.")

# Iniciar sistema de calidad para cada capa
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sistema de Calidad")
    parser.add_argument("-p", "--puerto", type=int, required=True, help="Puerto en el que escucha el sistema de calidad")
    args = parser.parse_args()
    sistema_calidad(args.puerto)
