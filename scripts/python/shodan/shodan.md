markdown
🔍 SHODAN TOOL - BÚSQUEDA DE VULNERABILIDADES Y EXPOSICIÓN DE SERVICIOS

===============================================================================

Nivel: 🟡 Intermedio
Categoría: OSINT / Cybersecurity / Vulnerability Assessment
Herramienta: Shodan API (Python)

===============================================================================

📋 DESCRIPCION

===============================================================================

Este script automatiza consultas a la API de Shodan para dos tareas principales:

1. **Búsqueda masiva (Search)** - Encontrar hosts que coincidan con una query
2. **Host Lookup** - Analizar una IP específica en busca de vulnerabilidades CVE

El script se autentica con tu API Key, realiza la consulta y presenta los 
resultados de forma estructurada, destacando especialmente los CVEs 
detectados en cada puerto abierto.

===============================================================================

🎯 ¿PARA QUE SIRVE?

===============================================================================

- **Auditoría de seguridad**: Verificar si tus sistemas expuestos tienen CVEs conocidos
- **OSINT ofensivo (autorizado)**: Reconocimiento de infraestructuras propias o con permiso
- **Gestión de vulnerabilidades**: Identificar rápidamente servicios vulnerables
- **Aprendizaje**: Entender cómo Shodan cataloga y expone información de dispositivos

===============================================================================

📦 REQUISITOS

===============================================================================

Instalar la librería de Shodan:

