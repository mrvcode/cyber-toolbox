import dns.resolver
import socket

def ReverseDNS(ip):
    """Obtiene nombres asociados a una IP (Reverse DNS)."""
    try:
        result = socket.gethostbyaddr(ip)
        return [result[0]] + list(result[1])
    except socket.herror:
        return []

def DNSRequest(sub, domain, hosts_acumulados):
    """Consulta un subdominio y actualiza el diccionario de resultados."""
    # Aseguramos que el dominio tenga el punto correctamente
    if not domain.startswith("."):
        domain = "." + domain
    
    hostname = sub + domain
    
    try:
        result = dns.resolver.resolve(hostname, 'A')
        for answer in result:
            ip = answer.to_text()
            hostnames_encontrados = ReverseDNS(ip)
            
            # Lista temporal de subdominios encontrados para esta IP
            subs_actuales = [sub]
            
            for h in hostnames_encontrados:
                if h.endswith(domain):
                    # Extraemos el subdominio quitando el dominio base
                    s = h.replace(domain, "").rstrip(".")
                    if s: subs_actuales.append(s)
            
            # Guardamos en el diccionario evitando duplicados (usando set)
            if ip in hosts_acumulados:
                hosts_acumulados[ip] = list(set(hosts_acumulados[ip] + subs_actuales))
            else:
                hosts_acumulados[ip] = list(set(subs_actuales))
    except Exception:
        pass

def DNSSearch(domain, use_nums, dict_path="subdomains.txt"):
    """Inicia la búsqueda masiva."""
    hosts_finales = {}
    
    # Intentar cargar diccionario externo
    try:
        with open(dict_path, "r") as f:
            dictionary = f.read().splitlines()
    except FileNotFoundError:
        print("[!] Archivo no encontrado. Usando lista básica...")
        dictionary = ["www", "mail", "ftp", "vpn", "ns", "admin"]

    print(f"[*] Escaneando {domain}...")
    for word in dictionary:
        DNSRequest(word, domain, hosts_finales)
        if use_nums:
            for i in range(0, 10): # Busca ns0, ns1...
                DNSRequest(word + str(i), domain, hosts_finales)
    
    return hosts_finales

if __name__ == "__main__":
    # input usuario
    target = input("Introduce dominio (ej: google.com): ")
    resultados = DNSSearch(target, True)
    
    print("\n[+] MAPA DE RED ENCONTRADO:")
    for ip, subs in resultados.items():
        print(f"{ip.ljust(15)} | {', '.join(subs)}")
