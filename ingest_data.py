import os
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    
    # El Zoomcamp guarda el archivo descargado como 'output.csv'
    # Evaluamos si la URL es de un archivo comprimido
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'
    
    # Descargamos el archivo desde internet usando wget
    print(f"Descargando datos desde: {url}...")
    os.system(f"wget {url} -O {csv_name}")

    print("Iniciando el proceso de ingesta...")
    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}')
    
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')
    print("Estructura creada y primer bloque insertado.")

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            print(f"Bloque insertado exitosamente... tomó {t_end - t_start:.3f} segundos")
        except StopIteration:
            print("¡Proceso ETL finalizado con éxito!")
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingesta de datos CSV a PostgreSQL')

    parser.add_argument('--user', help='Usuario de postgres')
    parser.add_argument('--password', help='Contraseña de postgres')
    parser.add_argument('--host', help='Host de postgres')
    parser.add_argument('--port', help='Puerto de postgres')
    parser.add_argument('--db', help='Nombre de la base de datos')
    parser.add_argument('--table_name', help='Nombre de la tabla')
    # Cambiamos el argumento para que ahora pida una URL
    parser.add_argument('--url', help='URL del archivo CSV')

    args = parser.parse_args()
    main(args)