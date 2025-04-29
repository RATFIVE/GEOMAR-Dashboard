import json

import pandas as pd
import requests
import datetime


pd.set_option("display.max_columns", None)  # Zeigt alle Spalten an


class FrostServer:
    def __init__(
        self,
        url="https://timeseries.geomar.de/soop/FROST-Server/v1.1/",
        thing="Things(3)",  # T-Box
    ):
        self.url = url
        self.thing = thing

    def get_content(self, url:str):
        """Fetches content from the specified URL.

        Args:
            url (str): The URL to fetch content from.

        Returns:
            dict: The parsed JSON content from the response.
        """
        response = requests.get(url)
        content = response.text
        return json.loads(content)

    def get_datastream_url(self):
        """Get the datastream url from the thing

        Returns:
            str: The URL of the datastream associated with the thing.
        """
        content = self.get_content(self.url + self.thing)
        datastream_url = content["Datastreams@iot.navigationLink"]
        return datastream_url

    def get_position_url(self):
        """Get the position URL associated with the thing.

        Returns:
            str: The URL of the position associated with the thing.
        """
        content = self.get_content(self.url + self.thing)
        position_url = content["Locations@iot.navigationLink"]
        return position_url

    def get_observations_url(self):
        """Get the observation url from the datastream

        Returns:
            str: The URL of the observations associated with the datastream.
        """
        datastream_url = self.get_datastream_url()
        content_datastream = self.get_content(datastream_url)
        observation_url = content_datastream["value"][0]["Observations@iot.navigationLink"]
        return observation_url

    def get_thing_name(self):
        """Get the name of the thing associated with the FrostServer instance.

        Returns:
            str: The name of the thing. E.g., "Badesteg Reventlou"
        """
        content = self.get_content(self.url + self.thing)
        name_url = content["name"]
        return name_url

    def print_content(self, content:str):
        """This function prints the content in a readable format.
        It uses the json.dumps() method to format the content with indentation and ensures that
        non-ASCII characters are displayed correctly.
        The function is useful for debugging or logging purposes, allowing you to see the structure
        and content of the JSON data in a more human-readable way.

        Args:
            content (str): The JSON content to be printed in a readable format.

        Returns:
            None: This function does not return a value.
        """
        return print(json.dumps(content, indent=4, ensure_ascii=False))

    def get_all_observations(self, last_n_days:int=365, col_name:str="water_temperatur"):

        """
        Fetches observation data from the past `last_n_days` via an API and returns it as a pandas DataFrame.

        The function constructs a time-based filter to retrieve hourly observation data from the API
        endpoint provided by `self.get_observations_url()`. The retrieved data is limited to one value 
        per hour over the specified number of days (default is 365 days). It processes the API response, 
        converts timestamps to datetime, renames columns, and returns a cleaned DataFrame.

        Parameters:
        ----------
        last_n_days : int, optional
            Number of days in the past to retrieve data for. Defaults to 365 days.
        col_name : str, optional
            Name of the column that stores the observation results (default: "water_temperatur").

        Returns:
        -------
        pd.DataFrame
            A DataFrame containing two columns:
            - "time": Timestamps of the observations (timezone-naive, sorted in descending order).
            - col_name: The corresponding float values of the observed phenomenon.
        """

        limit_per_page = last_n_days * 24 # hourly data and 24 hors per day, change this if data is in different time step
        observation_url = self.get_observations_url()

        # Zeitfilter: Letztes Jahr
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=last_n_days)

        # Formatieren der Datumswerte für den API-Filter (ISO 8601)
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "$filter": f"phenomenonTime ge {start_date_str} and phenomenonTime le {end_date_str}", # Filter data within the start and end date
            "$top": {limit_per_page},  # Limit to 1000 observations per page
            "$orderby": "phenomenonTime asc",  # Sort by phenomenonTime in ascending order
        }

        # Send request to the API
        response = requests.get(observation_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            print("Daten empfangen:", len(data.get("value", [])), "Einträge")
        else:
            # If Error, print the status code and error message
            print("Fehler:", response.status_code, response.text)
            return None
        
        # Convert the JSON data to a pandas DataFrame
        df = pd.DataFrame(data["value"])
        df["phenomenonTime"] = pd.to_datetime(df["phenomenonTime"])
        df["resultTime"] = pd.to_datetime(df["resultTime"])

        df["result"] = df["result"].astype(float)  # convert result to float
        df.rename(
            columns={"phenomenonTime": "time", "result": col_name}, # Rename columns
            inplace=True,
        )

        df = df[["time", col_name]] # keep only the relevant columns

        df["time"] = df["time"].dt.tz_localize(None) # remove timezone information
        df.sort_values("time", inplace=True, ascending=False) # sort by time in descending order
        df.reset_index(drop=True, inplace=True)

        return df





if __name__ == "__main__":

    server = FrostServer(thing="Things(3)")
    df_obs = server.get_all_observations(last_n_days=365, col_name="water_temperatur")

    print("\nHead:")
    print(df_obs.head(3))

    print("\nTail:")
    print(df_obs.tail(3))

    print("\nDescribe:")
    print(df_obs.describe())
    print("\nInfo:")

    print(df_obs.info())
    print("\nThing Name:")

    print(server.get_thing_name())
    print("\nPrint the Position:")
    print(server.print_content(server.get_content(server.get_position_url())))


    # print('\n\n')
    # content = server.get_observations_url()
    # content = server.get_content(url=content)
    # print(server.print_content(content=content))
