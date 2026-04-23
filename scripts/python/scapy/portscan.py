import sys
from scapy.all import *
import requests
import socket
import urllib3
import random

# Silenciar avisos de SSL para evitar ruido en la terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Puertos comunes a auditar
ports = [20, 21, 22, 23, 25, 53, 69, 80, 110, 143, 161, 162, 389, 443, 445, 636, 8080, 8443]

def SynScanNinja(host):
    """Fase 1: Descubrimiento sigiloso con Window Size aleatorio."""
    open_ports = []
    print(f"[*] Iniciando escaneo ninja en {host}...")

    for port in ports:
        random_window = random.randint(1024, 4096)
        ip_pkt = IP(dst=host)
        tcp_pkt = TCP(dport=port, flags="S", window=random_window)
        
        # Opcional: frags = fragment(ip_pkt/tcp_pkt, fragsize=16)
        ans = sr1(ip_pkt/tcp_pkt, timeout=2, verbose=0)
        
        if ans and ans.haslayer(TCP):
            if ans[TCP].flags == "SA": # SYN-ACK detectado
                open_ports.append(port)
                # Enviamos RST para no dejar la conexión abierta
                send(IP(dst=host)/TCP(dport=port, flags="R"), verbose=0)
    return open_ports

def bannerGrab(ip, port):
    """Captura de banner para servicios no-web (SSH, FTP)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        s.connect((ip, port))
        banner = s.recv(1024)
        s.close()
        return banner.decode("utf-8", errors='ignore').strip()
    except:
        return None

def HTTPHeaderGrab(ip, port):
    """Análisis de servidor web con disfraz de navegador."""
    try:
        headers_disfraz = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        protocol = "https" if port == 443 else "http"
        response = requests.head(f"{protocol}://{ip}:{port}", headers=headers_disfraz, verify=False, timeout=5)
        return response.headers
    except:
        return {}

if __name__ == "__main__":
    target_input = input("Introduce IP o Dominio (ej: scanme.nmap.org): ")
    try:
        target = socket.gethostbyname(target_input)
        if target != target_input:
            print(f"[*] Objetivo resuelto: {target}")
    except socket.gaierror:
        print("[!] Error: No se pudo resolver el dominio.")
        sys.exit(1)

    found_ports = SynScanNinja(target)
    
    if found_ports:
        print(f"\n[+] Puertos detectados: {found_ports}")
        for p in found_ports:
            print(f"\n--- Puerto {p} ---")
            if p in [80, 443, 8080, 8443]:
                h = HTTPHeaderGrab(target, p)
                if h: print(f"    [WEB] Server: {h.get('Server', 'Desconocido')}")
            else:
                b = bannerGrab(target, p)
                if b: print(f"    [BANNER] {b[:60]}...")
    else:
        print("\n[!] No se encontraron puertos abiertos.")
