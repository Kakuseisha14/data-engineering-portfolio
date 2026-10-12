# 🚀 Módulo 2: Infraestructura como Código (IaC) con Terraform y Docker

## 🧠 Concepto Clave: Automatización y Gestión de Estado (State)
La gestión manual de infraestructura (*ClickOps*) es inescalable y propensa a errores. Este módulo implementa **Infraestructura como Código (IaC)** utilizando Terraform. El objetivo es provisionar, auditar y destruir recursos de manera predecible, utilizando el archivo de estado (`terraform.tfstate`) como única fuente de verdad.

---

## 🏗️ Arquitectura y Decisiones Técnicas

En esta fase, reemplazamos el uso estático de `docker-compose` por código HCL (HashiCorp Configuration Language) para gestionar el motor local de Docker.

### 1. El Proveedor (Provider) Agnóstico (`main.tf`)
Terraform fue configurado para interactuar con el socket interno de Docker en Linux, demostrando su capacidad agnóstica para manejar múltiples entornos (locales o en la nube):

*   **Configuración del Provider (`kreuzwerker/docker`):** Se definió el plugin necesario para que Terraform traduzca las instrucciones HCL a comandos que el motor de Docker (`unix:///var/run/docker.sock`) pueda ejecutar nativamente.

### 2. Definición Dinámica de Recursos
Se programaron recursos interdependientes para garantizar un orden de ejecución lógico sin necesidad de scripts secuenciales:

*   **Bloque `docker_image`:** Automatiza el proceso de `docker pull`, descargando la imagen de `postgres:13` desde el registro oficial.
*   **Bloque `docker_container`:** Despliega el servidor de base de datos inyectando variables de entorno seguras (`POSTGRES_DB`, `POSTGRES_USER`).
*   **Árbol de Dependencias Implícito:** El contenedor hace referencia directa al ID de la imagen (`image = docker_image.postgres_img.image_id`). Terraform calcula matemáticamente que no puede levantar el contenedor hasta que la imagen esté completamente descargada, manejando la orquestación automáticamente.

---

## 🛡️ El Ciclo de Vida de IaC (Init, Plan, Apply, Destroy)

El aprovisionamiento se gestiona estrictamente bajo el estándar de la industria, asegurando auditoría previa a cualquier cambio:

1.  **`terraform init`:** Inicialización del backend y descarga de plugins. *(Se superaron bloqueos geopolíticos de red ruteando el tráfico de la terminal a través de una VPN a nivel de sistema operativo para alcanzar `registry.terraform.io`).*
2.  **`terraform plan`:** Auditoría en seco (Dry-run). Se verificaron los deltas de infraestructura (ej. `Plan: 2 to add...`) antes de comprometer recursos de cómputo.
3.  **`terraform apply`:** Ejecución de la arquitectura. Terraform consolida los metadatos de los contenedores creados (como IDs criptográficos y puertos) en su archivo `.tfstate`.
4.  **`terraform destroy`:** Limpieza absoluta del entorno. En lugar de borrar contenedores manualmente, Terraform lee su estado y desmantela la arquitectura limpiamente, evitando contenedores huérfanos y liberando puertos.

---

## 🔒 Estándares de Seguridad en Control de Versiones

Para mantener las credenciales y el estado de la infraestructura seguros, se configuró un archivo `.gitignore` estricto en este módulo:

*   Se excluye la carpeta oculta `.terraform/` (binarios de plugins pesados).
*   Se bloquean los archivos `*.tfstate` y `*.tfstate.backup`. **El estado de Terraform nunca debe exponerse en GitHub**, ya que puede contener variables de entorno sensibles y metadatos críticos de la infraestructura en texto plano.