# 🔍 PORT SCANNER - ESCANEO DE PUERTOS CON SCAPY

===============================================================================
Nivel: 🟡 Intermedio
Categoría: Reconocimiento Activo / Evasión de IDS
Herramienta: Python 3 (Scapy, socket, requests)


===============================================================================

## 📋 DESCRIPCIÓN

===============================================================================

Este script es una herramienta de reconocimiento avanzado que implementa técnicas de evasión para identificar servicios en un objetivo. A diferencia de los escaneos tradicionales, este script busca minimizar la firma digital mediante la manipulación de cabeceras TCP y la fragmentación opcional.

### Funciones Principales:
1.  **SynScan Ninja (Half-open):** Escaneo de puertos sin completar el Three-Way Handshake, utilizando un `Window Size` aleatorio para evadir firmas de Nmap.
2.  **Disfraz de User-Agent:** Captura de cabeceras HTTP simulando ser un navegador Chrome legítimo en Windows.
3.  **Lógica de Decisión Inteligente:** Separa el análisis entre puertos Web (sigilo por aplicación) y servicios de red (Banner Grabbing).
4.  **Resolución DNS Automática:** Soporta tanto IPs como nombres de dominio (ej. google.com).



===============================================================================

## 🎯 ¿PARA QUÉ SIRVE?

===============================================================================

| Técnica | Información obtenida | Nivel de Sigilo |
| :--- | :--- | :--- |
| **SynScan Ninja** | Puertos abiertos y cierre con RST | **Alto** (Sin conexión completa) |
| **HTTP Disfrazado** | Versión de servidor (Apache/Nginx) | **Medio** (Parece tráfico humano) |
| **Banner Grab** | Versión de SSH, FTP, Telnet | **Bajo** (Requiere conexión completa) |

**Caso de uso:** Identificar qué puertos están abiertos en un servidor y qué tecnología corre detrás sin disparar alarmas inmediatas en sistemas de detección de intrusos (IDS).

**Caso práctico:** Si encuentras vsftpd 3.0.3, puedes buscar vulnerabilidades conocidas como CVE-2015-1419



===============================================================================

## 📦 REQUISITOS E INSTALACIÓN

===============================================================================

Es necesario contar con Python 3 y privilegios de administrador para la manipulación de paquetes.

