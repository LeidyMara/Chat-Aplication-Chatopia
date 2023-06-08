import socket
import threading
import pymysql as sql
from datetime import datetime

MYSQL_ADDON_HOST = 'bvniofu42p5iyagxduki-mysql.services.clever-cloud.com'
MYSQL_ADDON_DB = 'bvniofu42p5iyagxduki'
MYSQL_ADDON_USER = 'ur0djjr0kswx2ypj'
MYSQL_ADDON_PORT = '3306'
MYSQL_ADDON_PASSWORD = 'ax8HJzAc3T6jQsysAK5m'
MYSQL_ADDON_URI='mysql://ur0djjr0kswx2ypj:ax8HJzAc3T6jQsysAK5m@bvniofu42p5iyagxduki-mysql.services.clever-cloud.com:3306/bvniofu42p5iyagxduki'

# Configuración de la base de datos
db_config = {
    'user': MYSQL_ADDON_USER,
    'password': MYSQL_ADDON_PASSWORD,
    'host': MYSQL_ADDON_HOST,
    'database': MYSQL_ADDON_DB,
    'raise_on_warnings': False
}

salas = []  # Lista de salas disponibles

def manejar_conexion(cliente_socket, cliente_direccion):
    # Lógica para iniciar sesión o registrarse
    usuario_registrado = False
    enviar_mensaje_cliente(cliente_socket, "BIENVENIDO A CHATOOPIA\n")
    enviar_mensaje_cliente(cliente_socket, "Por favor seleccione una opción:\n")
    enviar_mensaje_cliente(cliente_socket, "1. Iniciar sesión\n")
    enviar_mensaje_cliente(cliente_socket, "2. Registrarse\n")
    try:
        while not usuario_registrado:
            opcion = cliente_socket.recv(1024).decode('utf-8')
            if opcion == '1':
                usuario_registrado = iniciar_sesion(cliente_socket)
                enviar_mensaje_cliente(cliente_socket, "Control")
            elif opcion == '2':
                usuario_registrado = registrarse(cliente_socket)
            else:
                enviar_mensaje_cliente(cliente_socket, "Opción inválida. Por favor, selecciona una opción válida.")
    except Exception as e:
        print("Error:", str(e))

        if usuario_registrado == True:
            enviar_mensaje_cliente(cliente_socket, "Inicio de sesión exitoso. ¡Bienvenido al chat!")
            opciones_conexion(cliente_socket)

def opciones_conexion(cliente_socket):
    while True:
        try:
            mensaje = cliente_socket.recv(1024).decode('utf-8')
            if mensaje.startswith('#cR'):
                nombre_sala = mensaje.split(' ')[1]
                crear_sala(cliente_socket, nombre_sala)
            elif mensaje.startswith('#gR'):
                nombre_sala = mensaje.split(' ')[1]
                unirse_a_sala(cliente_socket, nombre_sala)
            elif mensaje == '#eR':
                salir_de_sala(cliente_socket)
            elif mensaje == '#exit':
                desconectar_cliente(cliente_socket)
                break
            elif mensaje == '#lR':
                listar_salas(cliente_socket)
            elif mensaje.startswith('#dR'):
                nombre_sala = mensaje.split(' ')[1]
                eliminar_sala(cliente_socket, nombre_sala)
            elif mensaje == '#show users':
                mostrar_usuarios(cliente_socket)
            elif mensaje.startswith('#private'):
                destinatario = mensaje.split(' ')[1]
                mensaje_privado(cliente_socket, destinatario)
            else:
                enviar_a_sala(cliente_socket, mensaje)
        except:
            print("Error al recibir mensajes del cliente.")
            break
    
