from fastapi import FastAPI, BackgroundTasks
import asyncio
from utils.OpenMeteoWeather import OpenMeteoWeather
import json

import json
import pandas as pd

import datetime

def clean_json(data):
    # convert datetime to isoformat
    for i in range(len(data)):
        for key, value in data[i].items():
            if isinstance(value, datetime.datetime):
                data[i][key] = value.isoformat(timespec='microseconds')
    return json.loads(json.dumps(data, allow_nan=False))



app = FastAPI(root_path="/api/v1")

# Globale Variable für Wetterdaten
weather_data = {}

async def update_weather():
    """ Aktualisiert die Wetterdaten alle 10 Sekunden """
    global weather_data
    while True:
        latitude = 52.52
        longitude = 13.405
        start_datetime = "2025-01-01"
        end_datetime = "2025-02-01"

        omw = OpenMeteoWeather(latitude=latitude, 
                               longitude=longitude, 
                               start_date=start_datetime, 
                               end_date=end_datetime
                               )
        df_omw = omw.get_weather_dataframe().dropna(axis=1, how='any')
        df_omw = df_omw.reset_index(drop=True)
        weather_data = df_omw.to_dict(orient='records')  # Als JSON-ähnliches Dict speichern
        #print(weather_data)
        weather_data = clean_json(weather_data)
        
        print("Wetterdaten aktualisiert")
        await asyncio.sleep(60)  # Alle 10 Sekunden neue Daten abrufen

@app.on_event("startup")
async def startup_event():
    """ Startet das Wetterupdate beim Hochfahren der API """
    asyncio.create_task(update_weather())

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the weather API",
        "endpoints": {
            "/weather/": "Get the latest weather data"
        }
    }

@app.get("/weather/")
def get_weather():
    """ Gibt die aktuellen Wetterdaten zurück """
    return weather_data
