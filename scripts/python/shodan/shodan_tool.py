import shodan_utils
import getpass
import json

def main():
    print("=== HERRAMIENTA AUTOMATIZADA DE SHODAN ===")

    # 1. Autenticación segura
    key = getpass.getpass("Introduce tu API KEY (no se verá al escribir): ")
    api = shodan_utils.conectar_api(key)

    # 2. Selección de modo
    print("\n¿Qué acción deseas realizar?")
    print("1. Búsqueda masiva (Search)")
    print("2. Investigar IP específica (Host Lookup)")
    opcion = input("\nSelecciona una opción (1 o 2): ")

    if opcion == "1":
        # MODO SEARCH
        query = input("[?] Introduce tu consulta (ej: org:Google): ")
        print(f"[*] Buscando '{query}'...")
        resultados = shodan_utils.queryShodan(api, query)

        print(f"\n[+] Resultados encontrados: {len(resultados)}")
        for ip, info in resultados.items():
            print(f"IP: {ip} | Puertos detectados: {info['ports']}")

    elif opcion == "2":
        # MODO HOST LOOKUP
        target_ip = input("[?] Introduce la IP a investigar: ")
        print(f"[*] Analizando la IP: {target_ip}...")
        datos = shodan_utils.ShodanLookup(api, target_ip)

        if datos:
            print(f"\n[+] Análisis de {target_ip}:")
            for item in datos:
                print(f"\n--- Puerto: {item['port']} ({item['product']}) ---")
                if item['vulnerabilities']:
                    # Solo imprimimos los códigos CVE, sin todo el texto largo
                    print(f"      [!] VULNERABILIDADES DETECTADAS: {', '.join(item['vulnerabilities'])}")
                else:
                    print("      [✓] No se detectaron vulnerabilidades conocidas.")
        else:
            print("[!] No se encontraron datos para esa IP.")

    else:
        print("[!] Opción no válida.")

if __name__ == "__main__":
    main()
