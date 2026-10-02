FROM python:3.9

# Instalamos la herramienta de descarga (wget) en el sistema operativo Linux del contenedor
RUN apt-get update && apt-get install -y wget

RUN pip install pandas sqlalchemy psycopg2-binary

WORKDIR /app

# Solo copiamos el script, ¡adiós a los datos pesados dentro de la imagen!
COPY ingest_data.py ingest_data.py 

ENTRYPOINT [ "python", "ingest_data.py" ]