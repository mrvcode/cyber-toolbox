"""
CVESearch.py - Búsqueda de vulnerabilidades en VulDB
Compatible con el plan gratuito de VulDB.
Puede ejecutarse de forma independiente o importarse.

NOTA: La API gratuita de VulDB permite un número limitado de consultas al día.
"""

import sys
import getpass
import requests


def VuldbLookup(product, version=None, api_key=None):
    """
    Consulta vulnerabilidades en VulDB para un producto/versión dado.
    - product : nombre del producto (ej: "Apache", "OpenSSH")
    - version : versión específica (ej: "2.4.49") — opcional
    - api_key : token de VulDB
    Devuelve lista de CVE IDs encontrados, o [] si no hay resultados.
    """
    if not api_key:
        return []

    if not product or not product.strip():
        return []

    url = "https://vuldb.com/?api"

    # Construir query de búsqueda avanzada
    if version:
        q = f"product:{product.strip()},version:{version.strip()}"
    else:
        q = f"product:{product.strip()}"

    payload = {
        "apikey":         api_key.strip(),
        "advancedsearch": q,
    }

    try:
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()
        j = response.json()

        cves = []
        for entry in j.get("result", []):
            # El CVE ID está en entry["source"]["cve"]["id"]
            try:
                cve_id = entry["source"]["cve"]["id"]
                if cve_id and cve_id not in cves:
                    cves.append(cve_id)
            except (KeyError, TypeError):
                # Algunos registros pueden no tener CVE asociado
                pass

        return cves

    except requests.exceptions.Timeout:
        print(f"  [!] VulDB: tiempo de espera agotado para '{product}'")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"  [!] VulDB error HTTP {e.response.status_code}: {e}")
        return []
    except Exception as e:
        print(f"  [!] Error inesperado en VulDB: {e}")
        return []


def _print_cve_results(product, version, cves):
    """Muestra CVEs encontrados de forma legible."""
    label = f"{product} {version}".strip() if version else product
    if not cves:
        print(f"  {label:<25} → Sin CVEs conocidos en VulDB")
    else:
        print(f"  {label:<25} → {len(cves)} CVE(s): {', '.join(cves[:5])}", end="")
        if len(cves) > 5:
            print(f" (+{len(cves)-5} más)", end="")
        print()


# ─────────────────────────────────────────────
# Ejecución independiente
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("     BÚSQUEDA DE CVEs EN VULDB")
    print("=" * 50)

    api_key = getpass.getpass("\nVulDB API Key (oculta): ").strip()
    if not api_key:
        print("[!] La API Key no puede estar vacía.")
        sys.exit(1)

    product = input("[?] Nombre del producto (ej: OpenSSH, Apache): ").strip()
    if not product:
        print("[!] El nombre del producto no puede estar vacío.")
        sys.exit(1)

    version = input("[?] Versión (dejar vacío para todas): ").strip() or None

    print(f"\n[*] Buscando vulnerabilidades para '{product}'" +
          (f" v{version}" if version else "") + "...")

    cves = VuldbLookup(product, version, api_key)

    print(f"\n[+] Resultados para {product}:")
    _print_cve_results(product, version, cves)

    if cves:
        print(f"\n  Lista completa de CVEs encontrados:")
        for i, cve in enumerate(cves, 1):
            print(f"    {i:>3}. {cve}")
