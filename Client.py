import socket
import threading

def recibir_mensajes(sock):
    while True:
        try:
            mensaje = sock.recv(1024).decode('utf-8')
            print(mensaje)
        except:
            print("Error al recibir mensajes del servidor.")
            sock.close()
            break

def enviar_mensajes(sock):
    while True:
        mensaje = input()
        sock.send(mensaje.encode('utf-8'))

def conectar_al_servidor():
    host = 'localhost'
    port = 10000

    try:
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((host, port))
        print("Conexión exitosa al servidor.")

        hilo_recibir = threading.Thread(target=recibir_mensajes, args=(cliente_socket,))
        hilo_recibir.start()

        hilo_enviar = threading.Thread(target=enviar_mensajes, args=(cliente_socket,))
        hilo_enviar.start()
    except:
        print("Error al conectar al servidor.")

if __name__ == "__main__":
    conectar_al_servidor()