```bash
pip install shodan
Verificar instalación:

bash
python -c "import shodan; print(shodan.__version__)"
API Key requerida:

Regístrate en: https://account.shodan.io/register

Obtén tu API Key en: https://account.shodan.io/

La versión gratuita tiene limitaciones (explicadas abajo)

===============================================================================

🚀 USO DEL SCRIPT

===============================================================================

Sintaxis:

python shodan_tool.py

Estructura del proyecto:

scripts/python/shodan/
├── shodan_tool.py       # Script principal
└── shodan_utils.py      # Funciones de conexión a Shodan API
Ejemplo de ejecución completa:

=== HERRAMIENTA AUTOMATIZADA DE SHODAN ===
Introduce tu API KEY (no se verá al escribir): 

¿Qué acción deseas realizar?
1. Búsqueda masiva (Search)
2. Investigar IP específica (Host Lookup)

Selecciona una opción (1 o 2): 2
[?] Introduce la IP a investigar: 45.33.32.156
[*] Analizando la IP: 45.33.32.156...

[+] Análisis de 45.33.32.156:

--- Puerto: 22 (N/A) ---
      [✓] No se detectaron vulnerabilidades conocidas.

--- Puerto: 80 (Apache httpd) ---
      [!] VULNERABILIDADES DETECTADAS: CVE-2014-0117, CVE-2017-7679, 
      CVE-2017-9798, CVE-2015-3185, CVE-2025-58098, CVE-2015-3183...
===============================================================================

⚙️ FUNCIONAMIENTO INTERNO

===============================================================================

shodan_utils.py - Funciones clave:

Función		Parámetros	Retorno				Descripción

conectar_api()	api_key		objeto Shodan			Autenticación con la API

queryShodan()	api, query	dict {ip: {ports: []}}		Búsqueda masiva

ShodanLookup()	api, ip		list [{port, product, vulns}]	Análisis detallado de IP

Modo 1 - Search:

Usa api.search(query) de Shodan

Retorna IPs agrupadas con sus puertos abiertos

Límite: 100 resultados en versión gratuita

Modo 2 - Host Lookup:

Usa api.host(ip) de Shodan

Escanea todos los puertos de la IP

Extrae vulnerabilidades CVE asociadas a cada servicio

===============================================================================

⚠️ LIMITACIONES DE LA VERSIÓN GRATUITA (IMPORTANTE)

===============================================================================

Error 401 en búsqueda masiva (opción 1):

text
Error en búsqueda: 401 Unauthorized
¿Por qué ocurre?

La API gratuita de Shodan NO permite el método api.search()
sin un plan de pago (mínimo $49/mes para el plan "Developer").

¿Qué funciona en versión gratuita?

Funcionalidad			Gratis		Pago
api.host(IP) - Host Lookup	✅ Sí		✅ Sí
api.search(query) - Búsqueda	❌ No		✅ Sí
Límite de resultados		1 IP/consulta	Ilimitado
Consultas por mes		Ilimitadas	Ilimitadas

Solución:

Usa solo la opción 2 (Host Lookup) con cuenta gratuita

Para búsquedas masivas, actualiza a plan de pago o usa la web de Shodan manualmente

===============================================================================

🌐 IPs SEGURAS PARA PRACTICAR (100% LEGALES)

===============================================================================

IPs de prueba (propiedad de empresas que permiten escaneo):

IP			Propietario		Servicios típicos
45.33.32.156		Linode (test box)	HTTP, SSH, NTP
8.8.8.8			Google DNS		DNS (puerto 53)
1.1.1.1			Cloudflare DNS		DNS (puerto 53)
185.199.108.153		GitHub Pages		HTTPS (443)

Servicios de prueba de Shodan:

scanme.nmap.org (45.33.32.156) - Diseñado para pruebas de escaneo

test.shodan.io - Servidor oficial de pruebas de Shodan

⚠️ NUNCA escanees IPs sin autorización explícita por escrito.

===============================================================================

💡 EJEMPLOS PRÁCTICOS DE CONSULTAS

===============================================================================

Modo 2 - Host Lookup (funciona en versión gratuita):

# Analizar un servidor de pruebas
IP: 45.33.32.156

# Analizar tu propio servidor (si tienes uno expuesto)
IP: <tu_ip_publica>

# Analizar DNS de Google
IP: 8.8.8.8
Modo 1 - Search (SOLO con plan de pago):

# Búsqueda de servidores Apache en España
query = "apache country:ES"

# Búsqueda de puerto SSH abierto en red de Google
query = "port:22 org:Google"

# Búsqueda de cámaras con autenticación débil
query = "webcam login"

===============================================================================

📊 INTERPRETANDO LOS RESULTADOS

===============================================================================

Ejemplo de output exitoso:

text
--- Puerto: 80 (Apache httpd) ---
      [!] VULNERABILIDADES DETECTADAS: CVE-2014-0117, CVE-2017-7679...
¿Qué significa?

Puerto 80 abierto → Servicio web HTTP expuesto

Apache httpd → Servidor web Apache

Lista de CVEs → Vulnerabilidades conocidas según base de datos de Shodan

Acciones recomendadas:

Verificar cada CVE en https://nvd.nist.gov/

Actualizar el software vulnerable

Restringir acceso al puerto si no es necesario

===============================================================================

🔧 POSIBLES ERRORES Y SOLUCIONES

===============================================================================

Error				Causa				Solución
401 Unauthorized (búsqueda)	API gratuita sin permisos	Usa solo opción 2 o actualiza plan
API key inválida		Key incorrecta o revocada	Regenera key en Shodan dashboard
No se encontraron datos		IP no indexada por Shodan	Prueba otra IP o espera 24h
Connection timeout		Problemas de red		Verifica conexión a internet

===============================================================================

⚖️ CONSIDERACIONES ÉTICAS Y LEGALES - LEE ESTO

===============================================================================

🚨 ILEGAL Y PROHIBIDO:

text
❌ Escanear IPs sin autorización por escrito
❌ Usar resultados para ataques activos
❌ Automatizar consultas masivas contra la API gratuita (viola ToS)
❌ Compartir API Key con terceros
❌ Intentar explotar las vulnerabilidades encontradas

✅ LEGAL Y PERMITIDO:

text
✓ Escanear tus propias IPs o servidores
✓ Usar IPs de prueba documentadas (scanme.nmap.org)
✓ Realizar auditorías con permiso explícito de cliente
✓ Fines educativos en entorno controlado
✓ Reportar vulnerabilidades a programas de bug bounty
Shodan Terms of Service:

La versión gratuita es para uso personal/no comercial

Prohibido hacer scraping automatizado

Límite de requests: no especificado, pero abusar = baneo de IP

===============================================================================

📚 RECURSOS ADICIONALES

===============================================================================

Documentación oficial:

Shodan API docs: https://developer.shodan.io/api

Shodan Python library: https://github.com/achillean/shodan-python

Bases de datos de vulnerabilidades:

NVD (National Vulnerability Database): https://nvd.nist.gov/

CVE Details: https://www.cvedetails.com/

Exploit-DB: https://www.exploit-db.com/

Libros recomendados:

"OSINT Techniques" - Michael Bazzell

"The Shodan Bible" - John Matherly (creador de Shodan)

===============================================================================

💡 TIP FINAL

===============================================================================

Para versión gratuita:

Usa SOLO la opción 2 (Host Lookup) - funciona perfectamente

La opción 1 siempre dará error 401 sin plan de pago

Para práctica legal:

Usa scanme.nmap.org (45.33.32.156) para todas tus pruebas

Configura tu propio VPS y analízalo con Shodan

Mejora del script (propuesta):

# Añadir verificación de tipo de cuenta antes de búsqueda
if opcion == "1":
    print("[!] La búsqueda masiva requiere plan de pago de Shodan")
    print("    Usa la opción 2 (Host Lookup) con cuenta gratuita")
    return

Script creado para entornos educativos y auditorías autorizadas.
Uso ético y responsable siempre.
