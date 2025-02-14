import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

class OpenMeteoWeather:
    def __init__(self, latitude, longitude, start_date, end_date):
        # Initialize parameters
        self.latitude = latitude
        self.longitude = longitude
        self.start_date = start_date
        self.end_date = end_date

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def fetch_weather_data(self):
        # Define the URL and parameters
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": [
                "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", 
                "precipitation_probability", "precipitation", "rain", "showers", "snowfall", "snow_depth",
                "weather_code", "pressure_msl", "surface_pressure", "cloud_cover", "cloud_cover_low", 
                "cloud_cover_mid", "cloud_cover_high", "visibility", "evapotranspiration", 
                "et0_fao_evapotranspiration", "vapour_pressure_deficit", "wind_speed_10m", "wind_speed_80m", 
                "wind_speed_120m", "wind_speed_180m", "wind_direction_10m", "wind_direction_80m", 
                "wind_direction_120m", "wind_direction_180m", "wind_gusts_10m", "temperature_80m", 
                "temperature_120m", "temperature_180m", "soil_temperature_0cm", "soil_temperature_6cm", 
                "soil_temperature_18cm", "soil_temperature_54cm", "soil_moisture_0_to_1cm", 
                "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", 
                "soil_moisture_27_to_81cm"
            ],
            "timezone": "Europe/Berlin",
            "start_date": self.start_date,
            "end_date": self.end_date
        }
        
        # Fetch data from Open-Meteo API
        responses = self.openmeteo.weather_api(url, params=params)
        return responses[0]

    def process_weather_data(self, response):
        # Process hourly data
        hourly = response.Hourly()
        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}

        variables = [
            "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", 
            "precipitation_probability", "precipitation", "rain", "showers", "snowfall", "snow_depth",
            "weather_code", "pressure_msl", "surface_pressure", "cloud_cover", "cloud_cover_low", 
            "cloud_cover_mid", "cloud_cover_high", "visibility", "evapotranspiration", 
            "et0_fao_evapotranspiration", "vapour_pressure_deficit", "wind_speed_10m", "wind_speed_80m", 
            "wind_speed_120m", "wind_speed_180m", "wind_direction_10m", "wind_direction_80m", 
            "wind_direction_120m", "wind_direction_180m", "wind_gusts_10m", "temperature_80m", 
            "temperature_120m", "temperature_180m", "soil_temperature_0cm", "soil_temperature_6cm", 
            "soil_temperature_18cm", "soil_temperature_54cm", "soil_moisture_0_to_1cm", 
            "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", 
            "soil_moisture_27_to_81cm"
        ]
        
        # Collecting each variable's data
        for idx, var in enumerate(variables):
            hourly_data[var] = hourly.Variables(idx).ValuesAsNumpy()

        # Convert to pandas DataFrame
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        return hourly_dataframe

    def get_weather_dataframe(self):
        # Fetch and process weather data
        response = self.fetch_weather_data()
        return self.process_weather_data(response)


if __name__ == "__main__":
    # Example usage:
    weather = OpenMeteoWeather(latitude=54.32, longitude=10.12, start_date="2025-02-01", end_date="2025-02-14")
    df = weather.get_weather_dataframe()
    print(df)
