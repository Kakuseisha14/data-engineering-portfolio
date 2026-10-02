# 🚀 Módulo 1: Dockerización y Parametrización de Ingesta (ETL)

## 🧠 Concepto Clave: Arquitectura Stateless y Agnóstica
Un contenedor en producción debe ser **Stateless** (sin estado) y **Agnóstico**. Esto significa que no debe almacenar datos masivos en su interior (solo debe contener código) y debe poder conectarse a diferentes entornos (Desarrollo, Pruebas, Producción) sin tener que modificar o recompilar el código fuente.

---

## 🏗️ Justificación de Arquitectura y Código

Para cumplir con el estándar de producción, el pipeline se construyó tomando las siguientes decisiones técnicas:

### 1. El Motor de Ingesta (`ingest_data.py`)
El script de Python dejó de ser un archivo estático para convertirse en una herramienta dinámica de línea de comandos.

*   **Parametrización Dinámica (`argparse`):** Dejar credenciales (`root`), nombres de bases de datos o rutas fijas (*hardcoded*) es una mala práctica de seguridad. Se implementó `argparse` para actuar como un "recepcionista", obligando al usuario a inyectar variables (`--user`, `--password`, `--url`) desde la terminal.
*   **Descarga Efímera al Vuelo (`os.system("wget...")`):** En lugar de leer un archivo local, el script descarga los datos desde internet hacia el contenedor justo antes de procesarlos. Al finalizar y apagarse el contenedor, los datos se destruyen, manteniendo el entorno limpio.
*   **Manejo de Binarios GZIP (`if url.endswith('.csv.gz'):`):** Las fuentes de Big Data suelen comprimir los archivos. Se añadió lógica condicional para detectar la extensión de la URL, permitiendo que `pandas` identifique y descomprima el binario al vuelo sin corromper la lectura.
*   **Procesamiento por Lotes (`chunksize=100000`):** Se utilizó un iterador para subir los datos a PostgreSQL en bloques de 100,000 registros, evitando el desbordamiento de memoria RAM (OOM) que ocurriría al intentar cargar millones de filas simultáneamente.

### 2. El Entorno Aislado (`Dockerfile`)
La imagen de Docker fue optimizada para ser ultraligera.

*   **Imagen Base Actualizada (`FROM python:3.9`):** Se abandonaron versiones con repositorios EOL (End of Life) para garantizar la compatibilidad de actualizaciones del sistema.
*   **Dependencias de Red Nativas (`RUN apt-get install -y wget`):** Se inyectaron herramientas de red a nivel del sistema operativo Linux dentro del contenedor para habilitar la descarga de datos externos.
*   **Ausencia de Datos Locales:** La instrucción `COPY` se limitó estrictamente al archivo `ingest_data.py`. No se copian archivos CSV masivos dentro de la imagen, reduciendo el peso del contenedor de gigabytes a solo unos pocos megabytes.

---

## 🐛 Troubleshooting (Resolución de Errores Comunes)

Durante la construcción del pipeline se superaron los siguientes bloqueos de infraestructura:

### Error 1: `404 Not Found / does not have a Release file` (Al construir Docker)
*   **Causa:** La imagen base inicial (`python:3.9.1`) utilizaba una versión antigua de Linux (Debian Buster) cuyos repositorios de internet fueron archivados por llegar a su fin de vida (EOL). Al intentar hacer `apt-get update`, el contenedor no encontraba los servidores.
*   **Solución:** Se actualizó la etiqueta base del Dockerfile a `FROM python:3.9`, obligando a Docker a descargar una distribución de Linux moderna y con repositorios activos.

### Error 2: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b` (Al leer datos)
*   **Causa:** La URL proporcionaba un archivo comprimido (`.csv.gz`), pero el script lo estaba nombrando erróneamente con extensión `.csv` normal. Cuando Pandas intentó leerlo asumiendo texto plano UTF-8, colapsó al encontrarse con datos binarios comprimidos.
*   **Solución:** Se implementó el control de flujo para guardar el archivo con la extensión `.gz` correcta. Pandas es lo suficientemente inteligente como para detectar esta firma y descomprimir el archivo "al vuelo" mientras lo lee.