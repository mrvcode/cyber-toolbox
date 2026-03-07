🔍 System Audit - Auditoría de Seguridad Linux

===============================================================================

Nivel: 🟠 Intermedio / Blue Teaming
Categoria: Seguridad/Auditoría
Herramienta: Bash Script / Linux Native Tools

===============================================================================

📋 DESCRIPCION

===============================================================================


Este script automatiza la recolección de evidencias tácticas en sistemas Linux.
Está diseñado con un estilo inspirado en las máquinas de Hack The Box (HTB) 
para identificar rápidamente vectores de persistencia, errores de sistema y 
configuraciones de red expuestas.


===============================================================================

🎯 ¿PARA QUE SIRVE?

===============================================================================


Post-Explotación: Enumeración rápida tras ganar acceso a una máquina.

Hardening: Revisar si tu propio servidor tiene puertos o servicios expuestos.

Detección de Intrusos: Ver comandos recientes y nuevos usuarios en el sistema.

Auditoría de Cumplimiento: Verificar el estado de SSH y tareas programadas.


===============================================================================

📦 REQUISITOS

===============================================================================


El script utiliza herramientas nativas de Linux. No requiere instalaciones 
externas en la mayoría de distribuciones modernas (Ubuntu, Debian, CentOS, etc).

Verificar que tienes instalados:

systemctl o service (para gestión de servicios)

ss o netstat (para auditoría de red)

journalctl o acceso a /var/log/syslog


===============================================================================

🚀 USO DEL SCRIPT

===============================================================================


Sintaxis:
./scripts/bash/system_audit.sh

Pasos para ejecución:

1. Dar permisos de ejecución:
chmod +x ./scripts/bash/system_audit.sh

2. Ejecutar (Se recomienda sudo para ver logs protegidos):
sudo ./scripts/bash/system_audit.sh


===============================================================================

🛡️ CARACTERISTICAS DEL ANALISIS

===============================================================================


Historial de Comandos:

Extrae las últimas 5 líneas de .bash_history para ver actividad reciente.


Usuarios Recientes:

Busca carpetas en /home modificadas o creadas en las últimas 24 horas.


Privilegios de Root/Sudo:

Lista usuarios con UID 0 y aquellos pertenecientes al grupo sudoers.


Estado de Red (SSH):

Verifica si el servicio SSH está activo y lista todos los puertos en escucha.


Tareas Cron:

Muestra las tareas programadas (cronjobs) diarias y horarias del sistema.


Logs de Errores:

Extrae los últimos 5 errores críticos del Journal de sistema o Syslog.


===============================================================================

⚠️ ADVERTENCIAS Y CONSECUENCIAS EN ENTORNOS EMPRESARIALES

===============================================================================


Privilegios Elevados:

El script requiere 'sudo' para leer logs de seguridad y tareas de otros 
usuarios. Ejecutar scripts desconocidos como root siempre conlleva un riesgo.


Impacto en Producción:

El impacto de este script en la CPU es MINIMO (solo lectura). Sin embargo, 
en servidores con millones de archivos, el comando 'find /home' podría generar 
I/O de disco si no se limita correctamente.


Privacidad de Datos:

Al listar el historial de comandos (.bash_history), podrías exponer 
accidentalmente contraseñas que algún usuario haya escrito por error en 
la línea de comandos.


Falsos Positivos:

Una carpeta modificada en /home no siempre significa un intruso; puede ser 
una actualización automática de una aplicación o un servicio legítimo.


===============================================================================

💡 CONSEJOS TACTICOS

===============================================================================


Filtra los resultados: Si sospechas de un usuario concreto, redirige la 
salida a un archivo para analizarlo con 'grep'.

Automatización: Puedes programar este script en un cronjob para que te 
envíe un reporte diario de cambios en el sistema.

SSH Check: Si el script indica que SSH está activo pero no debería estarlo, 
podría ser un vector de entrada para un ataque de fuerza bruta.


===============================================================================

📚 RECURSOS ADICIONALES

===============================================================================


Linux Auditd: https://man7.org/linux/man-pages/man8/auditd.8.html

GTFOBins (PrivEsc): https://gtfobins.github.io/

Digital Ocean Hardening Guide: https://www.digitalocean.com/community/tutorials/


===============================================================================

💡 TIP FINAL

===============================================================================


En auditorías reales, siempre documenta la hora exacta en la que corres el 
script para evitar confundir tus propios comandos con los de un atacante.


Script creado por mrvcode

Uso exclusivo educativo y en entornos autorizados
