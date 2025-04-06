# Servidor de Verificación de Números Primos
Este proyecto implementa un servidor dual (web y TCP) para la verificación de números primos. Proporciona dos interfaces diferentes para verificar si un número es primo o no:

- Una interfaz web a través de Flask que permite a los usuarios verificar números primos mediante un navegador
- Un servidor TCP dedicado que acepta conexiones de socket para verificar números primos programáticamente

## Características
- Servidor web Flask con una interfaz de usuario amigable
- Servidor TCP en segundo plano que opera en paralelo con el servidor web
- Verificación eficiente de números primos
- Registro completo de todas las operaciones en archivo de log
- Dos métodos para verificar números primos:
  - Directamente a través de la interfaz web
  - A través de una conexión TCP

## Requisitos
- Python 3.6+
- Flask
- Los paquetes estándar de Python: socket, threading, logging

## Instalación
1. Clona este repositorio o descarga los archivos
2. Instala las dependencias:

```bash
pip install flask
```

## Uso

### Iniciar el servidor
Para ejecutar el sistema completo (servidor web + servidor TCP):

```bash
python app.py
```

Esto iniciará:
- El servidor web Flask en http://127.0.0.1:5000
- El servidor TCP en 127.0.0.1:8810

### Utilizando la interfaz web
1. Abre tu navegador y visita: http://127.0.0.1:5000
2. Ingresa un número entero en el campo de texto
3. Selecciona uno de los dos métodos de verificación:
   - "Verificar directamente": Utiliza el servidor web directamente
   - "Verificar usando TCP": Hace que el servidor web se comunique con el servidor TCP

### Conectar al servidor TCP desde una aplicación externa
Para verificar números primos programáticamente a través del servidor TCP:

```python
import socket

# Crear una conexión al servidor TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8810))  # Puerto correcto: 8810

# Enviar un número para verificar
numero = "17"
client_socket.send(numero.encode())

# Recibir la respuesta
respuesta = client_socket.recv(1024).decode()
print(respuesta)  # Imprime: "El número 17 es primo"

# Cerrar la conexión
client_socket.close()
```

## Estructura del proyecto
- `app.py`: Contiene tanto la lógica del servidor Flask como la del servidor TCP
- `templates/index.html`: Plantilla HTML para la interfaz web
- `servidor_flask.log`: Archivo de registro que almacena la actividad del servidor
- `README.md`: Este archivo de documentación
- `Informe.md`: Informe técnico detallado sobre la implementación

## Interfaz Web
La interfaz web permite:
- Ingresar un número entero para verificar
- Elegir entre verificación directa o mediante TCP
- Ver el resultado de la verificación
- Recibir mensajes de error claros en caso de entrada inválida

## Algorítmo de Verificación
El servidor verifica si un número es primo utilizando un algoritmo optimizado que:
- Maneja casos especiales para números pequeños (1, 2, 3)
- Comprueba divisibilidad por 2 y 3
- Utiliza un patrón de salto de 6 para verificar divisores potenciales
- Maneja errores de entrada adecuadamente

## Registro (Logging)
Todas las operaciones del servidor se registran en el archivo `servidor_flask.log` con información detallada:
- Conexiones TCP establecidas y cerradas
- Números recibidos y resultados enviados
- Errores y excepciones
- Marcas de tiempo para cada evento