📊 Apache Bench - Test de Rendimiento
===============================================================================
Nivel: 🟢 Básico
Categoria: Testing/Performance
Herramienta: Apache Bench (ab)

===============================================================================
📋 DESCRIPCION
===============================================================================

Este script automatiza pruebas de rendimiento HTTP usando Apache Bench (ab).
Lanza un numero configurable de peticiones contra un servidor web y recoge
metricas clave como:

Requests por segundo

Tiempo de respuesta promedio

Tasa de transferencia

Latencia (percentiles 50%, 90%, 99%)

===============================================================================
🎯 ¿PARA QUE SIRVE?
===============================================================================

Testing de servidores web: Medir cuantas peticiones puede manejar tu servidor

Comparativa de configuraciones: Probar nginx vs apache, diferentes modulos

Deteccion de cuellos de botella: Identificar limites antes de produccion

Aprendizaje: Entender metricas de rendimiento web de forma practica

===============================================================================
📦 REQUISITOS
===============================================================================

Instalar Apache Bench (si no lo tienes):

Debian/Ubuntu:
sudo apt install apache2-utils

RHEL/CentOS/Fedora:
sudo yum install httpd-tools

macOS:
Ya viene instalado con Xcode Command Line Tools

Verificar instalacion:
ab -V

===============================================================================
🚀 USO DEL SCRIPT
===============================================================================

Sintaxis:
./scripts/bash/test_benchmark.sh [URL] [REQUESTS] [CONCURRENT]

Parametros:

URL URL objetivo del test Default: http://127.0.0.1:8000
REQUESTS Numero total de peticiones Default: 100
CONCURRENT Peticiones simultaneas Default: 10

Ejemplos:

Test basico contra servidor local:
./scripts/bash/test_benchmark.sh http://127.0.0.1:8000 500 20

Test rapido con valores por defecto:
./scripts/bash/test_benchmark.sh

Test contra httpbin.org:
./scripts/bash/test_benchmark.sh http://httpbin.org/get 100 10

===============================================================================
🔧 FLAGS DE APACHE BENCH (ab) - REFERENCIA COMPLETA
===============================================================================

-n Numero total de peticiones
Ejemplo: -n 1000
Lanza exactamente 1000 requests al servidor

-c Peticiones concurrentes (paralelas)
Ejemplo: -c 50
50 hilos simultaneos haciendo requests
(Fuente: Baeldung)

-t Tiempo maximo de prueba en segundos
Ejemplo: -t 60
La prueba dura 60 segundos maximo (en lugar de numero fijo)
(Fuente: linux.die.net)

-k Habilita HTTP Keep-Alive (reutiliza conexiones)
Ejemplo: -k
Simula comportamiento real de navegadores
(Fuente: Apache)

-s Timeout por socket en segundos
Ejemplo: -s 10
Si un request tarda mas de 10s, se considera fallido

-H Anade cabeceras HTTP personalizadas
Ejemplo: -H "Authorization: Bearer token123"
Util para testear APIs con autenticacion

-p Archivo con datos para POST
Ejemplo: -p datos.json -T "application/json"
Envia un body JSON en requests POST

-g Exporta resultados en formato TSV para graficar
Ejemplo: -g resultados.tsv
Compatible con GNUplot, Excel, Python pandas
(Fuente: Baeldung)

-w Salida en formato HTML tabular
Ejemplo: -w > resultado.html
Genera una tabla HTML con los resultados

-v Nivel de verbosidad (1-4)
Ejemplo: -v 3
3 muestra headers de respuesta, util para debugging

-q Silencia el progreso en pantalla
Ejemplo: -q
Ideal para scripts automatizados o logs limpios

===============================================================================
💡 EJEMPLOS PRACTICOS DE USO
===============================================================================

1000 peticiones, 50 concurrentes:
ab -n 1000 -c 50 http://tuservidor.local/

Prueba de 30 segundos con keep-alive:
ab -t 30 -c 20 -k http://tuservidor.local/

Con cabecera personalizada y timeout:
ab -n 500 -c 10 -H "X-Test: 1" -s 5 http://tuservidor.local/

Test contra API local con autenticacion:
ab -n 200 -c 20 -H "Authorization: Bearer token123" http://127.0.0.1:3000/api/users

Test POST con datos JSON:
ab -n 100 -p datos.json -T "application/json" http://127.0.0.1:3000/api/register

Exportar resultados para graficar:
ab -n 500 -c 20 -g resultados.tsv http://127.0.0.1:8000/

===============================================================================
🌐 SITIOS SEGUROS PARA PRACTICAR (100% LEGALES)
===============================================================================

Sitios disenados especificamente para testing:

http://example.com
http://example.org
http://example.net

