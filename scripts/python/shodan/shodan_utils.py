import shodan

def conectar_api(api_key):
    """Crea la conexión con la API."""
    return shodan.Shodan(api_key)

def queryShodan(api, query):
    """Función para búsqueda masiva (api.search)."""
    hosts = {}
    try:
        results = api.search(query)
        for service in results["matches"]:
            ip = service["ip_str"]
            ports = service["port"]
            if ip in hosts:
                if ports not in hosts[ip]["ports"]:
                    hosts[ip]["ports"].append(ports)
            else:
                hosts[ip] = {"ports": [ports]}
        return hosts
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return {}

def ShodanLookup(api, ip):
    try:
        results = api.host(ip)
        records = []
        for item in results["data"]:
            vulns = item.get("vulns", [])
            r = {
                "port": item.get("port"),
                "product": item.get("product", "N/A"),
                "version": item.get("version", "N/A"),
                "vulnerabilities": vulns 
            }
            records.append(r)
        return records
    except Exception as e:
        print(f"Error en lookup: {e}")
        return []
