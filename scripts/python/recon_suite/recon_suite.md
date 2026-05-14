Aquí se recoge como actúan todos los archivos en un resumen claro que esta también en GitHub:



Toolkit modular en Python para reconocimiento de redes y análisis de vulnerabilidades. Desarrollado como parte de una ruta de formación práctica en ciberseguridad, con cada módulo mapeado al framework MITRE ATT&CK.

> **Aviso legal:** Este toolkit está destinado a auditorías autorizadas, entornos de laboratorio personal y plataformas legales como Hack The Box o `scanme.nmap.org`. El uso no autorizado contra sistemas de terceros es ilegal bajo la LSSI española, la CFAA estadounidense y leyes equivalentes en otras jurisdicciones.

---

## Estructura del proyecto

```
cyber-toolbox/
└── recon_suite/
    ├── main.py               # Punto de entrada interactivo — ejecuta todos los módulos
    ├── PortScan.py           # Escáner SYN sigiloso + captura de banners
    ├── ShodanSearch.py       # OSINT pasivo mediante la API de Shodan
    ├── dns_recon.py          # Enumeración de subdominios vía DNS
    ├── CVESearch.py          # Búsqueda de CVEs mediante la API de VulDB
    ├── ServiceLookup.py      # Orquestador: combina todos los módulos por IP
    ├── subdomains.txt        # Diccionario para fuerza bruta DNS
    └── requirements.txt
```

Todos los archivos deben estar en el **mismo directorio**. Los módulos se importan entre sí por nombre.

---

## Mapeo MITRE ATT&CK

|Módulo|Táctica|Técnica|
|---|---|---|
|`dns_recon.py`|Reconocimiento|T1596 — Búsqueda en bases de datos técnicas abiertas|
|`ShodanSearch.py`|Reconocimiento|T1596.005 — Escaneo de bases de datos|
|`PortScan.py`|Reconocimiento|T1046 — Escaneo de servicios de red|
|`CVESearch.py`|Reconocimiento|T1592 — Recopilación de información del host objetivo|
|`ServiceLookup.py`|Reconocimiento|T1046 + T1592 (combinado)|

---

## Instalación

```bash
git clone https://github.com/<tu-usuario>/cyber-toolbox.git
cd cyber-toolbox/recon_suite
pip install -r requirements.txt
```

`requirements.txt`:

```
scapy
requests
urllib3
dnspython
shodan
```

