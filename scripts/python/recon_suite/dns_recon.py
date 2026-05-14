"""
dns_recon.py - Reconocimiento DNS y enumeración de subdominios
Puede ejecutarse de forma independiente o importarse.
"""

import sys
import socket
import dns.resolver


def ReverseDNS(ip):
    """
    Obtiene nombres de host asociados a una IP (PTR record).
    Devuelve lista de hostnames o lista vacía si no hay datos.
    """
    try:
        result = socket.gethostbyaddr(ip)
        return [result[0]] + list(result[1])
    except (socket.herror, socket.gaierror):
        return []
    except Exception:
        return []


def DNSRequest(subdomain, domain, hosts_acumulados):
    """
    Resuelve un subdominio y acumula los resultados en el diccionario compartido.
    Formato del diccionario: { ip: [subdominio1, subdominio2, ...] }
    """
    # Normalizar: eliminar puntos extras y construir FQDN
    domain_clean = domain.strip(".").lower()
    sub_clean    = subdomain.strip(".").lower()
    hostname     = f"{sub_clean}.{domain_clean}"

    try:
        result = dns.resolver.resolve(hostname, 'A')

        for answer in result:
            ip = answer.to_text()
            subs_para_esta_ip = [sub_clean]

            # Reverse DNS: a veces revela subdominios adicionales
            for h in ReverseDNS(ip):
                h_clean = h.strip(".").lower()
                if h_clean.endswith(f".{domain_clean}"):
                    # Extraemos solo la parte del subdominio
                    s = h_clean[: -(len(domain_clean) + 1)]
                    if s and s not in subs_para_esta_ip:
                        subs_para_esta_ip.append(s)

            # Merge con resultados previos para esta IP
            if ip in hosts_acumulados:
                combined = set(hosts_acumulados[ip]) | set(subs_para_esta_ip)
                hosts_acumulados[ip] = list(combined)
            else:
                hosts_acumulados[ip] = subs_para_esta_ip

    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
        pass  # Subdominio no existe o no responde: normal, silencioso
    except Exception:
        pass


def DNSSearch(domain, use_nums=True, dict_path="subdomains.txt"):
    """
    Enumeración masiva de subdominios usando un diccionario.
    - domain    : dominio objetivo (ej: example.com)
    - use_nums  : si True, prueba también word0, word1... word9
    - dict_path : ruta al archivo de subdominios
    Devuelve dict { ip: [subdominios] }
    """
    hosts_finales = {}

    # Cargar diccionario
    try:
        with open(dict_path, "r") as f:
            dictionary = [line.strip() for line in f if line.strip()]
        print(f"[*] Diccionario cargado: {len(dictionary)} entradas desde '{dict_path}'")
    except FileNotFoundError:
        print(f"[!] '{dict_path}' no encontrado. Usando lista básica de respaldo.")
        dictionary = ["www", "mail", "ftp", "vpn", "ns", "admin", "api", "dev", "test"]

    print(f"[*] Enumerando subdominios de {domain}...\n")

    total = len(dictionary)
    for idx, word in enumerate(dictionary, 1):
        # Mostrar progreso cada 50 palabras sin saturar la terminal
        if idx % 50 == 0 or idx == total:
            print(f"    Progreso: {idx}/{total}", end="\r")

        DNSRequest(word, domain, hosts_finales)

        if use_nums:
            for i in range(10):
                DNSRequest(f"{word}{i}", domain, hosts_finales)

    print()  # Nueva línea tras el progreso
    return hosts_finales


def _print_dns_results(domain, resultados):
    """Muestra el mapa de red descubierto de forma legible."""
    if not resultados:
        print(f"\n[!] No se encontraron subdominios activos para {domain}")
        return

    print(f"\n[+] Mapa de red descubierto para {domain}:\n")
    print(f"  {'IP':<18} {'SUBDOMINIOS ENCONTRADOS'}")
    print(f"  {'-'*17:<18} {'-'*40}")

    for ip, subs in sorted(resultados.items()):
        subs_str = ", ".join(sorted(subs))
        print(f"  {ip:<18} {subs_str}")

    print(f"\n  Total: {len(resultados)} IP(s) únicas, {sum(len(v) for v in resultados.values())} subdominio(s)")


# ─────────────────────────────────────────────
# Ejecución independiente
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("      RECONOCIMIENTO DNS / SUBDOMINIOS")
    print("=" * 50)

    target = input("\nIntroduce el dominio objetivo (ej: example.com): ").strip()
    if not target:
        print("[!] Dominio no válido.")
        sys.exit(1)

    usar_nums = input("¿Probar variantes numéricas (www0, ns1...)? [s/N]: ").strip().lower() == "s"

    resultados = DNSSearch(target, use_nums=usar_nums)
    _print_dns_results(target, resultados)