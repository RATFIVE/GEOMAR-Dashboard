import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

class OpenMeteoMarine:
    def __init__(self, cache_file='.cache', cache_expiry=3600, retries=5, backoff_factor=0.2):
        self.cache_session = requests_cache.CachedSession(cache_file, expire_after=cache_expiry)
        self.retry_session = retry(self.cache_session, retries=retries, backoff_factor=backoff_factor)
        self.client = openmeteo_requests.Client(session=self.retry_session)

    def fetch_marine_data(self, latitude, longitude, start_date, end_date):
        url = "https://marine-api.open-meteo.com/v1/marine"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["sea_surface_temperature", "sea_level_height_msl"],
            "start_date": start_date,
            "end_date": end_date
        }
        
        responses = self.client.weather_api(url, params=params)
        response = responses[0]
        
        # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation {response.Elevation()} m asl")
        # print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
        
        return self.process_hourly_data(response)

    def process_hourly_data(self, response):
        hourly = response.Hourly()
        hourly_sea_surface_temperature = hourly.Variables(0).ValuesAsNumpy()
        hourly_sea_level_height_msl = hourly.Variables(1).ValuesAsNumpy()
        
        hourly_data = {
            "time": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "sea_surface_temperature": hourly_sea_surface_temperature,
            "sea_level_height_msl": hourly_sea_level_height_msl
        }
        
        return pd.DataFrame(data=hourly_data)

# Beispielaufruf
if __name__ == "__main__":
    client = OpenMeteoMarine()
    df = client.fetch_marine_data(latitude=54.3323, longitude=10.1519, start_date="2024-05-08", end_date="2025-03-31")
    print(df)
