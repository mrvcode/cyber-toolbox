# 📊 Apache Bench - Test de Rendimiento

**Nivel:** 🟢 Básico  
**Categoría:** Testing/Performance  
**Herramienta:** Apache Bench (`ab`)

---

## 📋 Descripción

Este script automatiza pruebas de rendimiento HTTP usando Apache Bench (`ab`). 
Lanza un número configurable de peticiones contra un servidor web y recoge 
métricas clave como:
- Requests por segundo
- Tiempo de respuesta
- Tasa de transferencia
- Latencia percentil

## 🎯 ¿Para qué sirve?

- **Testing de servidores web**: Medir cuántas peticiones puede manejar tu servidor
- **Comparativa de configuraciones**: Probar diferentes setups (nginx vs apache, etc.)
- **Detección de cuellos de botella**: Identificar límites de rendimiento
- **Aprendizaje**: Entender métricas de rendimiento web

## 📦 Requisitos

```bash
# Instalar Apache Bench (si no lo tienes)
# Debian/Ubuntu:
sudo apt install apache2-utils

# RHEL/CentOS:
sudo yum install httpd-tools

# macOS (ya viene con ab):
# No requiere instalación
