
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from utils.Copernicus import AdvancedCopernicus
import json 
from utils.OpenMeteoWeather import OpenMeteoWeather
import datetime


ac = AdvancedCopernicus() 


def get_json_data(file):
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    return data

marinas = get_json_data('../data/marinas.json')

marinas


OUTPUT_FILENAME = "output.nc"
START_DATETIME = "2023-05-01T00:00:00Z"
END_DATETIME = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
RADIUS = 0.1

for marina in marinas:
    marina_name = marina['name']
    marina_latitude = marina['location']['latitude']
    marina_longitude = marina['location']['longitude']

    minimum_longitude = marina_longitude - RADIUS
    maximum_longitude = marina_longitude + RADIUS
    minimum_latitude = marina_latitude - RADIUS
    maximum_latitude = marina_latitude + RADIUS



    marina_data = ac.get_subset(
        dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
        dataset_version="202406",
        variables=["so", "thetao", "vo", "zos", "uo"], 
        minimum_longitude=minimum_longitude,
        maximum_longitude=maximum_longitude,
        minimum_latitude=minimum_latitude,
        maximum_latitude=maximum_latitude,
        start_datetime=START_DATETIME,
        end_datetime=END_DATETIME,
        minimum_depth=0.49402499198913574,
        maximum_depth=0.49402499198913574,
        coordinates_selection_method="strict-inside",
        disable_progress_bar=False,
        output_filename=OUTPUT_FILENAME
        )
    
    ac.delete_dataset(OUTPUT_FILENAME)

    marina_df = marina_data.to_dataframe().reset_index()
    marina_df = marina_df.dropna(axis=0, how='all')
    marina_df_grouped = marina_df.groupby('time').mean()
    marina_df_grouped.sort_values(by='time', ascending=False, inplace=True)
    marina_df_grouped.reset_index(inplace=True)

    omw = OpenMeteoWeather(
            latitude=marina_latitude, 
            longitude=marina_longitude, 
            start_date=START_DATETIME.split('T')[0], 
            end_date=END_DATETIME.split('T')[0]
            )
    df_omw = omw.get_weather_dataframe()
    cols = ['time', 'wind_speed_10m', 'wind_direction_10m', 'temperature_2m', 'pressure_msl', 'relative_humidity_2m']
    df_omw = df_omw[cols]
    df_omw["time"] = pd.to_datetime(df_omw["time"]).dt.tz_localize(None)
    df_omw.dropna(axis=1, how='all', inplace=True)
    df_omw.dropna(axis=0, how='any', inplace=True)
    df_omw.sort_values(by='time', ascending=False, inplace=True)
    df_omw.reset_index(drop=True, inplace=True)
    # Sicherstellen, dass der Schlüssel 'measurement' existiert
    
    def insert_measurement(df:pd.DataFrame, data:dict, key:str, name:str):
        if 'measurement' not in data:
            data['measurement'] = {}

        if key not in df.columns:
            return print(f"Key {key} not in dataframe")
        
        df = df.loc[:, ['time', key]].rename(columns={key: 'values'})
        data['measurement'][name] = df.loc[:, ['time', 'values']].to_dict(orient='list')


    insert_measurement(marina_df_grouped, marina, key='thetao', name='water_temperature')
    insert_measurement(marina_df_grouped, marina, key='zos', name='water_height')
    insert_measurement(df_omw, marina, key='wind_speed_10m', name='wind_speed')
    insert_measurement(df_omw, marina, key='wind_direction_10m', name='wind_direction')
    insert_measurement(df_omw, marina, key='temperature_2m', name='air_temperature')
    insert_measurement(df_omw, marina, key='pressure_msl', name='air_pressure')
    insert_measurement(df_omw, marina, key='relative_humidity_2m', name='air_humidity')
    




app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/data")
def read_marinas():
    return JSONResponse(content=jsonable_encoder(marinas), media_type="application/json")

@app.get("/settings")
def read_settings():
    return {"settings": "settings"}




