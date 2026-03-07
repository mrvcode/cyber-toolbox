# =================================================================
# SCRIPT DE INSTALACIÓN Y AUDITORÍA INTEGRADO (VERSIÓN FINAL)
# =================================================================

# 1. VERIFICACIÓN DE PRIVILEGIOS
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "[!] ERROR: Debes ejecutar este script como ADMINISTRADOR." -ForegroundColor Red
    return
}

# 2. DETECTAR IDIOMA DEL SISTEMA (SOLO PARA INFORMACIÓN DURANTE INSTALACIÓN)
$culture = Get-Culture
$adminGroupNameDetected = if ($culture.Name -eq "es-ES") { "Administradores" } else { "Administrators" }
Write-Host "[*] Sistema detectado: $($culture.DisplayName)" -ForegroundColor Cyan
Write-Host "[*] Grupo de administradores: $adminGroupNameDetected" -ForegroundColor Cyan

# 3. DEFINICIÓN DE LA FUNCIÓN DE AUDITORÍA (CORREGIDA PARA SER AUTOSUFICIENTE)
$AuditCode = @'
function MyAudit {
    <#
    .Description
    Auditoria avanzada de seguridad.
    Detecta persistencia, cambios en usuarios y activa telemetria de scripts.
    #>
    $OutputEncoding = [System.Text.Encoding]::UTF8

    # --- DETECTAR IDIOMA DENTRO DE LA FUNCIÓN (Para que no falle al reiniciar) ---
    $culture = Get-Culture
    $adminGroupName = if ($culture.Name -eq "es-ES") { "Administradores" } else { "Administrators" }

    # --- HARDENING DE LOGS ---
    try {
        $LogPath = "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
        if (!(Test-Path $LogPath)) { New-Item -Path $LogPath -Force | Out-Null }
        Set-ItemProperty -Path $LogPath -Name "EnableScriptBlockLogging" -Value 1 -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $LogPath -Name "EnableModuleLogging" -Value 1 -ErrorAction SilentlyContinue
    } catch {
        Write-Host "[!] No se pudo configurar el logging (permisos)" -ForegroundColor Yellow
    }

    # --- RECOLECCIÓN DE DATOS (CORREGIDA) ---
    $24HoursAgo = (Get-Date).AddDays(-1)
    
    # Usuarios recientes (con manejo de errores)
    $RecentUsers = @()
    try {
        $RecentUsers = Get-LocalUser -ErrorAction Stop | Where-Object { $_.PrincipalSource -eq "Local" } |
                       ForEach-Object {
                           $user = $_
                           $userPath = Join-Path $env:SystemDrive "Users\$($user.Name)"
                           $created = if (Test-Path $userPath) { 
                               (Get-Item $userPath -ErrorAction SilentlyContinue).CreationTime 
                           } else { $null }
                           
                           if ($created -and $created -gt $24HoursAgo) {
                               [PSCustomObject]@{
                                   Name = $user.Name
                                   Enabled = $user.Enabled
                                   Created = $created
                               }
                           }
                       }
    } catch {
        Write-Host "[!] No se pudo obtener lista de usuarios" -ForegroundColor Yellow
    }

    # Administradores (usando la variable local detectada)
    $Admins = @()
    try {
        $Admins = Get-LocalGroupMember -Group $adminGroupName -ErrorAction Stop | 
                  Select-Object Name, PrincipalSource
    } catch {
        try {
            # Intento con el nombre en inglés por si acaso
            $Admins = Get-LocalGroupMember -Group "Administrators" -ErrorAction Stop | 
                      Select-Object Name, PrincipalSource
        } catch {
            Write-Host "[!] No se pudo obtener grupos de administradores" -ForegroundColor Yellow
        }
    }

    # Servicios críticos
    $CriticalServices = @()
    try {
        $CriticalServices = Get-Service -Name "WinRM", "sshd", "TermService" -ErrorAction SilentlyContinue | 
                            Select-Object Name, Status, StartType
    } catch {}

    # Reglas de firewall
    $FirewallRules = @()
    try {
        $FirewallRules = Get-NetFirewallRule -ErrorAction SilentlyContinue | 
                         Where-Object { $_.DisplayName -like "*WinRM*" -or $_.DisplayName -like "*Escritorio remoto*" -or $_.DisplayName -like "*RDP*" } | 
                         Select-Object DisplayName, Enabled, Direction, Action
    } catch {}

    # Tareas programadas
    $Tasks = @()
    try {
        $Tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | 
                 Where-Object { $_.State -eq "Ready" } | 
                 Select-Object TaskName, TaskPath -First 10
    } catch {}

    # Logs de PowerShell (con manejo de errores)
    $PSLogs = @()
    try {
        $PSLogs = Get-WinEvent -FilterHashtable @{
            LogName='Microsoft-Windows-PowerShell/Operational'
            ID=4104
            StartTime=$24HoursAgo
        } -MaxEvents 5 -ErrorAction Stop | 
        ForEach-Object {
            $msg = $_.Message
            $snippet = if ($msg.Length -gt 100) { 
                $msg.Substring(0, 100) + "..." 
            } else { 
                $msg 
            }
            [PSCustomObject]@{
                TimeCreated = $_.TimeCreated
                ScriptSnippet = $snippet
            }
        }
    } catch {
        Write-Host "[!] No hay logs de PowerShell disponibles" -ForegroundColor Yellow
    }

    # --- SALIDA VISUAL ---
    Clear-Host
    Write-Host "`n[!] WINDOWS SECURITY AUDIT TOOL [!]" -ForegroundColor White -BackgroundColor DarkBlue
    Write-Host "----------------------------------------------------" -ForegroundColor Gray

    Write-Host "`n[?] AUDITORÍA DE COMANDOS (Logs PS últimas 24h):" -ForegroundColor Magenta
    if ($PSLogs) {
        $PSLogs | Format-Table -AutoSize
    } else { Write-Host "[+] No hay actividad de scripts reciente." -ForegroundColor Green }

    if ($RecentUsers -and $RecentUsers.Count -gt 0) {
        Write-Host "`n[!] ALERTA: Usuarios creados recientemente:" -ForegroundColor Red
        $RecentUsers | Format-Table -AutoSize
    } else { Write-Host "`n[+] No se han detectado usuarios nuevos (24h)." -ForegroundColor Green }

    Write-Host "`n[+] Grupos de Administradores:" -ForegroundColor Cyan
    if ($Admins) { $Admins | Format-Table -AutoSize } else { Write-Host "No disponible" -ForegroundColor Gray }

    Write-Host "[+] Estado de Red y Firewall (RDP/WinRM):" -ForegroundColor Yellow
    if ($FirewallRules) { $FirewallRules | Format-Table -AutoSize } else { Write-Host "No disponible" -ForegroundColor Gray }
    if ($CriticalServices) { $CriticalServices | Format-Table -AutoSize } else { Write-Host "No disponible" -ForegroundColor Gray }

    Write-Host "[+] Tareas programadas activas (Top 10):" -ForegroundColor Gray
    if ($Tasks) { $Tasks | Format-Table -AutoSize } else { Write-Host "No disponible" -ForegroundColor Gray }

    Write-Host "`n[!] Auditoría completada." -ForegroundColor White -BackgroundColor DarkGreen
}
'@

