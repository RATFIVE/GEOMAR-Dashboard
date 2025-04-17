import pandas as pd
import numpy as np
from utils.OpenMeteoWeather import OpenMeteoWeather
from utils.OpenMeteoMarine import OpenMeteoMarine
from utils.FrostServer import FrostServer
import datetime
import json

client_marine = OpenMeteoMarine()


# Konvertiere Timestamps in Strings
def convert_timestamps(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj


def get_json_data(file):
    with open(file, encoding="utf-8") as f:
        data = json.load(f)
    return data


def process_data(df: pd.DataFrame):
    df["time"] = pd.to_datetime(df["time"]).dt.tz_localize(None)
    df.dropna(axis=1, how="all", inplace=True)
    df.dropna(axis=0, how="all", inplace=True)
    df.sort_values(by="time", inplace=True, ascending=False)
    df.reset_index(drop=True, inplace=True)

    return df


def insert_measurement(df: pd.DataFrame, data: dict, key: str, name: str):
    if "measurement" not in data:
        data["measurement"] = {}

    if key not in df.columns:
        return print(f"Key {key} not in dataframe")

    df = df.loc[:, ["time", key]].rename(columns={key: "values"})
    data["measurement"][name] = df.loc[:, ["time", "values"]].to_dict(orient="list")


def get_marina_data():
    marinas = get_json_data("v03/data/marinas.json")

    OUTPUT_FILENAME = "output.nc"

    # Get Start and End Date as 2025-01-1
    END_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
    START_DATE = datetime.datetime.now() - datetime.timedelta(days=365)
    START_DATE = START_DATE.strftime("%Y-%m-%d")

    for i, marina in enumerate(marinas):
        marina_name = marina["name"]
        marina_latitude = marina["location"]["latitude"]
        marina_longitude = marina["location"]["longitude"]

        if marina["name"] == "Badesteg Reventlou":
            print(f"Processing Marina: {marina_name}")

            server = FrostServer(thing="Things(3)")
            df_obs = server.get_all_observations()

            df_marine = client_marine.fetch_marine_data(
                latitude=marina_latitude,
                longitude=marina_longitude,
                start_date=START_DATE,
                end_date=END_DATE,
            )

            df_weaher = OpenMeteoWeather(
                latitude=marina_latitude,
                longitude=marina_longitude,
                start_date=START_DATE,
                end_date=END_DATE,
            ).get_weather_dataframe()

            # Select only the relevant columns
            cols = [
                "time",
                "wind_speed_10m",
                "wind_direction_10m",
                "temperature_2m",
                "pressure_msl",
                "relative_humidity_2m",
            ]
            df_weaher = df_weaher[cols]

            # Merge the two dataframes
            df = pd.merge(df_marine, df_weaher, on="time", how="inner")
            df = process_data(df)

            # Filter data to just until today
            df = df.loc[df["time"] <= datetime.datetime.now()]

            print(df.describe())

            # Insert the observation data from OpenMeteo
            insert_measurement(
                df, marina, key="sea_level_height_msl", name="water_height"
            )
            insert_measurement(df, marina, key="wind_speed_10m", name="wind_speed")
            insert_measurement(
                df, marina, key="wind_direction_10m", name="wind_direction"
            )
            insert_measurement(df, marina, key="temperature_2m", name="air_temperature")
            insert_measurement(df, marina, key="pressure_msl", name="air_pressure")
            insert_measurement(
                df, marina, key="relative_humidity_2m", name="air_humidity"
            )

            # Insert the observation data from Frost Server
            insert_measurement(
                df_obs, marina, key="water_temperatur", name="water_temperature"
            )

            # print(marina['measurement']['water_temperature'])

        df_marine = client_marine.fetch_marine_data(
            latitude=marina_latitude,
            longitude=marina_longitude,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        df_weaher = OpenMeteoWeather(
            latitude=marina_latitude,
            longitude=marina_longitude,
            start_date=START_DATE,
            end_date=END_DATE,
        ).get_weather_dataframe()
        cols = [
            "time",
            "wind_speed_10m",
            "wind_direction_10m",
            "temperature_2m",
            "pressure_msl",
            "relative_humidity_2m",
        ]
        df_weaher = df_weaher[cols]

        # Merge the two dataframes
        df = pd.merge(df_marine, df_weaher, on="time", how="inner")
        df = process_data(df)
        # Filter data to just until today
        df = df.loc[df["time"] <= datetime.datetime.now()]

        insert_measurement(
            df, marina, key="sea_surface_temperature", name="water_temperature"
        )
        insert_measurement(df, marina, key="sea_level_height_msl", name="water_height")
        insert_measurement(df, marina, key="wind_speed_10m", name="wind_speed")
        insert_measurement(df, marina, key="wind_direction_10m", name="wind_direction")
        insert_measurement(df, marina, key="temperature_2m", name="air_temperature")
        insert_measurement(df, marina, key="pressure_msl", name="air_pressure")
        insert_measurement(df, marina, key="relative_humidity_2m", name="air_humidity")

    return marinas


if __name__ == "__main__":
    marinas = get_marina_data()

    print(json.dumps(marinas, default=convert_timestamps, indent=4))
