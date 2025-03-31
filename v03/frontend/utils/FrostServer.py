import json

import pandas as pd
import requests
import datetime

# import plotly.express as px
# import plotly.graph_objects as go

pd.set_option("display.max_columns", None)  # Zeigt alle Spalten an
#pd.set_option("display.max_rows", None)  # Optional: Zeigt alle Zeilen an
pd.set_option("display.width", None)  # Passt die Breite dynamisch an
pd.set_option(
    "display.expand_frame_repr", False
)  # Verhindert Zeilenumbrüche bei breiten DataFrames


class FrostServer:
    def __init__(
        self,
        url="https://timeseries.geomar.de/soop/FROST-Server/v1.1/",
        thing="Things(3)",  # T-Box
    ):
        self.url = url
        self.thing = thing

    def get_content(self, url):
        response = requests.get(url)
        content = response.text
        return json.loads(content)

    def get_datastream_url(self):
        content = self.get_content(self.url + self.thing)
        datastream_url = content["Datastreams@iot.navigationLink"]
        return datastream_url

    def get_position_url(self):
        content = self.get_content(self.url + self.thing)
        position_url = content["Locations@iot.navigationLink"]
        return position_url

    def get_observations_url(self):
        datastream_url = self.get_datastream_url()
        content_datastream = self.get_content(datastream_url)
        observation_url = content_datastream["value"][0][
            "Observations@iot.navigationLink"
        ]
        return observation_url

    def get_thing_name(self):
        content = self.get_content(self.url + self.thing)
        name_url = content["name"]
        return name_url

    def print_content(self, content):
        return print(json.dumps(content, indent=4, ensure_ascii=False))

    def get_all_observations(self, limit_per_page=10000):
        observation_url = self.get_observations_url()

        # Zeitfilter: Letztes Jahr
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)

        # Formatieren der Datumswerte für den API-Filter (ISO 8601)
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")


        params = {
            "$filter": f"phenomenonTime ge {start_date_str} and phenomenonTime le {end_date_str}",
            "$top": {limit_per_page},  # Limit to 1000 observations per page
            "$orderby": "phenomenonTime asc",  # Sort by phenomenonTime in ascending order
        }
        
        # Anfrage senden
        response = requests.get(observation_url, params=params)

        # Überprüfung der Antwort
        if response.status_code == 200:
            data = response.json()  # JSON-Daten extrahieren
            print("Daten empfangen:", len(data.get("value", [])), "Einträge")
        else:
            print("Fehler:", response.status_code, response.text)


        df = pd.DataFrame(data["value"])
        df["phenomenonTime"] = pd.to_datetime(df["phenomenonTime"])
        df["resultTime"] = pd.to_datetime(df["resultTime"])

        df["result"] = df["result"].astype(float) # convert result to float
        df.rename(
        columns={"phenomenonTime": "time", "result": "water_temperatur"}, inplace=True
        )

        df = df[["time", "water_temperatur"]]

        df["time"] = df["time"].dt.tz_localize(None)
        df.sort_values("time", inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)

        return df



if __name__ == "__main__":
    server = FrostServer(thing="Things(3)")
    observation_url = server.get_observations_url()
    content = server.get_content(observation_url)
    df_obs = server.get_all_observations(limit_per_page=10000)

    

    print(df_obs.head(3))
    print(df_obs.tail(3))
    print(df_obs.describe())
    print(df_obs.info())
