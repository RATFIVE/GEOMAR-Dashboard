import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://marine-api.open-meteo.com/v1/marine"
params = {
	"latitude": 54.3323,
	"longitude": 10.1519,
	"hourly": ["sea_surface_temperature", "sea_level_height_msl"],
	"start_date": "2024-05-08",
	"end_date": "2025-03-31"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

							# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_sea_surface_temperature = hourly.Variables(0).ValuesAsNumpy()
hourly_sea_level_height_msl = hourly.Variables(1).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["sea_surface_temperature"] = hourly_sea_surface_temperature
hourly_data["sea_level_height_msl"] = hourly_sea_level_height_msl

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

