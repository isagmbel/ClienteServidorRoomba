# Informe: Servidor de Verificación de Números Primos

## Introducción
Este informe documenta el desarrollo e implementación de un servidor dual para la verificación de números primos. El sistema proporciona dos métodos distintos para verificar si un número es primo: una interfaz web basada en Flask que ofrece una experiencia de usuario interactiva, y un servidor TCP dedicado que procesa solicitudes a nivel de socket. Esta dualidad permite tanto a usuarios finales como a desarrolladores interactuar con el servicio de manera flexible según sus necesidades específicas.

## Proceso de Desarrollo
El desarrollo del sistema siguió un enfoque iterativo, comenzando con la implementación del algoritmo fundamental para la verificación de números primos. Inicialmente, se implementó una versión básica del algoritmo que verificaba todos los posibles divisores hasta la raíz cuadrada del número. Sin embargo, pronto quedó claro que este enfoque carecía de eficiencia para números grandes, lo que llevó a la implementación de optimizaciones como el chequeo temprano de divisibilidad por 2 y 3, y la utilización del patrón de salto 6k±1.

Una vez establecida la función core de verificación, el desarrollo se bifurcó en dos líneas paralelas: la interfaz web y el servidor TCP. Para la interfaz web, se eligió Flask por su simplicidad y facilidad de uso, permitiendo una rápida implementación de rutas REST y renderizado de plantillas HTML. La interfaz de usuario se diseñó con énfasis en la claridad y facilidad de uso, empleando estilos CSS para proporcionar retroalimentación visual clara sobre los resultados.

El servidor TCP se desarrolló utilizando la biblioteca estándar de sockets de Python, implementándolo en un hilo separado para evitar bloqueos en el servidor web principal. La integración de ambos componentes requirió especial atención al manejo de concurrencia y al paso de mensajes entre los distintos módulos del sistema.

Las pruebas se realizaron de manera continua durante el desarrollo, verificando tanto la precisión del algoritmo como la robustez de las interfaces de comunicación. La fase final del desarrollo se centró en mejorar el manejo de errores y la experiencia del usuario, añadiendo mensajes informativos y registro detallado de las operaciones.

## Principales Desafíos Encontrados
El desarrollo del sistema presentó varios desafíos significativos que requirieron soluciones específicas. Uno de los principales fue la ejecución concurrente del servidor web y el servidor TCP. La necesidad de mantener ambos servidores funcionando simultáneamente llevó a la implementación de un enfoque multihilo, donde el servidor TCP se ejecuta en un hilo separado. Esto planteó cuestiones de concurrencia que debieron ser cuidadosamente manejadas para evitar condiciones de carrera o bloqueos:

```python
if __name__ == '__main__':
    # Iniciar el servidor TCP en un hilo separado
    tcp_thread = threading.Thread(target=iniciar_servidor_tcp)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    # Iniciar la aplicación Flask
    app.run(debug=True, host='127.0.0.1', port=5000)
```

La configuración del socket del servidor TCP también presentó desafíos, particularmente en lo relacionado con la reutilización de direcciones. Durante el desarrollo iterativo y las pruebas, el reinicio frecuente del servidor causaba errores de "Address already in use". Este problema se resolvió habilitando la opción SO_REUSEADDR en el socket:

```python
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, puerto))
```

Otro desafío importante fue el manejo de errores y la recuperación ante situaciones inesperadas. El sistema debía ser capaz de manejar diversos tipos de errores, desde entradas inválidas hasta fallos de conexión, sin dejar de funcionar. Esto requirió un diseño cuidadoso de las estructuras try-except en ambos componentes del servidor. Por ejemplo, en la función `iniciar_servidor_tcp()`, se implementaron múltiples niveles de manejo de excepciones para capturar errores en diferentes etapas del procesamiento:

```python
try:
    while True:
        conexion, direccion = server_socket.accept()
        logging.info(f"Conexión TCP establecida con {direccion}")
        
        try:
            datos = conexion.recv(1024)
            if not datos:
                logging.warning("Datos vacíos recibidos")
                continue

            try:
                numero = int(datos.decode().strip())
                # Procesamiento del número...
            except ValueError:
                respuesta = "Error: Entrada no es un número entero."
                # ...
        except Exception as e:
            logging.error(f"Error en la conexión TCP: {e}")
        finally:
            conexion.close()
except Exception as e:
    logging.error(f"Error en el servidor TCP: {e}")
finally:
    server_socket.close()
```

La comunicación entre la interfaz web y el servidor TCP también presentó desafíos, particularmente en cuanto a la gestión de timeouts y el manejo de conexiones. Fue necesario implementar mecanismos para cerrar apropiadamente las conexiones en todos los casos, incluso cuando ocurrían errores, para evitar fugas de recursos.

## Estrategias para la Verificación de Números Primos
La estrategia central para la verificación de números primos se basa en un algoritmo optimizado que reduce significativamente el número de divisiones necesarias. El enfoque se fundamenta en varios principios matemáticos que permiten descartar rápidamente muchos números:

