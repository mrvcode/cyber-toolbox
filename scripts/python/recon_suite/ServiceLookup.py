"""
ServiceLookup.py - Identificación y análisis de servicios por IP
Orquesta PortScan + Shodan para obtener un mapa de servicios detallado.
Puede ejecutarse de forma independiente o importarse desde main.py.
"""

import sys
import re
import socket
import getpass

from PortScan import (
    SynScanNinja, bannerGrab, HTTPHeaderGrab,
    WEB_PORTS, DEFAULT_PORTS
)
from ShodanSearch import ShodanLookup, conectar_api as shodan_conectar
from CVESearch import VuldbLookup

# Puertos esperados según el nombre del subdominio
DEFAULTS_POR_SUB = {
    "smtp":  [25, 465, 587],
    "mail":  [25, 465, 587, 110, 143],
    "dns":   [53],
    "ns":    [53],
    "web":   [80, 443, 8080, 8443],
    "www":   [80, 443],
    "api":   [80, 443, 3000, 5000, 8080],
    "ftp":   [20, 21],
    "ssh":   [22],
    "db":    [3306, 5432, 27017],
    "admin": [9090, 10000, 8443],
    "vpn":   [1194, 1723, 4500],
}

SERVICIOS_CRITICOS = {"ssh", "telnet", "mysql", "ftp", "rdp", "smb"}


def _parseBanner(banner_text, port):
    """
    Extrae producto, versión y nivel de riesgo de un banner o cabecera HTTP.
    Devuelve (product, version, severity).
    """
    product, version, severity = "", "", "Bajo"

    if not banner_text:
        return product, version, severity

    banner_str = str(banner_text)

    if port in WEB_PORTS:
        # Para web: analizamos la cabecera Server
        vals = banner_str.split("/")
        product = vals[0].strip()
        version = vals[1].strip() if len(vals) > 1 else ""
        severity = "Medio"
    else:
        # Patrón genérico: NombreProducto/versión o NombreProducto versión
        match = re.search(
            r"([A-Za-z][A-Za-z0-9_\-]+)[\s/_]([0-9]+(?:[.\-][0-9a-zA-Z]+)+)",
            banner_str
        )
        if match:
            product = match.group(1)
            version = match.group(2)
        else:
            # Fallback: buscar palabras clave de servicio conocidas
            keywords = re.findall(
                r"\b(ssh|ftp|smtp|telnet|mysql|postgresql|apache|nginx|iis|postfix|exim)\b",
                banner_str.lower()
            )
            if keywords:
                product = keywords[0]

        if product.lower() in SERVICIOS_CRITICOS:
            severity = "Alto"
        elif product:
            severity = "Medio"

    return product, version, severity


def _bannerRecord(ip, port):
    """
    Obtiene un registro completo de servicio para un puerto dado.
    Devuelve dict con port, product, version, severity.
    """
    product, version, severity = "", "", "Desconocido"

    try:
        if port in WEB_PORTS:
            headers = HTTPHeaderGrab(ip, port)
            server_header = headers.get("Server", "") if headers else ""
            if server_header:
                product, version, severity = _parseBanner(server_header, port)
        else:
            banner = bannerGrab(ip, port)
            if banner:
                product, version, severity = _parseBanner(banner, port)
    except Exception:
        pass  # Silencioso: seguimos con el resto de puertos

    return {
        "port":     port,
        "product":  product,
        "version":  version,
        "severity": severity,
    }


