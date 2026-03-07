#!/bin/bash

# --- COLORES ---
BLUE='\033[44;97m'
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE} [!] REVISION DE SEGURIDAD AVANZADA (LINUX) [!] ${NC}"
echo -e "${GRAY}----------------------------------------------------${NC}"

# 1. AUDITORÍA DE COMANDOS (Equivalente a Logs PS)
echo -e "\n${MAGENTA}[?] ULTIMOS COMANDOS EJECUTADOS (Historial):${NC}"
# Intentamos leer el historial del usuario actual
tail -n 5 ~/.bash_history 2>/dev/null | sed 's/^/  > /' || echo -e "${GREEN}[+] Historial no disponible o vacío.${NC}"

# 2. USUARIOS RECIENTES
echo -e "\n${CYAN}[!] ACTIVIDAD EN /HOME (Ultimas 24h):${NC}"
RECENT_USERS=$(find /home -maxdepth 1 -type d -ctime -1 2>/dev/null | grep -v "/home$")
if [ -z "$RECENT_USERS" ]; then
    echo -e "${GREEN}[+] No se han detectado carpetas de usuario nuevas (24h).${NC}"
else
    echo -e "${RED}[!] Carpetas modificadas:${NC}"
    echo "$RECENT_USERS" | sed 's/^/  - /'
fi

# 3. ADMINISTRADORES (UID 0 y Grupo Sudo)
echo -e "\n${CYAN}[+] USUARIOS CON PRIVILEGIOS (Root/Sudo):${NC}"
(
echo "USUARIO TIPO"
awk -F: '($3 == 0) {print $1 " [ROOT-UID]"}' /etc/passwd
getent group sudo | cut -d: -f4 | tr ',' '\n' | awk '{print $1 " [SUDO-GROUP]"}'
) | column -t | sed 's/^/  /'

# 4. RED Y SERVICIOS (SSH / Puertos abiertos)
echo -e "\n${YELLOW}[+] ESTADO DE RED Y SERVICIOS (SSH):${NC}"
# Estado de SSH
if systemctl is-active --quiet ssh 2>/dev/null; then
    echo -e "  SSH Service: ${GREEN}ACTIVO${NC}"
else
    echo -e "  SSH Service: ${RED}INACTIVO${NC}"
fi

# Puertos en escucha (Equivalente a ver reglas de Firewall activas)
echo -e "\n${YELLOW}[+] Puertos en escucha (Listening):${NC}"
ss -tuln | grep "LISTEN" | awk '{print $1, $5}' | column -t | sed 's/^/  /'

# 5. TAREAS PROGRAMADAS (Cronjobs)
echo -e "\n${GRAY}[+] TAREAS PROGRAMADAS (Cron):${NC}"
ls /etc/cron.daily /etc/cron.hourly 2>/dev/null | head -n 5 | sed 's/^/  /'

# 6. LOGS DE SISTEMA (Errores)
echo -e "\n${MAGENTA}[+] ULTIMOS 5 ERRORES DE SISTEMA:${NC}"
if command -v journalctl &> /dev/null; then
    journalctl -p err -n 5 --no-pager | tail -n 5 | cut -c 1-100 | sed 's/^/  /'
else
    grep -i "error" /var/log/syslog 2>/dev/null | tail -n 5 | sed 's/^/  /'
fi

echo -e "\n${BLUE} [!] Auditoria completada. ${NC}"