```bash
# Actualizar e instalar dependencias
sudo pip3 install scapy requests urllib3

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

notas:

Scapy hace lo mismo que nmap, nc o metasploit. Pero Scapy es más lento para escanear miles de puertos que Nmap por ejemplo.
Por ejemplo con nmap -sS seria igual de silencioso que scapy. Pero si lanzaras nmap -sT o nmap -A o -T5 seria muy ruidoso y en los log del servidor aparecería.
nc(Netcat), solo hace conexiones completas, no es sigiloso.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Importante

Scapy por una razón: Evasión.
Si un Firewall bloquea a Nmap porque reconoce su "huella digital" (la forma en que Nmap ordena los paquetes), tú puedes usar este script de Python, cambiar el orden de los datos, añadir relleno (padding) o modificar el tamaño de la ventana TCP para engañar al Firewall.

Verificación:

python3 -c "import scapy, requests; print('✅ Librerías listas')"

Nota: Scapy requiere sudo para enviar paquetes crudos (Raw Sockets).



===============================================================================

⚙️ SCRIPT

===============================================================================


estructura del proyecto:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
scripts/python/scanner/
├── portscan.py          # Script se lanza con sudo
└── portscan.md
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==========================================================================

EJEMPLO DE RESULTADO REAL

==========================================================================


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ sudo python3 portscan.py
Introduce IP o Dominio: scanme.nmap.org
[*] Objetivo resuelto: 45.33.32.156
[*] Iniciando escaneo ninja en 45.33.32.156...

[+] Puertos detectados: [22, 80]

--- Análisis del Puerto 22 ---
    [BANNER] SSH-2.0-OpenSSH_9.2p1 Debian-2+deb12u3...

--- Análisis del Puerto 80 ---
    [WEB] Server: Apache/2.4.62 (Debian)

[*] Escaneo finalizado.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Interpretación:

Puerto 22 (SSH) → OpenSSH 6.6.1p1 (posibles CVEs)

Puerto 80 (HTTP) → Apache 2.4.7 (vulnerabilidades conocidas)



===============================================================================

⚙️ EXPLICACIÓN DE LA TÉCNICA NINJA

===============================================================================

1. Evasión de Firmas (Window Size)
Nmap tiene una firma TCP muy conocida por los firewalls. Este script genera un valor de window aleatorio para cada paquete, haciendo que el tráfico parezca provenir de diferentes aplicaciones legítimas y no de un escáner automático.

2. El Paquete de Reseteo (RST)
En el escaneo SYN, si recibimos una respuesta positiva, enviamos inmediatamente un paquete con flag R (Reset). Esto le dice al servidor: "Olvida la conexión, fue un error". Esto evita que el socket se quede en estado "Listening" y reduce la probabilidad de que aparezca en los logs de conexiones establecidas.

3. Fragmentación (Opcional)
En el código se incluye comentada la función fragment(). Esta técnica divide los paquetes IP en trozos tan pequeños que algunos IDS/IPS básicos no son capaces de reensamblarlos para analizarlos, permitiendo que la "pregunta" pase desapercibida.




===============================================================================

⚙️ EXPLICACIÓN DE LA SINTAXIS DE SCAPY

===============================================================================

Componente                 Código                                         Explicación

Capa IP                         IP(dst=host)                                Define destino. El resto (src, ttl) se auto-completan
Capa TCP                      TCP(dport=ports, flags="S")         flags="S" = SYN, dport acepta lista
Envío/Recepción            sr(packet, timeout, verbose)        Envía y espera respuesta, empareja automáticamente
Respuesta                     r[TCP].flags == "SA"                   SYN-ACK = puerto abierto
Destino                         s[TCP].dport                               Puerto que enviamos (debe coincidir con respuesta)


===============================================================================

🏠 ENTORNO DE PRUEBAS LEGAL (IMPORTANTE)

===============================================================================

NUNCA escanees IPs sin autorización. Usa estos entornos seguros:

Opción 1: Máquina virtual local (RECOMENDADA)


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Levantar servicios de prueba en tu propia máquina
sudo python -m http.server 80          # HTTP en puerto 80
sudo nc -lvp 21 -e /bin/bash           # Fake FTP (solo prueba)
# O mejor: usar Metasploitable 2 (VM descargable)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Opción 2: Scanme.nmap.org


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Única IP pública autorizada para escaneo
sudo python3 portscan.py
# scanme.nmap.org
# Puertos típicos abiertos: 22, 80, 31337
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Opción 3: Servidor local con Docker


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Levantar servicios vulnerables controlados
docker run -d -p 21:21 -p 80:80 vulnerables/web-dvwa
docker run -d -p 22:22 rastasheep/ubuntu-sshd:14.04
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Opción 4: Tu propio router (con permiso si eres el dueño)

sudo python portscan.py 192.168.1.1



===============================================================================

⚠️ FLAGS TCP - REFERENCIA RÁPIDA

===============================================================================


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Flag      Nombre       Significado                             En escaneo

S          SYN             Iniciar conexión                    Lo enviamos nosotros
A          ACK             Reconocimiento                      Lo envía el servidor
SA        SYN-ACK          Servidor acepta conexión            Puerto ABIERTO
R          RST             Reiniciar conexión                  Puerto CERRADO
F          FIN             Finalizar conexión                  Alternativa sigilosa
P          PUSH	           Datos urgentes                      Raramente usado
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Flags típicas en respuestas:

SA (SYN-ACK) → Puerto abierto

RA (RST-ACK) → Puerto cerrado

Sin respuesta → Filtrado por firewall



===============================================================================

⚖️ CONSIDERACIONES LEGALES Y ÉTICAS

===============================================================================

✅ LEGAL Y PERMITIDO:

Escanear tus propios servidores o red doméstica

Escanear scanme.nmap.org (autorizado explícitamente)

Auditorías con contrato firmado

Pruebas en laboratorio local (VMs, Docker)

❌ ILEGAL Y PROHIBIDO:

Escanear IPs de terceros sin autorización por escrito

Usar resultados para ataques activos

Escaneos masivos (pueden considerarse DDoS)

Violar términos de servicio de proveedores cloud

Leyes aplicables:

España: Ley de Servicios de la Sociedad de la Información (LSSI)

USA: Computer Fraud and Abuse Act (CFAA)

UK: Computer Misuse Act

"El simple escaneo de puertos puede ser considerado ilegal en algunos países sin autorización previa."



===============================================================================

📚 RECURSOS ADICIONALES

===============================================================================

Documentación Scapy: https://scapy.readthedocs.io/

Nmap reference: https://nmap.org/book/man-port-scanning-techniques.html

Práctica legal: https://scanme.nmap.org/

CVEs vsftpd 3.0.3: https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=vsftpd

Libro: "Python for Cybersecurity" (Wiley)



===============================================================================

💡 TIP FINAL

===============================================================================

La diferencia entre passive y active recon:

Tipo             Herramientas                   Detectable        Info obtenida

Pasivo          Shodan, DNS                     ❌ NO             Limitada, histórica

Activo          SYN scan, banner grab           ✅ Sí             Precisa, actual


Siempre empieza con passive recon (Shodan, DNS) antes de pasar a escaneo activo. El escaneo activo debe ser la última opción en una auditoría autorizada.


Comando útil para pruebas locales rápidas:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Crear servidor HTTP de prueba
python3 -m http.server 8000

# Y en otra terminal
sudo python portscan.py 127.0.0.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Script creado con fines educativos. Úsalo SOLO en sistemas con autorización explícita.