def iniciar_sesion(cliente_socket):
    # Lógica para iniciar sesión
    enviar_mensaje_cliente(cliente_socket, "Ingrese su nombre de usuario:")
    usuario = cliente_socket.recv(1024).decode('utf-8')
    enviar_mensaje_cliente(cliente_socket, "Ingrese su contraseña:")
    contrasena = cliente_socket.recv(1024).decode('utf-8')

    try:
        cnx = sql.connect(**db_config)
        cursor = cnx.cursor()
        query = "SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s"
        values = (usuario, contrasena)
        cursor.execute(query, values)
        resultado = cursor.fetchone()
        cursor.close()
        cnx.close()
    # Resto del código de conexión a la base de datos
    except Exception as e:
        print("Error al conectar a la base de datos:", str(e))

    if resultado:
        return True
    else:
        enviar_mensaje_cliente(cliente_socket, "Credenciales inválidas. Por favor, intenta nuevamente.")
        return False

def registrarse(cliente_socket):
    # Lógica para registrarse
    enviar_mensaje_cliente(cliente_socket, "Ingrese un nombre de usuario:")
    usuario = cliente_socket.recv(1024).decode('utf-8')
    enviar_mensaje_cliente(cliente_socket, "Ingrese una contraseña:")
    contrasena = cliente_socket.recv(1024).decode('utf-8')
    enviar_mensaje_cliente(cliente_socket, "Ingrese su nombre:")
    nombreUsuario = cliente_socket.recv(1024).decode('utf-8')
    enviar_mensaje_cliente(cliente_socket, "Ingrese su apellido:")
    apellido = cliente_socket.recv(1024).decode('utf-8')
    enviar_mensaje_cliente(cliente_socket, "Ingrese su edad:")
    edad = cliente_socket.recv(1024).decode('utf-8')
    enviar_mensaje_cliente(cliente_socket, "Ingrese su genero:")
    genero = cliente_socket.recv(1024).decode('utf-8')

    cnx = sql.connect(**db_config)
    cursor = cnx.cursor()
    query = "INSERT INTO usuarios (usuario, contrasena, nombreUsuario, apellido, edad, genero) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (usuario, contrasena, nombreUsuario, apellido, edad, genero)
    cursor.execute(query, values)
    cnx.commit()
    cursor.close()
    cnx.close()

    enviar_mensaje_cliente(cliente_socket, "Registro exitoso. Por favor, inicia sesión.")
    return False
    
def crear_sala(cliente_socket, nombre_sala):
    # Lógica para crear una sala
    cnx = sql.connect(**db_config)
    cursor = cnx.cursor()
    query = "INSERT INTO salas (nombre, creador) VALUES (%s, %s)"
    values = (nombre_sala, cliente_socket.getpeername()[0])
    cursor.execute(query, values)
    cnx.commit()
    cursor.close()
    cnx.close()

    sala = Sala(nombre_sala, cliente_socket)
    salas.append(sala)
    enviar_mensaje_cliente(cliente_socket, f"Sala '{nombre_sala}' creada con éxito.")

def unirse_a_sala(cliente_socket, nombre_sala):
    # Lógica para unirse a una sala
    sala = obtener_sala(nombre_sala)
    if sala:
        sala.agregar_cliente(cliente_socket)
        enviar_mensaje_cliente(cliente_socket, f"Te has unido a la sala '{nombre_sala}'.")
    else:
        enviar_mensaje_cliente(cliente_socket, f"No se encontró la sala '{nombre_sala}'.")

def salir_de_sala(cliente_socket):
    # Lógica para salir de una sala
    sala = obtener_sala_cliente(cliente_socket)
    if sala:
        sala.remover_cliente(cliente_socket)
        enviar_mensaje_cliente(cliente_socket, "Has salido de la sala.")
    else:
        enviar_mensaje_cliente(cliente_socket, "No estás en ninguna sala.")

def desconectar_cliente(cliente_socket):
    # Lógica para desconectar a un cliente
    sala = obtener_sala_cliente(cliente_socket)
    if sala:
        sala.remover_cliente(cliente_socket)
    cliente_socket.close()
    print("Cliente desconectado.")

def listar_salas(cliente_socket):
    # Lógica para listar las salas disponibles
    cnx = sql.connect(**db_config)
    cursor = cnx.cursor()
    query = "SELECT nombre FROM salas"
    cursor.execute(query)
    resultado = cursor.fetchall()
    cursor.close()
    cnx.close()

    if len(resultado) > 0:
        mensaje = "Salas disponibles:\n"
        for nombre_sala in resultado:
            mensaje += f"- {nombre_sala[0]}\n"
        enviar_mensaje_cliente(cliente_socket, mensaje)
    else:
        enviar_mensaje_cliente(cliente_socket, "No hay salas disponibles.")

