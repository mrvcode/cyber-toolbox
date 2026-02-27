#!/bin/bash
# 🔧 test_benchmark.sh - Script educativo para pruebas de rendimiento con Apache Bench
# 📝 Documentación: test_benchmark.md
# 👤 by mrvcode - Uso exclusivo en entornos autorizados

set -euo pipefail

# Colores para output (opcional)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parámetros por defecto
TARGET="${1:-http://127.0.0.1:8000}"
REQUESTS="${2:-100}"
CONCURRENT="${3:-10}"
LOGFILE="/tmp/ab_$(date +%Y%m%d_%H%M%S).log"

echo -e "${GREEN}[*] Iniciando test de rendimiento${NC}"
echo "    → Objetivo: $TARGET"
echo "    → Peticiones: $REQUESTS | Concurrentes: $CONCURRENT"
echo "    → Log: $LOGFILE"
echo ""

# Verificar que ab está instalado
if ! command -v ab &> /dev/null; then
    echo -e "${RED}[!] Error: Apache Bench (ab) no está instalado${NC}"
    echo "    Instala con: sudo apt install apache2-utils"
    exit 1
fi

# Ejecutar ab y guardar resultados
ab -n "$REQUESTS" -c "$CONCURRENT" -g "$LOGFILE" "$TARGET" 2>/dev/null || {
    echo -e "${RED}[!] Error en la ejecución de ab${NC}"
    exit 2
}

# Mostrar métrica principal
echo ""
echo -e "${GREEN}[✓] Test completado${NC}"
echo "    📊 Requests per second:"
grep "Requests per second" "$LOGFILE" | tail -1 | awk '{print "       " $4 " req/s"}'

echo ""
echo -e "${YELLOW}💡 Tip:${NC} Revisa $LOGFILE para ver todas las métricas"
