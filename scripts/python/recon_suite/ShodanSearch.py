"""
ShodanSearch.py - Consultas a la API de Shodan
Compatible con el plan GRATUITO de Shodan.
Puede ejecutarse de forma independiente o importarse.

NOTA PLAN GRATUITO:
  - api.host(ip)    → Funciona siempre ✓
  - api.search(...) → Funciona con hasta 100 resultados ✓
  - Filtros como org: → Limitados o bloqueados en free tier ✗
"""

import sys
import getpass
import shodan


def conectar_api(api_key):
    """
    Crea y verifica la conexión con la API de Shodan.
    Devuelve el objeto API o None si falla.
    """
    try:
        api = shodan.Shodan(api_key)
        # Verificación real: si la clave es inválida esto lanza excepción
        api.info()
        return api
    except shodan.APIError as e:
        print(f"[!] Error de autenticación Shodan: {e}")
        return None
    except Exception as e:
        print(f"[!] No se pudo conectar con Shodan: {e}")
        return None


def ShodanLookup(api, ip):
    """
    Consulta información detallada de una IP específica (api.host).
    Funciona con el plan gratuito.
    Devuelve lista de dicts con puerto, producto, versión y CVEs.
    """
    records = []
    try:
        result = api.host(ip)
        for item in result.get("data", []):
            vulns = list(item.get("vulns", {}).keys())  # Las keys son los CVE IDs
            records.append({
                "port":            item.get("port"),
                "product":         item.get("product") or "",
                "version":         item.get("version") or "",
                "vulnerabilities": vulns,
                "transport":       item.get("transport", "tcp"),
                "banner":          item.get("data", "")[:100],
            })
    except shodan.APIError as e:
        if "No information available" in str(e):
            print(f"  [!] Shodan no tiene datos para {ip}")
        else:
            print(f"  [!] Error Shodan al consultar {ip}: {e}")
    except Exception as e:
        print(f"  [!] Error inesperado en Shodan Lookup: {e}")

    return records


def queryShodan(api, query):
    """
    Búsqueda masiva por query (api.search).
    Funciona con el plan gratuito (máx. 100 resultados).
    EVITAR filtros como org:, net: — limitados en free tier.
    Usa preferiblemente: hostname:, port:, product:, country:
    Devuelve dict {ip: {"ports": [...], "hostnames": [...]}}
    """
    hosts = {}
    try:
        results = api.search(query)
        total = results.get("total", 0)
        matches = results.get("matches", [])

        if total == 0:
            return {}

        for service in matches:
            ip = service.get("ip_str", "")
            port = service.get("port")
            hostnames = service.get("hostnames", [])

            if not ip or not port:
                continue

            if ip in hosts:
                if port not in hosts[ip]["ports"]:
                    hosts[ip]["ports"].append(port)
            else:
                hosts[ip] = {"ports": [port], "hostnames": hostnames}

    except shodan.APIError as e:
        if "upgrade" in str(e).lower() or "plan" in str(e).lower():
            print(f"  [!] Esta búsqueda requiere plan de pago en Shodan: {e}")
        else:
            print(f"  [!] Error en búsqueda Shodan: {e}")
    except Exception as e:
        print(f"  [!] Error inesperado en Shodan Search: {e}")

    return hosts


def _print_lookup_results(ip, datos):
    """Muestra resultados de Host Lookup de forma legible."""
    if not datos:
        print(f"  [!] Sin datos para {ip}")
        return

    print(f"\n  {'PUERTO':<8} {'PRODUCTO':<18} {'VERSIÓN':<12} {'CVEs'}")
    print(f"  {'-'*7:<8} {'-'*17:<18} {'-'*11:<12} {'-'*30}")

    for item in datos:
        cve_str = ", ".join(item["vulnerabilities"]) if item["vulnerabilities"] else "Ninguno"
        prod = (item["product"] or "Desconocido")[:17]
        ver  = (item["version"] or "-")[:11]
        print(f"  {item['port']:<8} {prod:<18} {ver:<12} {cve_str}")


def _print_search_results(resultados):
    """Muestra resultados de búsqueda masiva de forma legible."""
    if not resultados:
        print("  [!] Sin resultados.")
        return

    print(f"\n  {'IP':<18} {'PUERTOS':<30} {'HOSTNAMES'}")
    print(f"  {'-'*17:<18} {'-'*29:<30} {'-'*30}")

    for ip, info in resultados.items():
        ports_str = str(info["ports"])[:28]
        hosts_str = ", ".join(info.get("hostnames", []))[:30] or "-"
        print(f"  {ip:<18} {ports_str:<30} {hosts_str}")


# ─────────────────────────────────────────────
# Ejecución independiente
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("         CONSULTA SHODAN (FREE TIER)")
    print("=" * 50)

    api_key = getpass.getpass("\nShodan API Key (oculta): ").strip()
    if not api_key:
        print("[!] La API Key no puede estar vacía.")
        sys.exit(1)

    api = conectar_api(api_key)
    if not api:
        sys.exit(1)

    print("\n¿Qué acción deseas realizar?")
    print("  [1] Investigar una IP específica (Host Lookup) — recomendado free tier")
    print("  [2] Búsqueda por filtro (Search)  — ej: port:22 country:ES")
    opcion = input("\nOpción (1/2): ").strip()

    if opcion == "1":
        target_ip = input("[?] IP a investigar: ").strip()
        if not target_ip:
            print("[!] IP no válida.")
            sys.exit(1)
        print(f"\n[*] Consultando Shodan para {target_ip}...")
        datos = ShodanLookup(api, target_ip)
        print(f"\n[+] Servicios detectados en {target_ip}:")
        _print_lookup_results(target_ip, datos)

    elif opcion == "2":
        print("\n  Ejemplos de queries compatibles con free tier:")
        print("  · port:22 country:ES")
        print("  · product:Apache version:2.4")
        print("  · hostname:example.com")
        query = input("\n[?] Introduce la query: ").strip()
        if not query:
            print("[!] Query vacía.")
            sys.exit(1)
        print(f"\n[*] Buscando '{query}' en Shodan...")
        resultados = queryShodan(api, query)
        print(f"\n[+] {len(resultados)} host(s) encontrados:")
        _print_search_results(resultados)

    else:
        print("[!] Opción no válida.")
        sys.exit(1)