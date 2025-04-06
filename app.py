import socket
import threading
import logging
from flask import Flask, render_template, request, jsonify

# Configurar logging
logging.basicConfig(filename='servidor_flask.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Función para determinar si un número es primo
def isprime(n):
    """Determina si n es un número primo."""
    try:
        n = int(n)
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True
    except ValueError:
        return None

# Función que inicia el servidor TCP en un hilo separado
def iniciar_servidor_tcp():
    """Inicializa y ejecuta el servidor TCP en segundo plano."""
    host = '127.0.0.1'
    puerto = 8810
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, puerto))
    server_socket.listen(5)
    logging.info(f"Servidor TCP iniciado en {host}:{puerto}")

    try:
        while True:
            # Aceptar conexiones entrantes
            conexion, direccion = server_socket.accept()
            logging.info(f"Conexión TCP establecida con {direccion}")
            
            try:
                # Recibir datos del cliente
                datos = conexion.recv(1024)
                if not datos:
                    logging.warning("Datos vacíos recibidos")
                    continue

                # Intentar convertir los datos recibidos a entero
                try:
                    numero = int(datos.decode().strip())
                    logging.info(f"Número recibido por TCP: {numero}")
                    
                    # Comprobar si el número es primo
                    if isprime(numero):
                        respuesta = f"El número {numero} es primo"
                    else:
                        respuesta = f"El número {numero} no es primo"
                    
                except ValueError:
                    respuesta = "Error: Entrada no es un número entero."
                    logging.error(f"Datos inválidos recibidos por TCP: {datos.decode().strip()}")
                
                # Enviar respuesta al cliente
                conexion.send(respuesta.encode())
                logging.info(f"Respuesta TCP enviada: {respuesta}")
                
            except Exception as e:
                logging.error(f"Error en la conexión TCP: {e}")
            finally:
                conexion.close()
                logging.info(f"Conexión TCP cerrada con {direccion}")
    
    except Exception as e:
        logging.error(f"Error en el servidor TCP: {e}")
    finally:
        server_socket.close()
        logging.info("Socket del servidor TCP cerrado")

# Ruta principal - Renderiza la interfaz web
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para verificar número primo directamente por la web
@app.route('/check_prime', methods=['POST'])
def check_prime():
    data = request.get_json()
    numero = data.get('numero', '')
    
    try:
        numero = int(numero)
        logging.info(f"Número recibido por web: {numero}")
        
        # Comprobar si el número es primo
        if isprime(numero):
            resultado = f"El número {numero} es primo"
        else:
            resultado = f"El número {numero} no es primo"
            
    except ValueError:
        resultado = "Error: Por favor introduce un número entero válido."
        logging.error(f"Datos inválidos recibidos por web: {numero}")
    
    logging.info(f"Respuesta web enviada: {resultado}")
    return jsonify({'resultado': resultado})

# Ruta para verificar número primo usando la conexión TCP
@app.route('/check_prime_tcp', methods=['POST'])
def check_prime_tcp():
    data = request.get_json()
    numero = data.get('numero', '')
    
    try:
        # Crear socket cliente
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8810))
        
        # Enviar número al servidor TCP
        client_socket.send(str(numero).encode())
        
        # Recibir respuesta del servidor TCP
        respuesta = client_socket.recv(1024).decode()
        logging.info(f"Respuesta TCP recibida: {respuesta}")
        
    except ConnectionRefusedError:
        respuesta = "Error: No se pudo conectar al servidor TCP."
        logging.error("Error de conexión al servidor TCP")
    except Exception as e:
        respuesta = f"Error: {e}"
        logging.error(f"Error al usar el servidor TCP: {e}")
    finally:
        client_socket.close()
    
    return jsonify({'resultado': respuesta})

if __name__ == '__main__':
    # Iniciar el servidor TCP en un hilo separado
    tcp_thread = threading.Thread(target=iniciar_servidor_tcp)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    # Iniciar la aplicación Flask
    app.run(debug=True, host='127.0.0.1', port=5000)