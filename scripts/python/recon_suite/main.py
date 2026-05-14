"""
main.py - Herramienta de reconocimiento modular
Coursera: "Python in Recon" — Ejercicio de auditoría ética

Permite ejecutar las herramientas de forma independiente o combinada:
  [1] DNS Recon     — Enumeración de subdominios
  [2] Port Scan     — Escaneo de puertos sigiloso
  [3] Shodan        — Inteligencia OSINT por IP
  [4] CVE Search    — Búsqueda de vulnerabilidades en VulDB

USO:
  sudo python3 main.py        (recomendado: root para SYN scan)
  python3 main.py             (usa TCP connect como fallback)
"""

import sys
import socket
import getpass


# ─────────────────────────────────────────────────────────────
# MENÚ Y SELECCIÓN DE HERRAMIENTAS
# ─────────────────────────────────────────────────────────────

HERRAMIENTAS = {
    "1": "DNS Recon     (enumeración de subdominios)",
    "2": "Port Scan     (escaneo sigiloso de puertos)",
    "3": "Shodan        (OSINT por IP — requiere API key)",
    "4": "CVE Search    (vulnerabilidades — requiere API key VulDB)",
}


def mostrar_banner():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║       HERRAMIENTA DE RECONOCIMIENTO MODULAR          ║")
    print("║                   Auditoría ética                    ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()


def seleccionar_herramientas():
    """
    Muestra el menú y devuelve un set con los números de herramienta elegidos.
    """
    print("Herramientas disponibles:")
    for num, desc in HERRAMIENTAS.items():
        print(f"  [{num}] {desc}")
    print("  [A] Todas las herramientas")
    print()

    seleccion = input("¿Qué herramientas ejecutar? (ej: 1,3  o  A): ").strip().upper()

    if seleccion == "A":
        return {"1", "2", "3", "4"}

    elegidas = set()
    for c in seleccion.replace(" ", "").split(","):
        if c in HERRAMIENTAS:
            elegidas.add(c)
        else:
            print(f"  [!] Opción '{c}' no reconocida, ignorada.")

    if not elegidas:
        print("[!] No se seleccionó ninguna herramienta válida.")
        sys.exit(1)

    return elegidas


def pedir_objetivo():
    """Solicita el objetivo (IP o dominio) y lo valida."""
    print()
    objetivo_input = input("Objetivo (IP o dominio, ej: scanme.nmap.org): ").strip()
    if not objetivo_input:
        print("[!] Objetivo vacío.")
        sys.exit(1)

    try:
        objetivo_ip = socket.gethostbyname(objetivo_input)
        dominio = objetivo_input if objetivo_input != objetivo_ip else None

        if dominio:
            print(f"  [*] Dominio resuelto: {dominio} → {objetivo_ip}")

        return objetivo_ip, dominio  # (ip, dominio o None)

    except socket.gaierror:
        print(f"[!] No se pudo resolver '{objetivo_input}'.")
        sys.exit(1)


def pedir_claves(herramientas):
    """Solicita solo las API keys necesarias para las herramientas elegidas."""
    claves = {}

    if "3" in herramientas:
        print()
        print("─── Credenciales Shodan ─────────────────────────────")
        claves["shodan"] = getpass.getpass("  Shodan API Key (oculta): ").strip()

    if "4" in herramientas:
        print()
        print("─── Credenciales VulDB ──────────────────────────────")
        claves["vuldb"] = getpass.getpass("  VulDB  API Key (oculta): ").strip()

    return claves


# ─────────────────────────────────────────────────────────────
# EJECUCIÓN DE CADA MÓDULO
# ─────────────────────────────────────────────────────────────

def ejecutar_dns(dominio):
    """Fase 1: Enumeración DNS. Devuelve { ip: [subdominios] }"""
    print()
    print("══ [1] DNS RECON ════════════════════════════════════════")

    if not dominio:
        print("  [!] DNS Recon necesita un dominio, no solo una IP.")
        print("  [!] Saltando esta fase.")
        return {}

    try:
        from dns_recon import DNSSearch, _print_dns_results
        usar_nums = input("  ¿Probar variantes numéricas (ns0, ns1...)? [s/N]: ").strip().lower() == "s"
        resultados = DNSSearch(dominio, use_nums=usar_nums)
        _print_dns_results(dominio, resultados)
        return resultados
    except ImportError:
        print("  [!] dns_recon.py no encontrado en la misma carpeta.")
        return {}
    except Exception as e:
        print(f"  [!] Error en DNS Recon: {e}")
        return {}


def ejecutar_portscan(target_ip):
    """Fase 2: Escaneo de puertos. Devuelve lista de puertos abiertos."""
    print()
    print("══ [2] PORT SCAN ════════════════════════════════════════")

    try:
        from PortScan import SynScanNinja, _print_scan_results
        print(f"  [*] Escaneando {target_ip}...")
        puertos = SynScanNinja(target_ip)
        _print_scan_results(target_ip, puertos)
        return puertos
    except ImportError:
        print("  [!] PortScan.py no encontrado en la misma carpeta.")
        return []
    except Exception as e:
        print(f"  [!] Error en Port Scan: {e}")
        return []


def ejecutar_shodan(target_ip, api_key):
    """Fase 3: Consulta Shodan. Devuelve lista de registros de servicio."""
    print()
    print("══ [3] SHODAN LOOKUP ════════════════════════════════════")

    if not api_key:
        print("  [!] No se proporcionó API key de Shodan. Saltando.")
        return []

    try:
        from ShodanSearch import conectar_api, ShodanLookup, _print_lookup_results
        api = conectar_api(api_key)
        if not api:
            return []
        print(f"  [*] Consultando Shodan para {target_ip}...")
        datos = ShodanLookup(api, target_ip)
        print(f"\n  [+] Servicios detectados por Shodan en {target_ip}:")
        _print_lookup_results(target_ip, datos)
        return datos
    except ImportError:
        print("  [!] ShodanSearch.py no encontrado en la misma carpeta.")
        return []
    except Exception as e:
        print(f"  [!] Error en Shodan: {e}")
        return []


def ejecutar_cve(servicios, api_key):
    """Fase 4: Búsqueda de CVEs para los servicios descubiertos."""
    print()
    print("══ [4] CVE SEARCH (VulDB) ═══════════════════════════════")

    if not api_key:
        print("  [!] No se proporcionó API key de VulDB. Saltando.")
        return

    if not servicios:
        print("  [!] No hay servicios que analizar. Ejecuta Port Scan o Shodan primero.")
        return

    try:
        from CVESearch import VuldbLookup

        # Deduplicar: un solo lookup por producto único
        vistos = {}
        for s in servicios:
            prod = (s.get("product") or "").strip()
            ver  = (s.get("version") or "").strip()
            if prod and prod not in vistos:
                vistos[prod] = ver

        if not vistos:
            print("  [!] No se identificaron productos en los servicios detectados.")
            return

        print(f"\n  {'PRODUCTO':<20} {'VERSIÓN':<12} {'CVEs ENCONTRADOS'}")
        print(f"  {'-'*19:<20} {'-'*11:<12} {'-'*35}")

        for prod, ver in vistos.items():
            cves = VuldbLookup(prod, ver or None, api_key)
            cve_str = (", ".join(cves[:4]) + (" ..." if len(cves) > 4 else "")) if cves else "Ninguno"
            print(f"  {prod:<20} {(ver or '-'):<12} {cve_str}")

    except ImportError:
        print("  [!] CVESearch.py no encontrado en la misma carpeta.")
    except Exception as e:
        print(f"  [!] Error en CVE Search: {e}")


# ─────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────

def mostrar_resumen(target_ip, dominio, dns_data, puertos, shodan_data):
    """Combina todos los resultados en un resumen ejecutivo."""
    print()
    print("══ RESUMEN EJECUTIVO ════════════════════════════════════")
    print(f"\n  Objetivo analizado : {target_ip}" + (f" ({dominio})" if dominio else ""))

    if dns_data:
        total_subs = sum(len(v) for v in dns_data.values())
        print(f"  Subdominios activos: {total_subs} en {len(dns_data)} IP(s)")

    if puertos:
        print(f"  Puertos abiertos   : {', '.join(str(p) for p in puertos)}")
    else:
        print(f"  Puertos abiertos   : Ninguno detectado (o no se ejecutó Port Scan)")

    all_services = shodan_data if shodan_data else []
    if all_services:
        with_vulns = [s for s in all_services if s.get("vulnerabilities")]
        print(f"  Servicios (Shodan) : {len(all_services)}, con CVEs conocidos: {len(with_vulns)}")

    print()
    print("  Análisis completado.")
    print("═" * 55)


# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────

def main():
    mostrar_banner()

    # 1. Selección de herramientas
    herramientas = seleccionar_herramientas()
    print(f"\n  Herramientas seleccionadas: {', '.join(sorted(herramientas))}")

    # 2. Objetivo
    target_ip, dominio = pedir_objetivo()

    # 3. API keys (solo las necesarias)
    claves = pedir_claves(herramientas)

    # ── Ejecución de fases ────────────────────────────────────
    dns_data    = {}
    puertos     = []
    shodan_data = []

    if "1" in herramientas:
        dns_data = ejecutar_dns(dominio)

    if "2" in herramientas:
        puertos = ejecutar_portscan(target_ip)

    if "3" in herramientas:
        shodan_data = ejecutar_shodan(target_ip, claves.get("shodan", ""))

    if "4" in herramientas:
        # CVE Search usa los servicios de Shodan si están disponibles,
        # o construye registros básicos con los puertos encontrados
        servicios_para_cve = shodan_data or [{"product": "", "version": "", "port": p} for p in puertos]
        ejecutar_cve(servicios_para_cve, claves.get("vuldb", ""))

    # ── Resumen final ─────────────────────────────────────────
    if len(herramientas) > 1:
        mostrar_resumen(target_ip, dominio, dns_data, puertos, shodan_data)


if __name__ == "__main__":
    main()