def eliminar_sala(cliente_socket, nombre_sala):
    sala = obtener_sala(nombre_sala)
    if sala and sala.creador == cliente_socket:
        salas.remove(sala)

    #Eliminar sala de la base de datos
        cnx = sql.connect(**db_config)
        cursor = cnx.cursor()
        query = "DELETE FROM salas WHERE nombre = %s"
        values = (nombre_sala,)
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()
        cnx.close()

        enviar_mensaje_cliente(cliente_socket, f"Sala '{nombre_sala}' eliminada.")
    else:
        enviar_mensaje_cliente(cliente_socket, "No tienes permisos para eliminar esa sala.")

def mostrar_usuarios(cliente_socket):
    cnx = sql.connect(**db_config)
    cursor = cnx.cursor()
    query = "SELECT DISTINCT cliente FROM salas"
    cursor.execute(query)
    resultado = cursor.fetchall()
    cursor.close()
    cnx.close()

    mensaje = "Usuarios en el sistema:\n"
    for cliente in resultado:
        mensaje += f"- {cliente[0]}\n"
    enviar_mensaje_cliente(cliente_socket, mensaje)

def mensaje_privado(cliente_socket, destinatario):
    # Lógica para enviar un mensaje privado a un usuario
    sala = obtener_sala_cliente(cliente_socket)
    if sala:
        cliente_destino = sala.obtener_cliente_por_nombre(destinatario)
        if cliente_destino:
            mensaje = f"[Mensaje Privado de {cliente_socket.getpeername()[0]}]: "
            enviar_mensaje_cliente(cliente_destino, mensaje)
        else:
            enviar_mensaje_cliente(cliente_socket, f"No se encontró al usuario '{destinatario}'.")
    else:
        enviar_mensaje_cliente(cliente_socket, "No estás en ninguna sala.")

def enviar_a_sala(cliente_socket, mensaje):
    # Lógica para enviar un mensaje a la sala actual
    sala = obtener_sala_cliente(cliente_socket)
    if sala:
        mensaje = f"[{cliente_socket.getpeername()[0]}]: {mensaje}"
        sala.enviar_mensaje_a_todos(mensaje)
    else:
        enviar_mensaje_cliente(cliente_socket, "No estás en ninguna sala.")

def enviar_mensaje_cliente(cliente_socket, mensaje):
    cliente_socket.send(mensaje.encode('utf-8'))

def obtener_sala(nombre_sala):
    for sala in salas:
        if sala.nombre == nombre_sala:
            return sala
    return None

def obtener_sala_cliente(cliente_socket):
    for sala in salas:
        if cliente_socket in sala.clientes:
            return sala
    return None

class Sala:
    def __init__(self, nombre, creador):
        self.nombre = nombre
        self.creador = creador
        self.clientes = []

    def agregar_cliente(self, cliente_socket):
        self.clientes.append(cliente_socket)

    def remover_cliente(self, cliente_socket):
        self.clientes.remove(cliente_socket)

    def obtener_numero_participantes(self):
        return len(self.clientes)

    def obtener_cliente_por_nombre(self, nombre):
        for cliente in self.clientes:
            if cliente.getpeername()[0] == nombre:
                return cliente
        return None

    def enviar_mensaje_a_todos(self, mensaje):
        for cliente in self.clientes:
            enviar_mensaje_cliente(cliente, mensaje)

def iniciar_servidor():
    host = 'localhost'
    port = 10000

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind((host, port))
    servidor_socket.listen(5)
    print("Servidor en ejecución.")

    while True:
        cliente_socket, cliente_direccion = servidor_socket.accept()
        print("Cliente conectado:", cliente_direccion)

        hilo_cliente = threading.Thread(target=manejar_conexion, args=(cliente_socket, cliente_direccion))
        hilo_cliente.start()

if __name__ == "__main__":
    iniciar_servidor()