# 4. DETECTAR VERSIÓN DE POWERSHELL Y CREAR MÓDULO
$psVersion = $PSVersionTable.PSVersion.Major
if ($psVersion -ge 6) {
    $ModuleDir = "$HOME\Documents\PowerShell\Modules\MyAudit"
    Write-Host "[*] PowerShell Core $psVersion detectado" -ForegroundColor Cyan
} else {
    $ModuleDir = "$HOME\Documents\WindowsPowerShell\Modules\MyAudit"
    Write-Host "[*] PowerShell $psVersion detectado" -ForegroundColor Cyan
}

# Crear módulo con try/catch
try {
    if (!(Test-Path $ModuleDir)) {
        New-Item -Path $ModuleDir -ItemType Directory -Force | Out-Null
        Write-Host "[+] Carpeta de modulo creada." -ForegroundColor Green
    }

    $ModuleFile = "$ModuleDir\MyAudit.psm1"
    $AuditCode | Out-File -FilePath $ModuleFile -Encoding UTF8 -Force
    Write-Host "[+] Archivo MyAudit.psm1 actualizado." -ForegroundColor Green
} catch {
    Write-Host "[!] ERROR creando módulo: $_" -ForegroundColor Red
    return
}

# 5. CONFIGURACIÓN DEL PERFIL
try {
    if (!(Test-Path $PROFILE)) {
        New-Item -Path $PROFILE -ItemType File -Force | Out-Null
        Write-Host "[+] Archivo de perfil creado." -ForegroundColor Green
    }

    $ProfileContent = Get-Content $PROFILE -ErrorAction Stop
    if ($ProfileContent -notcontains "Import-Module MyAudit -Force") {
        Add-Content -Path $PROFILE -Value "`nImport-Module MyAudit -Force"
        Write-Host "[+] Importación añadida al perfil permanentemente." -ForegroundColor Green
    } else {
        Write-Host "[*] El perfil ya contiene la configuración necesaria." -ForegroundColor Gray
    }
} catch {
    Write-Host "[!] No se pudo modificar el perfil: $_" -ForegroundColor Yellow
}

# 6. POLÍTICA DE EJECUCIÓN
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "[+] Política de ejecución configurada." -ForegroundColor Green
} catch {
    Write-Host "[!] No se pudo cambiar la política de ejecución" -ForegroundColor Yellow
}

# 7. EJECUCIÓN INMEDIATA
Write-Host "`n[*] Instalación finalizada. Iniciando auditoria..." -ForegroundColor Cyan
Start-Sleep -Seconds 1

# Cargar la función en la sesión actual
try {
    Import-Module MyAudit -Force -ErrorAction Stop
    MyAudit
} catch {
    Write-Host "[!] Error al ejecutar la auditoría: $_" -ForegroundColor Red
}
