terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# 1. Definimos el recurso de la Imagen de Docker
resource "docker_image" "postgres_img" {
  name         = "postgres:13"
  keep_locally = false
}

# 2. Definimos el recurso del Contenedor (nuestro servidor de BD)
resource "docker_container" "postgres_db" {
  name  = "ny_taxi_postgres_tf"
  image = docker_image.postgres_img.image_id

  env = [
    "POSTGRES_USER=root",
    "POSTGRES_PASSWORD=root",
    "POSTGRES_DB=ny_taxi"
  ]

  ports {
    internal = 5432
    external = 5433
  }
}