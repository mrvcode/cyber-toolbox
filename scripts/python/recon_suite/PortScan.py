"""
PortScan.py - Escaneo sigiloso de puertos
Puede ejecutarse de forma independiente o importarse desde otros módulos.
"""

import sys
import socket
import random
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Puertos comunes a auditar
DEFAULT_PORTS = [
    20, 21, 22, 23, 25, 53, 69, 80, 110, 143,
    161, 162, 389, 443, 445, 636, 3306, 8080, 8443
]

WEB_PORTS = [80, 443, 8000, 8080, 8443, 8888, 3000, 5000, 9000, 10000]

# User-Agent de navegador real para no levantar sospechas
BROWSER_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'close',
}


def SynScanNinja(host, ports=None):
    """
    Escaneo SYN sigiloso usando Scapy.
    - Window size aleatorio para evitar fingerprinting.
    - Orden de puertos aleatorio para evitar detección por patrones secuenciales.
    - RST tras SYN-ACK para no dejar conexiones abiertas (no logueable en muchos sistemas).
    - Pausa aleatoria entre puertos para evadir IDS por velocidad.
    Requiere privilegios root/admin.
    """
    try:
        from scapy.all import IP, TCP, sr1, send, conf
        conf.verb = 0  # Silenciar Scapy completamente
    except ImportError:
        print("[!] Scapy no disponible. Usando TCP Connect como fallback.")
        return TCPConnectScan(host, ports)

    if ports is None:
        ports = DEFAULT_PORTS

    open_ports = []
    # Orden aleatorio: evita detección por patrón de escaneo secuencial
    port_order = ports.copy()
    random.shuffle(port_order)

    for port in port_order:
        try:
            random_window = random.randint(1024, 65535)
            pkt = IP(dst=host) / TCP(dport=port, flags="S", window=random_window)
            ans = sr1(pkt, timeout=1.2, verbose=0)

            if ans and ans.haslayer(TCP):
                if ans[TCP].flags == 0x12:  # SYN-ACK → puerto abierto
                    open_ports.append(port)
                    # RST limpio: cerramos sin establecer conexión completa
                    rst = IP(dst=host) / TCP(dport=port, flags="R")
                    send(rst, verbose=0)

            # Pausa aleatoria entre puertos (evasión IDS por velocidad)
            time.sleep(random.uniform(0.1, 0.5))

        except Exception:
            pass  # Silencioso: errores de red no interrumpen el escaneo

    return sorted(open_ports)


def TCPConnectScan(host, ports=None):
    """
    Fallback: TCP connect scan estándar.
    No requiere root, pero es más detectable.
    """
    if ports is None:
        ports = DEFAULT_PORTS

    open_ports = []
    port_order = ports.copy()
    random.shuffle(port_order)

    for port in port_order:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            result = s.connect_ex((host, port))
            s.close()
            if result == 0:
                open_ports.append(port)
            time.sleep(random.uniform(0.05, 0.2))
        except Exception:
            pass

    return sorted(open_ports)


def bannerGrab(ip, port):
    """
    Captura el banner de servicios no-web (SSH, FTP, SMTP...).
    Devuelve string con el banner o None si no hay respuesta.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((ip, port))
        banner = s.recv(1024)
        s.close()
        return banner.decode("utf-8", errors='ignore').strip()
    except Exception:
        return None


def HTTPHeaderGrab(ip, port):
    """
    Solicita cabeceras HTTP(S) haciéndose pasar por un navegador real.
    Devuelve dict con las cabeceras o {} si falla.
    """
    try:
        protocol = "https" if port in [443, 8443] else "http"
        url = f"{protocol}://{ip}:{port}"
        response = requests.head(
            url,
            headers=BROWSER_HEADERS,
            verify=False,
            timeout=5,
            allow_redirects=True
        )
        return dict(response.headers)
    except Exception:
        return {}


def _print_scan_results(target, found_ports):
    """Muestra los resultados del escaneo de forma legible."""
    if not found_ports:
        print("\n[!] No se encontraron puertos abiertos.")
        return

    print(f"\n[+] {len(found_ports)} puerto(s) abierto(s) en {target}\n")
    print(f"  {'PUERTO':<8} {'TIPO':<8} {'INFORMACIÓN'}")
    print(f"  {'-'*7:<8} {'-'*7:<8} {'-'*40}")

    for p in found_ports:
        if p in WEB_PORTS:
            headers = HTTPHeaderGrab(target, p)
            server = headers.get('Server', 'Desconocido') if headers else 'Sin respuesta'
            tipo = "HTTPS" if p in [443, 8443] else "HTTP"
            print(f"  {p:<8} {tipo:<8} Servidor: {server}")
        else:
            banner = bannerGrab(target, p)
            info = (banner[:55] + '...') if banner and len(banner) > 55 else (banner or "Sin banner")
            print(f"  {p:<8} {'TCP':<8} {info}")


# ─────────────────────────────────────────────
# Ejecución independiente
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("       ESCÁNER DE PUERTOS SIGILOSO")
    print("=" * 50)

    target_input = input("\nIntroduce IP o Dominio (ej: scanme.nmap.org): ").strip()

    if not target_input:
        print("[!] No introdujiste ningún objetivo.")
        sys.exit(1)

    try:
        target = socket.gethostbyname(target_input)
        if target != target_input:
            print(f"[*] Dominio resuelto → {target}")
    except socket.gaierror:
        print("[!] Error: No se pudo resolver el dominio.")
        sys.exit(1)

    print()
    found_ports = SynScanNinja(target)
    _print_scan_results(target, found_ports)