> Scapy requiere **root/sudo** para enviar paquetes crudos (SYN scan). En Windows, instala [Npcap](https://npcap.com/) antes de ejecutar Scapy. En WSL2, `sudo python3` funciona sin configuración adicional.

---

## Inicio rápido

```bash
# Modo interactivo completo (recomendado)
sudo python3 main.py

# Módulos individuales
python3 dns_recon.py
sudo python3 PortScan.py
python3 ShodanSearch.py
python3 CVESearch.py
sudo python3 ServiceLookup.py
```

---

## Referencia de módulos

### main.py — Orquestador interactivo

Punto de entrada con menú para seleccionar qué módulos ejecutar.

```
[1] DNS Recon      — enumeración de subdominios
[2] Port Scan      — SYN scan sigiloso
[3] Shodan         — OSINT pasivo (requiere API key)
[4] CVE Search     — búsqueda de vulnerabilidades (requiere API key)
[A] Todas las herramientas
```

Acepta tanto una IP como un dominio. Si se introduce un dominio, se resuelve automáticamente a IP y se activa DNS Recon. Si solo se introduce una IP, DNS Recon se omite con un aviso.

Las API keys se solicitan mediante `getpass` (entrada oculta, nunca almacenada).

**Ejemplo de salida:**

```
  Objetivo analizado : 45.33.32.156 (scanme.nmap.org)
  Subdominios activos: 3 en 2 IP(s)
  Puertos abiertos   : 22, 80, 9929
  Servicios (Shodan) : 3, con CVEs conocidos: 1
```

---

### PortScan.py — Escáner de puertos sigiloso

Realiza un SYN half-open scan usando Scapy. Si no hay permisos de root o Scapy no está instalado, cambia automáticamente a TCP connect scan.

**Técnicas de evasión aplicadas:**

|Técnica|Efecto|
|---|---|
|SYN scan (half-open)|Sin conexión TCP completa — en muchos sistemas no queda registrado|
|Orden de puertos aleatorio|Evita la detección de patrones secuenciales por IDS|
|Window size aleatorio|Evita la firma de fingerprinting de Nmap|
|RST tras SYN-ACK|Cierre limpio antes de establecer la sesión|
|Pausa aleatoria entre puertos|Evasión de IDS basada en velocidad (0,1–0,5 s)|

**Funciones:**

|Función|Descripción|
|---|---|
|`SynScanNinja(host, ports)`|Escaneo sigiloso principal. Devuelve lista de puertos abiertos.|
|`TCPConnectScan(host, ports)`|Fallback sin root. Más detectable.|
|`bannerGrab(ip, port)`|Lee los primeros 1024 bytes de servicios no web.|
|`HTTPHeaderGrab(ip, port)`|Petición HTTP HEAD con User-Agent de Chrome.|

**Uso independiente:**

```bash
sudo python3 PortScan.py
# Introduce IP o Dominio: scanme.nmap.org
```

**Ejemplo de salida:**

```
  PUERTO   TIPO     INFORMACION
  22       TCP      SSH-2.0-OpenSSH_9.2p1 Debian-2+deb12u3
  80       HTTP     Servidor: Apache/2.4.62 (Debian)
```

**SYN scan frente a alternativas:**

|Herramienta|Sigilo|Notas|
|---|---|---|
|Este script (Scapy)|Alto|Cabeceras de paquetes totalmente personalizables|
|`nmap -sS`|Alto|Mismo método, más rápido, firma conocida|
|`nmap -sT` / `-A`|Bajo|Conexión completa, muy ruidoso en logs|
|`nc` (Netcat)|Bajo|Solo conexiones completas|

> Ventaja frente a Nmap: cuando un firewall reconoce la firma de Nmap, Scapy permite cambiar el window size, el orden de los campos, añadir padding — opciones que Nmap no expone.

**Opcional: fragmentación IP (comentado por defecto)**

```python
# Descomentar solo si el escaneo normal está siendo filtrado:
from scapy.all import fragment
pkt_fragmentado = fragment(IP(dst=host) / TCP(dport=port, flags="S"), fragsize=16)
for frag in pkt_fragmentado:
    send(frag, verbose=0)
```

La fragmentación puede evadir IDS básicos, pero los firewalls modernos pueden descartar paquetes fragmentados, generando falsos negativos.

---

### ShodanSearch.py — OSINT pasivo

Consulta la base de datos de Shodan sin generar tráfico hacia el objetivo. Ejecutar siempre antes del escaneo activo.

**Compatibilidad con el plan gratuito de Shodan:**

|Función|Plan gratuito|Notas|
|---|---|---|
|`ShodanLookup(api, ip)`|Siempre|Consulta de host por IP|
|`queryShodan(api, query)`|Hasta 100 resultados|Solo filtros básicos|
|Filtros `org:`, `net:`|Limitados|Generalmente requieren plan de pago|

**Consultas seguras en el plan gratuito:**

```
port:22 country:ES
product:Apache version:2.4
hostname:example.com
```

**Funciones:**

|Función|Descripción|
|---|---|
|`conectar_api(api_key)`|Conecta y valida la clave mediante `api.info()` antes de continuar|
|`ShodanLookup(api, ip)`|Devuelve lista de dicts: puerto, producto, versión, CVEs|
|`queryShodan(api, query)`|Devuelve dict `{ip: {ports, hostnames}}`|

**API key:** Regístrate en [account.shodan.io](https://account.shodan.io/) — plan gratuito disponible.

**Uso independiente:**

```bash
python3 ShodanSearch.py
# Opción 1: Host Lookup (recomendado para el plan gratuito)
# Opción 2: Búsqueda por filtro
```

**Ejemplo de salida:**

```
  PUERTO   PRODUCTO           VERSION      CVEs
  22       OpenSSH            9.2p1        Ninguno
  80       Apache httpd       2.4.62       CVE-2014-0117, CVE-2017-7679
```

---

### dns_recon.py — Enumeración de subdominios

Enumera subdominios usando un diccionario. Para cada subdominio resuelto, realiza Reverse DNS para descubrir nombres adicionales asociados a la misma IP.

**Funciones:**

|Función|Descripción|
|---|---|
|`DNSSearch(domain, use_nums, dict_path)`|Bucle principal — carga el diccionario y llama a DNSRequest por cada palabra|
|`DNSRequest(subdomain, domain, hosts)`|Resuelve un subdominio y combina los resultados en el dict compartido|
|`ReverseDNS(ip)`|Consulta PTR — descubre nombres adicionales para una IP|

**Parámetro `use_nums`:**

- `True` — para cada palabra, prueba también `word0`, `word1`...`word9` (encuentra `ns1`, `vpn2`, etc.)
- `False` — solo las palabras exactas del diccionario, más rápido

**Archivo necesario:** `subdomains.txt` debe estar en el mismo directorio. Si no se encuentra, usa una lista interna mínima de respaldo.

**Uso independiente:**

```bash
python3 dns_recon.py
# Introduce el dominio objetivo: example.com
# Probar variantes numericas? [s/N]:
```

**Ejemplo de salida:**

```
  IP               SUBDOMINIOS ENCONTRADOS
  142.250.185.46   www, mail, smtp
  8.8.8.8          dns, ns, ns1

  Total: 2 IP(s) unicas, 5 subdominio(s)
```

**Interpretación de resultados:**

|Patrón de subdominio|Servicio probable|Puertos a investigar|
|---|---|---|
|`mail`, `smtp`|Servidor de correo|25, 465, 587|
|`ns`, `dns`|Servidor DNS|53|
|`vpn`|Endpoint VPN|1194, 1723, 4500|
|`admin`, `panel`|Panel de administración|9090, 8443, 10000|

**Dominios seguros para practicar:**

```
scanme.nmap.org     Autorizado expresamente por Nmap
google.com          Infraestructura amplia, buena para demostración
github.com          Subdominios reales: api.github.com, pages.github.com
```

---

### CVESearch.py — Búsqueda de vulnerabilidades

Consulta la API de VulDB para obtener CVEs asociados a un producto y versión concretos. Se usa como última fase del reconocimiento: una vez que `PortScan` o `Shodan` identifica "OpenSSH 7.6p1", este módulo comprueba si existen vulnerabilidades conocidas.

**Función:**

|Función|Descripción|
|---|---|
|`VuldbLookup(product, version, api_key)`|POST a VulDB. Devuelve lista de strings con CVE IDs.|

**Estructura de la respuesta de la API de VulDB:**

```json
{
  "result": [
    {
      "source": {
        "cve": { "id": "CVE-2023-1234" }
      }
    }
  ]
}
```

El CVE ID se extrae de `entry["source"]["cve"]["id"]`.

**Consejo de uso:** Utiliza el nombre exacto del producto tal como lo devuelve el banner grabbing o Shodan:

- `"OpenSSH"` — correcto
- `"ssh"` — no coincidirá

**API key:** Regístrate en [vuldb.com](https://vuldb.com/). El plan gratuito tiene un límite diario de peticiones. El módulo deduplica las consultas automáticamente.

**Uso independiente:**

```bash
python3 CVESearch.py
# VulDB API Key: (oculta)
# Nombre del producto: OpenSSH
# Version: 7.6p1
```

**Ejemplo de salida:**

```
  OpenSSH 7.6p1             -> 1 CVE(s): CVE-2018-15473
```

---

### ServiceLookup.py — Orquestador de identificación de servicios

Combina PortScan, Shodan y CVESearch para construir un mapa completo de servicios para una sola IP. Utiliza una estrategia de tres fases para minimizar el tráfico hacia el objetivo.

**Lógica de las tres fases:**

```
Fase 1 — Inferencia por subdominios (sin tráfico adicional)
  "mail.example.com" -> comprueba directamente los puertos 25, 465, 587

Fase 2 — Shodan (pasivo, datos históricos)
  Solo si la Fase 1 no dio resultados y hay API key disponible
  Enriquece con banner local si Shodan no identificó el producto

Fase 3 — SYN scan completo (activo, último recurso)
  Solo si las Fases 1 y 2 están vacías
  Escanea todos los DEFAULT_PORTS con SynScanNinja()
```

**Funciones:**

|Función|Descripción|
|---|---|
|`serviceID(ip, subs, shodan_api)`|Función principal — ejecuta las tres fases, devuelve lista de servicios|
|`enrich_with_cves(records, vuldb_key)`|Añade datos de CVE a cada registro de servicio|
|`print_service_table(ip, records)`|Muestra la tabla de resultados con colores|

**Uso independiente:**

```bash
sudo python3 ServiceLookup.py
# Introduce IP o Dominio objetivo: scanme.nmap.org
# Shodan API Key: (oculta, Enter para omitir)
# VulDB API Key: (oculta, Enter para omitir)
```

**Ejemplo de salida:**

```
  PUERTO   PRODUCTO           VERSION      RIESGO     CVEs
  22       OpenSSH            9.2p1        Alto       CVE-2023-38408
  80       Apache             2.4.62       Medio      CVE-2021-41773
  3306     mysql              8.0.33       Alto       Ninguno
```

Colores de severidad (terminal ANSI):

- Rojo — servicio crítico (SSH, FTP, MySQL, Telnet, RDP, SMB)
- Amarillo — servicio identificado pero no crítico
- Sin color — desconocido / sin banner

---

## Flujo de trabajo recomendado

```
1. ShodanSearch.py   ->  Pasivo: qué está expuesto públicamente
2. dns_recon.py      ->  Mapa de subdominios, inferencia de servicios
3. PortScan.py       ->  Activo: confirmar puertos abiertos, capturar banners
4. CVESearch.py      ->  Relacionar versiones con CVEs conocidos
5. main.py           ->  Todo lo anterior en una sola ejecución
```

Reconocimiento pasivo primero, escaneo activo al final y solo con autorización.

---

## Entornos legales para pruebas

```bash
# Tu propia máquina
sudo python3 PortScan.py  ->  127.0.0.1

# Autorizado por Nmap
sudo python3 PortScan.py  ->  scanme.nmap.org

# Objetivo Docker en local
docker run -d -p 22:22 -p 80:80 vulnerables/web-dvwa

# Servidor HTTP local para pruebas de banner
sudo python3 -m http.server 80
```

---

## Referencias

- MITRE ATT&CK: https://attack.mitre.org/
- Documentación de Scapy: https://scapy.readthedocs.io/
- Filtros de Shodan: https://www.shodan.io/search/filters
- API de VulDB: https://vuldb.com/?kb.api
- NVD (sin API key): https://nvd.nist.gov/vuln/search
- Diccionarios SecLists: https://github.com/danielmiessler/SecLists
- Objetivo autorizado de Nmap: https://scanme.nmap.org/