def serviceID(ip, subs=None, shodan_api=None):
    """
    Identifica servicios en una IP mediante tres fases progresivas:
    1. Inferencia por nombre de subdominio (rápido, sin tráfico extra)
    2. Shodan Lookup (si se proporciona API)
    3. SYN Scan ninja completo (si las fases anteriores no dieron resultados)

    Devuelve lista de dicts: [{ port, product, version, severity }, ...]
    """
    records = []
    scanned_ports = set()

    # ── FASE 1: Inferencia por subdominios ────────────────────────────────
    if subs:
        for sub in subs:
            # Normalizar: quitar dígitos finales (www1 → www, ns2 → ns)
            sub_base = sub.strip().lower().rstrip("0123456789")
            if sub_base in DEFAULTS_POR_SUB:
                for p in DEFAULTS_POR_SUB[sub_base]:
                    if p not in scanned_ports:
                        records.append(_bannerRecord(ip, p))
                        scanned_ports.add(p)

    # ── FASE 2: Shodan ────────────────────────────────────────────────────
    if shodan_api:
        try:
            shodan_data = ShodanLookup(shodan_api, ip)
            for r in shodan_data:
                port = r.get("port")
                if port and port not in scanned_ports:
                    # Si Shodan no identificó el producto, intentamos con banner propio
                    if not r.get("product"):
                        r_local = _bannerRecord(ip, port)
                        r["product"]  = r_local["product"]
                        r["version"]  = r_local["version"]
                        r["severity"] = r_local["severity"]
                    else:
                        r["severity"] = (
                            "Alto" if r["product"].lower() in SERVICIOS_CRITICOS
                            else "Medio"
                        )
                    records.append(r)
                    scanned_ports.add(port)
        except Exception as e:
            print(f"  [!] Shodan falló en fase 2: {e}")

    # ── FASE 3: SYN Scan completo ─────────────────────────────────────────
    if not records:
        open_ports = SynScanNinja(ip, DEFAULT_PORTS)
        for p in open_ports:
            if p not in scanned_ports:
                records.append(_bannerRecord(ip, p))
                scanned_ports.add(p)

    return records


def enrich_with_cves(records, vuldb_key):
    """
    Añade CVEs a cada registro de servicio consultando VulDB.
    Modifica los dicts in-place añadiendo la clave 'cves'.
    """
    for r in records:
        r["cves"] = []
        if r.get("product") and vuldb_key:
            try:
                r["cves"] = VuldbLookup(r["product"], r.get("version"), vuldb_key)
            except Exception:
                r["cves"] = []
    return records


def print_service_table(ip, records):
    """Muestra la tabla de servicios de forma legible."""
    if not records:
        print(f"  [!] No se encontraron servicios para {ip}")
        return

    print(f"\n  {'PUERTO':<8} {'PRODUCTO':<18} {'VERSIÓN':<12} {'RIESGO':<10} CVEs")
    print(f"  {'-'*7:<8} {'-'*17:<18} {'-'*11:<12} {'-'*9:<10} {'-'*30}")

    for r in records:
        port     = str(r.get("port", "?"))
        product  = (r.get("product") or "Desconocido")[:17]
        version  = (r.get("version") or "-")[:11]
        severity = r.get("severity", "?")
        cves     = r.get("cves", [])
        cve_str  = (", ".join(cves[:3]) + (" ..." if len(cves) > 3 else "")) if cves else "Ninguno"

        # Color visual según riesgo (funciona en terminales ANSI)
        color = ""
        reset = "\033[0m"
        if severity == "Alto":
            color = "\033[91m"   # Rojo
        elif severity == "Medio":
            color = "\033[93m"   # Amarillo

        print(f"  {port:<8} {product:<18} {version:<12} {color}{severity:<10}{reset} {cve_str}")


# ─────────────────────────────────────────────
# Ejecución independiente
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("       IDENTIFICACIÓN DE SERVICIOS Y VULNERABILIDADES")
    print("=" * 55)

    target_input = input("\nIntroduce IP o Dominio objetivo: ").strip()
    if not target_input:
        print("[!] Objetivo vacío.")
        sys.exit(1)

    try:
        target_ip = socket.gethostbyname(target_input)
        if target_ip != target_input:
            print(f"[*] Resuelto: {target_input} → {target_ip}")
    except socket.gaierror:
        print("[!] No se pudo resolver el dominio.")
        sys.exit(1)

    print("\n--- CLAVES DE API (Enter para omitir herramienta) ---")
    shodan_key = getpass.getpass("Shodan API Key: ").strip()
    vuldb_key  = getpass.getpass("VulDB  API Key: ").strip()

    shodan_api = None
    if shodan_key:
        shodan_api = shodan_conectar(shodan_key)
        if not shodan_api:
            print("[!] Shodan no disponible, continuando sin él.")

    print(f"\n[*] Analizando {target_ip}...")
    records = serviceID(target_ip, subs=[], shodan_api=shodan_api)

    if vuldb_key and records:
        print("[*] Enriqueciendo con datos de VulDB...")
        records = enrich_with_cves(records, vuldb_key)

    print(f"\n[+] Servicios detectados en {target_ip}:")
    print_service_table(target_ip, records)
