🔍 DNS EXPLORATION - ENUMERACIÓN DE SUBDOMINIOS

===============================================================================

Nivel: 🟡 Intermedio
Categoría: OSINT / Reconocimiento / DNS
Herramienta: Python (dnspython, socket)

===============================================================================

📋 DESCRIPCIÓN

===============================================================================

Este script automatiza la enumeración de subdominios de una organización
mediante consultas DNS directas y resolución inversa (Reverse DNS).

**¿Qué hace?**

1. Carga una lista de subdominios comunes (www, mail, ftp, etc.)
2. Para cada subdominio, consulta su resolución DNS
3. Obtiene la(s) IP(s) asociadas
4. Realiza Reverse DNS para encontrar más subdominios asociados a esa IP
5. Agrupa resultados: IP → [lista de subdominios]

**Lógica clave:** Si una IP tiene múltiples subdominios (ej: www y mail apuntan al mismo servidor), los fusiona automáticamente.

===============================================================================

🎯 ¿PARA QUE SIRVE?

===============================================================================

- **Descubrimiento de superficie de ataque**: Encontrar todos los servidores expuestos de una organización
- **Identificación de servicios**: mail.* → servidor de correo, vpn.* → VPN, ns.* → DNS
- **Mapeo de infraestructura**: Relacionar IPs con sus propósitos
- **Fase de reconocimiento**: Paso inicial en auditorías autorizadas

===============================================================================

📦 REQUISITOS

===============================================================================

Instalar la librería dnspython:

pip install dnspython

crear subdomains.txt con lista de subdominios (uno por línea)


🚀 USO DEL SCRIPT

===============================================================================

Estructura del proyecto:

scripts/python/dns/
├── dns_recon.py         # Script principal
└── subdomains.txt     # Lista de subdominios a probar


===============================================================================

📊 EXPLICACIÓN DEL FLUJO (PASO A PASO)

===============================================================================


cuando lo lanzas con:

python dns_recon.py


Paso 1: Carga del diccionario

El script abre el archivo externo y limpia los saltos de línea para crear una lista de palabras clave.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
with open("subdomains.txt", "r") as f:
    dictionary = f.read().splitlines()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Paso 2: Bucle principal y variantes numéricas

Se recorre el diccionario y, si se activa la opción nums, se generan intentos adicionales añadiendo números al final de la palabra.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for word in dictionary:
    DNSRequest(word, domain, hosts_finales)
    if use_nums:
        for i in range(0, 10):
            DNSRequest(word + str(i), domain, hosts_finales)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Paso 3: Normalización y consulta DNS directa

Se asegura que el dominio tenga el formato correcto y se utiliza el resolver para obtener la IPv4 (Registro A).


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
hostname = sub + domain
result = dns.resolver.resolve(hostname, 'A')
# Retorna IP: 142.250.191.132
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Paso 4: Reverse DNS (Inverso)

Toma la IP encontrada y le pregunta al sistema por todos los nombres de dominio que apuntan a ella.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ReverseDNS(ip):
    result = socket.gethostbyaddr(ip)
    return [result[0]] + list(result[1])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Paso 5: Extracción y limpieza de subdominios

Filtra los resultados del Reverse DNS para quedarse solo con la parte del subdominio que pertenece al objetivo.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if h.endswith(domain):
    s = h.replace(domain, "").rstrip(".")
    # De 'mail.google.com' -> quita '.google.com' -> queda 'mail'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Paso 6: Almacenamiento y fusión

Guarda los resultados en el diccionario. Si la IP ya existía, combina los subdominios nuevos con los viejos eliminando duplicados.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if ip in hosts_acumulados:
    hosts_acumulados[ip] = list(set(hosts_acumulados[ip] + subs_actuales))
else:
    hosts_acumulados[ip] = list(set(subs_actuales))
    
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



===============================================================================

💡 EJEMPLOS PRÁCTICOS DE USO (APLICADOS AL SCRIPT)

===============================================================================

Ejemplo 1: Escanear tu propio dominio

Si quieres auditar tu propia infraestructura, solo tienes que cambiar la variable de entrada. El script se encargará de normalizar los puntos.



~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# No importa si olvidas el punto inicial, el script lo gestiona
domain = "miempresa.com" 
# Ejecuta la búsqueda con variantes numéricas activadas
hosts = DNSSearch(domain, True)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Ejemplo 2: Escaneo rápido (Solo subdominios base)