Sitios estaticos oficiales para documentacion
Perfectos para: ab, curl, wget basicos

http://httpbin.org

API de pruebas HTTP muy completa

Ejemplos:
ab -n 100 -c 10 http://httpbin.org/get
ab -n 50 http://httpbin.org/status/200
ab -n 50 http://httpbin.org/delay/1
ab -n 50 http://httpbin.org/bytes/1024

https://httpstat.us

Testing de codigos de respuesta HTTP

Ejemplos:
ab -n 50 https://httpstat.us/200 (OK)
ab -n 50 https://httpstat.us/404 (Not Found)
ab -n 50 https://httpstat.us/500 (Server Error)

https://reqres.in

API REST fake para testing

Ejemplos:
ab -n 50 https://reqres.in/api/users?page=2
ab -n 50 https://reqres.in/api/users/2

===============================================================================
🏠 TESTING LOCAL (RECOMENDADO - MAXIMO CONTROL)
===============================================================================

Levantar un servidor HTTP con Python en 10 segundos:

Crear archivo de prueba:
echo "<h1>Test Server - by mrvcode</h1>" > index.html

Iniciar servidor en puerto 8000:
python3 -m http.server 8000

En otra terminal, ejecutar el test:
ab -n 500 -c 20 http://127.0.0.1:8000/index.html

Otras opciones locales:
ab -n 1000 -c 50 http://localhost:3000/
ab -n 200 -c 10 http://127.0.0.1:8080/api/health

===============================================================================
📊 INTERPRETANDO LOS RESULTADOS
===============================================================================

Ejemplo de output de ab:

Server Software: nginx/1.18.0
Server Hostname: 127.0.0.1
Server Port: 8000

Concurrency Level: 20
Time taken for tests: 2.456 seconds
Complete requests: 500
Failed requests: 0
Requests per second: 203.58 [#/sec] (mean) <-- METRICA PRINCIPAL
Time per request: 98.234 [ms] (mean)
Transfer rate: 245.67 [Kbytes/sec] received

Connection Times (ms)
min mean[+/-sd] median max
Connect: 0 5 2.1 5 15
Processing: 10 85 45.2 75 350
Total: 10 90 45.8 80 355

Percentage of requests served within time:

50% 80ms (La mitad de requests fueron <=80ms)
90% 145ms (90% fueron <=145ms)
99% 280ms (99% fueron <=280ms, ojo con outliers)

===============================================================================
⚠️ ADVERTENCIAS IMPORTANTES - LEE ESTO
===============================================================================

NUNCA HAGAS ESTO:

No ataques sitios que no te pertenezcan:
ab -n 1000000 https://sitio-ajeno.com <-- ILEGAL

No hagas DDoS:
ab -n 999999 -c 1000 https://cualquier-sitio.com <-- DELITO

No testes sin permiso escrito:
ab -n 1000 https://empresa.com <-- Podria ser ilegal

SIEMPRE HAZ ESTO:

Testea solo tus propios sistemas:
ab -n 500 http://127.0.0.1:8000 <-- Seguro y legal

Usa sitios disenados para testing:
ab -n 100 http://httpbin.org/get <-- Autorizado

Obtén permiso POR ESCRITO para sistemas de terceros:
Si necesitas testear un servidor de cliente/empresa

===============================================================================
🔍 EJEMPLOS AVANZADOS
===============================================================================

Test de API con autenticacion Bearer:

ab -n 200 -c 20
-H "Authorization: Bearer tu_token_aqui"
-H "Content-Type: application/json"
http://127.0.0.1:3000/api/users

Test POST con archivo JSON:

cat > test_data.json << EOF
{"username": "testuser", "email": "test@example.com"}
EOF

ab -n 100 -p test_data.json -T "application/json"
http://127.0.0.1:3000/api/register

Test prolongado con keep-alive (60 segundos):

ab -t 60 -c 30 -k http://127.0.0.1:8000/

Exportar y graficar con Python despues:

ab -n 1000 -c 50 -g resultados.tsv http://127.0.0.1:8000/

Luego en Python: pandas.read_csv('resultados.tsv', sep='\t')

===============================================================================
📚 RECURSOS ADICIONALES
===============================================================================

Documentacion oficial: man ab
Apache docs: https://httpd.apache.org/docs/2.4/programs/ab.html
Guia Baeldung: https://www.baeldung.com/linux/apache-bench
Referencia Linux: https://linux.die.net/man/1/ab

===============================================================================
💡 TIP FINAL
===============================================================================

Siempre empieza con tests pequeños (n=50, c=5) antes de subir la carga.
Monitorea tu propio sistema durante las pruebas para no saturarlo.
Los resultados varian segun red, CPU y configuracion del servidor.

Script creado por mrvcode
Uso exclusivo educativo y en entornos autorizados