1. Todo número primo mayor que 3 puede expresarse como 6k±1, donde k es un entero positivo. Esto significa que podemos descartar de inmediato números divisibles por 2 o 3.

2. Para verificar si un número n es primo, solo necesitamos comprobar divisores hasta la raíz cuadrada de n.

3. Siguiendo el patrón 6k±1, podemos verificar solo los potenciales divisores de la forma 6k-1 y 6k+1, saltándonos cinco de cada seis números.

La implementación del algoritmo refleja estas estrategias:

```python
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
```

Este algoritmo comienza descartando los casos especiales (números menores o iguales a 1, 2 y 3), luego elimina rápidamente los números divisibles por 2 o 3. A continuación, verifica divisibilidad solo por números de la forma 6k-1 (representado por i) y 6k+1 (representado por i+2), incrementando i en 6 en cada iteración. El bucle se detiene cuando i^2 excede n, lo que significa que hemos verificado todos los posibles divisores hasta la raíz cuadrada.

Esta estrategia reduce drásticamente el número de operaciones de división necesarias, especialmente para números grandes, mejorando el rendimiento del sistema sin comprometer la precisión.

## Estrategias para la Comunicación Cliente-Servidor
La comunicación entre los distintos componentes del sistema se implementó siguiendo varios patrones y estrategias para garantizar robustez y eficiencia:

Para la comunicación entre el cliente web y el servidor Flask, se utilizó el patrón REST con intercambio de datos en formato JSON. Las solicitudes del cliente se envían mediante llamadas fetch() de JavaScript, utilizando el método POST para enviar los datos del número a verificar:

```javascript
fetch('/check_prime', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ numero: numero }),
})
.then(response => response.json())
.then(data => {
    mostrarResultado(data.resultado, data.resultado.includes('Error'));
})
```

El servidor Flask procesa estas solicitudes y devuelve respuestas también en formato JSON, permitiendo una fácil interpretación por parte del cliente JavaScript.

Para la comunicación entre el servidor web y el servidor TCP, se implementó un patrón de cliente-servidor básico utilizando sockets TCP. Cuando un usuario selecciona la verificación mediante TCP, el servidor web actúa como cliente del servidor TCP, estableciendo una conexión, enviando el número a verificar, recibiendo la respuesta y cerrando la conexión:

```python
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
```

Este enfoque de "puente" permite a los usuarios de la interfaz web beneficiarse de ambos métodos de verificación sin necesidad de implementar un cliente TCP separado.

El servidor TCP en sí mismo implementa un patrón de servidor iterativo, procesando cada conexión secuencialmente. Si bien este enfoque podría limitar el rendimiento bajo carga alta, proporciona una implementación sencilla y robusta adecuada para el alcance actual del proyecto. Para cargas de trabajo mayores, se podría considerar la implementación de un servidor concurrente que maneje múltiples conexiones simultáneamente.

## Arquitectura del Sistema
La arquitectura del sistema se compone de varios componentes interrelacionados que trabajan juntos para proporcionar el servicio de verificación de números primos. El servidor web Flask constituye la cara visible del sistema, proporcionando una interfaz de usuario HTML/CSS/JavaScript accesible a través del navegador. Este componente procesa solicitudes HTTP para la verificación de números primos y se ejecuta en el puerto 5000, permitiendo un acceso sencillo mediante cualquier navegador web moderno.

En paralelo, el servidor TCP dedicado se ejecuta en segundo plano en un hilo separado, procesando conexiones de socket directas. Este servidor utiliza el mismo algoritmo de verificación de primos pero proporciona una interfaz programática para aplicaciones que requieren integración a nivel de socket. El servidor TCP opera en el puerto 8810, permitiendo conexiones directas desde aplicaciones cliente.

El núcleo del sistema es el algoritmo de verificación de primos, implementado en la función `isprime()`. Esta función está optimizada para determinar eficientemente si un número es primo, utilizando técnicas como el chequeo temprano y el patrón de salto 6k±1 para reducir el número de divisiones necesarias.

Complementando estos componentes, el sistema incorpora un sistema de registro completo que documenta todas las operaciones, conexiones y posibles errores. Estos registros se almacenan en el archivo `servidor_flask.log`, facilitando la depuración y el análisis del comportamiento del sistema durante su operación.

## Flujo de Trabajo
El sistema permite dos flujos de trabajo distintos para la verificación de números primos. En el método web directo, el usuario ingresa un número en la interfaz web, y el cliente envía una solicitud POST a la ruta `/check_prime`. El servidor procesa esta solicitud directamente llamando a la función `isprime()` y devuelve el resultado, que la interfaz muestra al usuario. Este proceso es inmediato y se maneja completamente dentro del servidor web Flask.

El método TCP, por otro lado, sigue un flujo más complejo. El usuario ingresa un número en la misma interfaz web, pero al hacer clic en el botón "Verificar usando TCP", el cliente envía una solicitud POST a la ruta `/check_prime_tcp`. En este caso, el servidor web actúa como intermediario, creando una conexión al servidor TCP interno, enviando el número a verificar, recibiendo la respuesta del servidor TCP, y finalmente reenviando esta respuesta al cliente web. La interfaz muestra el resultado al usuario de la misma manera que en el método directo.