Si tienes prisa y solo quieres probar las palabras exactas del diccionario (sin probar vpn1, vpn2, etc.), desactiva el parámetro use_nums.



~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# use_nums=False -> Ahorra tiempo al no probar variantes del 0 al 9
hosts = DNSSearch("objetivo.com", False)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Ejemplo 3: Exportar resultados a formato JSON

Ideal para guardar los datos en un archivo que luego pueda leer otra herramienta o para tener un reporte limpio y estructurado.



~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import json

resultados = DNSSearch("google.com", True)
# Convierte el diccionario de IPs a un formato JSON legible
print(json.dumps(resultados, indent=4))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Ejemplo 4: Identificar objetivos específicos (Filtro)

Una vez terminada la búsqueda, puedes filtrar el diccionario para localizar servicios críticos, como servidores de correo o paneles de administración.



~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Buscar solo IPs que tengan servicios relacionados con 'admin' o 'mail'
for ip, subdomains in resultados.items():
    if any(keyword in s for s in subdomains for keyword in ['mail', 'admin']):
        print(f"[!] Objetivo crítico detectado: {ip} gestiona {subdomains}")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



===============================================================================

🌐 SITIOS SEGUROS PARA PRACTICAR

===============================================================================

Dominio					Propósito						Notas

google.com				Demostración				Público, gran infraestructura
example.com				Documentación				Solo DNS básico, pocos subdominios
github.com				Práctica							Subdominios como api.github.com
scanme.nmap.org		Escaneo autorizado		Propiedad de Nmap.org

⚠️ ADVERTENCIA: No uses esta técnica contra dominios sin autorización por escrito. La enumeración de subdominios es considerada reconocimiento proactivo y puede violar términos de servicio.


🔍 INTERPRETANDO LOS RESULTADOS

===============================================================================

Salida típica:

8.8.8.8 ['dns', 'ns', 'ns1']

¿Qué significa?

• La IP 8.8.8.8 tiene tres subdominios asociados

• dns.google.com, ns.google.com, ns1.google.com apuntan al mismo servidor

• Conclusión: Este servidor maneja DNS, probablemente hay más servicios relacionados


Otro ejemplo:


142.250.191.101 ['mail', 'smtp']

• La IP 142.250.191.101 es servidor de correo

• Conclusión: Revisar puertos 25 (SMTP), 465 (SMTPS), 587 (SMTP submission)


===============================================================================

🐛 POSIBLES ERRORES Y SOLUCIONES

===============================================================================

Error													Causa										Solución
No module named 'dns'							dnspython no instalado				pip install dnspython
FileNotFoundError: subdomains.txt			Archivo no existe						Crear archivo con lista de subdominios
socket.herror											Reverse DNS no configurado		Normal, muchos servidores no tienen PTR
Timeout												DNS lento o bloqueado				Probar con dns.resolver.resolve(hostname, lifetime=5)


===============================================================================

⚖️ CONSIDERACIONES ÉTICAS

===============================================================================

✅ PERMITIDO (con autorización):

• Escanear tus propios dominios

• Auditorías con permiso por escrito

• Programas de bug bounty que permitan enumeración DNS

• Fines educativos en entornos controlados

❌ PROHIBIDO:

• Enumerar subdominios de terceros sin permiso

• Usar los resultados para ataques activos

• Violar límites de rate (consulta masiva)

• Eludir protecciones anti-DNS-fuzzing

Nota legal:
 La enumeración DNS es considerada reconocimiento pasivo en muchos países, pero siempre consulta las leyes locales y los términos de servicio.
 
=============================================================================== 
 
 📚 RECURSOS ADICIONALES

===============================================================================

• RFC 1035: Especificación DNS original

• dnspython docs: https://www.dnspython.org/

• Herramientas alternativas:

- dnsrecon (Kali Linux)

- sublist3r

- amass (OWASP)

• Listas de subdominios:

- SecLists (GitHub)

- commonspeak2

- Diccionarios de miles o millones de palabras (como el famoso subdomains-top1million de SecLists)
===============================================================================

💡 TIP FINAL

===============================================================================


Rendimiento: Un diccionario de 1000 subdominios tomará ~2-5 minutos dependiendo de la latencia DNS. Usa time.sleep() para no saturar el resolver.

Script creado con fines educativos. Úsalo solo en sistemas autorizados
