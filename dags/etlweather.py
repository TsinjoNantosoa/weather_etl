from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from datetime import datetime, timedelta
import json
import requests

# Constantes
LATITUDE = 51.5074
LONGITUDE = 0.1278
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'

default_args = {
    'owner': 'airflow',
    'start_date': datetime.utcnow() - timedelta(days=1)
}

with DAG(
    dag_id='weather_etl_pipeline',
    default_args=default_args,
    schedule='@daily',  
    catchup=False,
    description='ETL pipeline to extract weather data and store it in PostgreSQL'
) as dag:


#http://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=0.1278&current_weather=true
    @task()
    def extract_weather_data() -> dict:
        http_hook = HttpHook(http_conn_id=API_CONN_ID, method='GET')
        endpoint = f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'
        print(f"Requesting endpoint: {endpoint}")

        response = http_hook.run(endpoint)
        if response.status_code == 200:
            print("Données récupérées avec succès.")
            return response.json()
        else:
            raise Exception(f"Échec de la récupération des données : {response.status_code}")

    @task()
    def transform_weather_data(weather_data: dict) -> dict:
        current_weather = weather_data.get('current_weather', {})
        if not current_weather:
            raise ValueError("Aucune donnée 'current_weather' trouvée.")
        
        print("Données transformées :", current_weather)

        return {
            'latitude': LATITUDE,
            'longitude': LONGITUDE,
            'temperature': current_weather.get('temperature'),
            'windspeed': current_weather.get('windspeed'),
            'weathercode': current_weather.get('weathercode'),
            'time': current_weather.get('time')
        }

    @task()
    def load_weather_data(transformed_data: dict) -> None:
        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        with postgres_hook.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_data (
                        id SERIAL PRIMARY KEY,
                        latitude FLOAT,
                        longitude FLOAT,
                        temperature FLOAT,
                        windspeed FLOAT,
                        weathercode INT,
                        time TIMESTAMP
                    )
                """)
                cursor.execute("""
                    INSERT INTO weather_data (latitude, longitude, temperature, windspeed, weathercode, time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    transformed_data['latitude'],
                    transformed_data['longitude'],
                    transformed_data['temperature'],
                    transformed_data['windspeed'],
                    transformed_data['weathercode'],
                    transformed_data['time']
                ))
                conn.commit()
                print("Données insérées avec succès.")

    # Orchestration
    raw_data = extract_weather_data()
    transformed = transform_weather_data(raw_data)
    load_weather_data(transformed)



