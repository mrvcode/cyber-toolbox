🔍 Windows Audit - Auditoría Universal PowerShell

===============================================================================

Nivel: 🟠 Intermedio / Blue Teaming
Categoria: Seguridad/Auditoría
Version: Compatible (Universal SID Detection)

===============================================================================

📋 DESCRIPCION

===============================================================================


Esta es la versión avanzada y ultra-compatible de la herramienta de auditoría 
mrcvode. A diferencia de scripts estándar, este utiliza identificadores de 
seguridad (SID) y verificaciones dinámicas de comandos para funcionar en 
cualquier edición de Windows, sin importar el idioma del sistema.


===============================================================================

🎯 ¿PARA QUE SIRVE?

===============================================================================


Auditoría Multilingüe: Funciona en Windows en español, inglés y otros idiomas.

Hardening Silencioso: Activa ScriptBlock Logging sin interrumpir al usuario.

Análisis de Persistencia: Detecta usuarios nuevos y tareas programadas activas.

Verificación de Red: Identifica exposición de RDP y WinRM de forma dinámica.


===============================================================================

📦 REQUISITOS Y COMPATIBILIDAD

===============================================================================


Privilegios: Requiere ejecución como ADMINISTRADOR.

Compatibilidad: Diseñado para Windows 10/11 y Windows Server 2016+.

Idiomas: Soportado globalmente (usa SID S-1-5-32-544 para administradores).

Versiones PS: Compatible con PowerShell 5.1 y PowerShell Core 6/7+.


===============================================================================

🚀 USO DEL SCRIPT

===============================================================================


Sintaxis:
./scripts/windows-ps1/Instalar_Audit.ps1

1. Abre PowerShell como Administrador.

2. Ejecuta el instalador. El script detectará tu versión de PS y creará 
   la carpeta de módulos correspondiente ($HOME\Documents\...).

3. Llama a la herramienta desde cualquier consola escribiendo:
MyAudit


===============================================================================

🛡️ NOVEDADES DE ESTA VERSION (COMPATIBLE)

===============================================================================


Detección por SID:

No busca el nombre "Administradores", sino el ID único del grupo. Esto evita 
errores en sistemas con idiomas no latinos.


Carga Dinámica de Módulos:

Intenta importar 'NetSecurity' y 'LocalAccounts' solo si están disponibles, 
evitando errores en instalaciones "Lite" o Core de Windows.


Búsqueda de Firewall Expandida:

Ahora detecta reglas bajo los nombres "WinRM", "RDP", "Escritorio remoto" 
y "Remote Desktop" simultáneamente.


Manejo de Errores Silencioso:

Cada bloque está envuelto en Try/Catch, lo que permite que el script termine 
de auditar aunque una sección (como los Logs) esté bloqueada por un EDR.


===============================================================================

⚠️ ADVERTENCIAS EMPRESARIALES

===============================================================================


Visibilidad: La activación de logs de telemetría es una acción de Hardening 
que queda registrada. Úsala con autorización en entornos de terceros.

Forense: Este script consulta logs existentes; si el atacante ha limpiado 
el visor de eventos (wevtutil cl), el script informará que no hay actividad.


===============================================================================

💡 TIP FINAL

===============================================================================


Si ejecutas 'MyAudit' y ves "Sin actividad reciente" en los logs, ¡es buena 
señal! Significa que no se han detectado ejecuciones sospechosas en las 
últimas 24 horas desdel el momento en que activaste el logging.


Script mejorado por mrvcode
Uso exclusivo educativo y en entornos autorizados