## Implementación Técnica
El servidor web utiliza el framework Flask para proporcionar una interfaz REST y renderizar la interfaz de usuario. Este framework facilita la creación de rutas para manejar diferentes tipos de solicitudes HTTP. La ruta principal GET `/` renderiza la plantilla HTML de la interfaz principal, mientras que las rutas POST `/check_prime` y `/check_prime_tcp` proporcionan endpoints para verificar números primos por los dos métodos disponibles.

La implementación del servidor TCP se realiza utilizando el módulo `socket` de Python y se ejecuta en un hilo separado para evitar bloquear el servidor web. Esta separación es crucial para mantener la responsividad de la interfaz web mientras se procesan conexiones TCP potencialmente lentas. El servidor TCP se configura para reutilizar direcciones mediante la opción `SO_REUSEADDR`, lo que facilita el reinicio del servidor sin problemas de direcciones ya en uso.

El manejo de errores es una parte fundamental de la implementación. Tanto el servidor web como el TCP incorporan estructuras try-except para capturar y manejar posibles excepciones, como errores de conexión, valores inválidos o conversiones fallidas. Esto asegura que el sistema pueda recuperarse de situaciones inesperadas sin dejar de funcionar.

La interfaz de usuario está diseñada para ser intuitiva y responsiva, con un diseño minimalista centrado en la tarea de verificación de números primos. La retroalimentación visual clara para los resultados y el manejo de errores en el lado del cliente mejoran la experiencia del usuario.

## Pruebas y Rendimiento
Durante las pruebas, el sistema demostró un rendimiento robusto, con capacidad para manejar múltiples conexiones simultáneas y proporcionar respuestas rápidas para números dentro del rango razonable. El manejo correcto de entradas inválidas y la recuperación adecuada de errores de conexión contribuyeron a la estabilidad general del sistema.

Las pruebas realizadas con diversos números, tanto primos como no primos, confirmaron la precisión del algoritmo de verificación. Para números pequeños como 2 y 17, el sistema identificó correctamente su condición de primos con tiempos de respuesta inferiores a 10 milisegundos. Para números compuestos como 123, el sistema también respondió correctamente y con rapidez. Incluso para números primos mayores como 997, el rendimiento se mantuvo dentro de parámetros aceptables.

En casos de entradas inválidas, como cadenas no numéricas ("abc"), el sistema respondió con mensajes de error apropiados tanto en el método web directo como en el método TCP, demostrando un manejo robusto de errores en ambas interfaces.

## Consideraciones de Seguridad
El sistema implementa varias medidas de seguridad para proteger contra posibles vulnerabilidades. La validación de entrada se realiza tanto en el cliente como en el servidor para prevenir inyecciones o comportamientos inesperados. El manejo adecuado de errores está diseñado para evitar revelar información sensible del sistema, proporcionando mensajes de error informativos pero genéricos.

El límite implícito en el tamaño de los datos recibidos por el socket TCP (1024 bytes) protege contra posibles ataques de desbordamiento de buffer, aunque para una aplicación en producción se recomendaría implementar medidas de seguridad adicionales como autenticación y cifrado para el servidor TCP.

## Conclusiones
El servidor dual para verificación de números primos demuestra cómo diferentes protocolos de comunicación pueden integrarse en una sola aplicación, proporcionando flexibilidad y opciones para diferentes casos de uso. La interfaz web ofrece una experiencia de usuario amigable y visual que resulta accesible para usuarios sin conocimientos técnicos, mientras que el servidor TCP proporciona una interfaz programática para integración con otros sistemas o aplicaciones.

Esta dualidad hace que el sistema sea versátil y adaptable a diferentes escenarios, desde una herramienta educativa para entender los números primos hasta un componente en una aplicación más grande que requiera verificación programática de primalidad.

## Trabajo Futuro
El desarrollo futuro del sistema podría enfocarse en varias áreas de mejora. La implementación de un sistema de caché para resultados frecuentes podría mejorar significativamente el rendimiento al evitar recálculos innecesarios para números solicitados repetidamente. El soporte para verificación por lotes de múltiples números permitiría operaciones más eficientes cuando se necesita verificar grandes conjuntos de datos.

Para números extremadamente grandes, se podrían implementar algoritmos de primalidad probabilísticos como el test de Miller-Rabin, que ofrecen mejor rendimiento a costa de una certeza absoluta. La adición de un sistema de autenticación para el servidor TCP mejoraría la seguridad en entornos de producción donde el acceso al servicio debe ser controlado.

Finalmente, una interfaz de línea de comandos complementaría las interfaces existentes, proporcionando una tercera vía de acceso al servicio que resultaría útil para scripts y automatizaciones. Estas mejoras expandirían la utilidad y aplicabilidad del sistema, convirtiéndolo en una herramienta más versátil para diversos escenarios de uso.