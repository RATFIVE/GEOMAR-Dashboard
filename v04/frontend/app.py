import pandas as pd
import streamlit as st
from utils.Visualisations import ShowMap, LinePlot, Windrose
#from utils.data_loader import get_marina_data
import json
import plotly.graph_objects as go
from utils.FrostServer import FrostServerClient
from pprint import pprint
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import folium
import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_folium import st_folium



print("\nStarting Streamlit App...\n")


# Colors
# [theme]
# base="light"
# primaryColor="#ff6666"
# secondaryBackgroundColor="#78d278"
# textColor="#053246"

st.set_page_config(layout="wide", page_title="SOOP-Dashboard", page_icon=":shark:")

API_URL = "http://localhost:8000/data"


# Konvertiere Timestamps in Strings
def convert_timestamps(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj


class StreamlitApp:
    def __init__(self):
        pass



    def preload_data(self):


        """
        Returns list of dictionaries with the following structure:
        [
            {
            '@iot.id': 3,
            'datastreams': [{'description': 'WTemp c7991906-983b-4bf3-849f-14a139ffe4f3',
                            'id': 1,
                            'name': 'WTemp* measured by sensor '
                                    '*c7991906-983b-4bf3-849f-14a139ffe4f3*',
                            'observations': {'time': ['2025-05-13 10:36:59',
                                                        '2025-05-13 09:37:00',
                                                        '2025-05-13 08:37:04',
                                                        '2025-05-13 07:37:19',
                                                        '2025-05-13 06:37:09'],
                                                'values': [14.62,
                                                        14.37,
                                                        14.18,
                                                        14.0,
                                                        13.87]}}],
            'description': 'LoRaWan box for temperature at Kiel, Reventlou.',
            'locations': [{'@iot.id': 1,
                            '@iot.selfLink': 'https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)',
                            'HistoricalLocations@iot.navigationLink': 'https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)/HistoricalLocations',
                            'Things@iot.navigationLink': 'https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)/Things',
                            'description': 'Measuring point',
                            'encodingType': 'application/geo+json',
                            'location': {'coordinates': [10.1519, 54.3323],
                                        'type': 'Point'},
                            'name': 'Position lat 54.3323, lon 10.1519'}],
            'name': 'Badesteg Reventlou'
            },
        ]
        """   

        
        frost = FrostServerClient("https://timeseries.geomar.de/soop/FROST-Server/v1.1/")
        things = frost.list_things()
        print(f"Anzahl Things on Frost-Server: {len(things)}")

        thing_dicts = [] 
        for thing in things:

            skip_list = ['TGPS Box Ship', 'Kitchen', 'Kitchen #2', 'Test Box', 'SOOP_Fridtjof_Nansen']
            if thing["name"] in skip_list:
               continue

            ######################################################################################################
            # Get Locations of the Thing
            ######################################################################################################

            locations = frost.get_entities(entity_type=f'Things({thing["@iot.id"]})/Locations')
            
            # Check in Datastreas for locations if not found in Locations
            if not locations:
                # Try to search for locations in the datastreams
                datastreams = frost.get_entities(entity_type=f'Things({thing["@iot.id"]})/Datastreams')
                if datastreams:
                    latitudes = []
                    longitudes = []
                    for datastream in datastreams:

                        lat = None
                        lon = None
                        if 'latitude' in datastream['name'].lower():

                            # Get Observations for the datastream
                            observations = frost.get_observations_for_datastream(datastream['@iot.id'], top=1000)

                            if observations:
                                # get the first observation
                                # get unique values
                                unique_observations = {obs['result'] for obs in observations}
                                all_obs = [obs['result'] for obs in observations]
                                # convert all_obs to set
                                unique_observations = set(all_obs)
                                print(f'\nall_obs: {len(all_obs)}')
                                print(f'\nunique_obs: {unique_observations}')

                                # convert to list
                                unique_observations = list(unique_observations)
                                first_observation = observations[0]
                                
                                lat = first_observation['result']
                                latitudes.append(lat)

                        if 'longitude' in datastream['name'].lower():
                            # Get Observations for the datastream
                            observations = frost.get_observations_for_datastream(datastream['@iot.id'])

                            if observations:
                                # get the first observation
                                # get unique values
                                unique_observations = {obs['result'] for obs in observations}
                                all_obs = [obs['result'] for obs in observations]
                                # convert all_obs to set
                                unique_observations = set(all_obs)
                                print(f'\nall_obs: {len(all_obs)}')
                                print(f'\nunique_obs: {unique_observations}')

                                # convert to list
                                unique_observations = list(unique_observations)
                                first_observation = observations[0]
                                
                                lon = first_observation['result']
                                longitudes.append(lon)

                    location = np.array([longitudes, latitudes])
                    # remove duplicates
                    location = np.unique(location, axis=1)
                    location = location.tolist()
                    # make list[longitude, latitude]
                    location = [longitudes[0], latitudes[0]]
                    locations = [{'location': {'type': 'Point', 'coordinates': location}}]

            ##############################################################################################
            # Get the datastreams for the things
            ##############################################################################################
            datastreams = frost.get_entities(entity_type=f'Things({thing["@iot.id"]})/Datastreams')
            datastream_list = []
            for datastream in datastreams:
                if 'latitude' in datastream['name'].lower() or 'longitude' in datastream['name'].lower():
                    continue
                ##############################################################################################
                # Get the observations for each datastream and thing
                ##############################################################################################
                observations = frost.get_observations_for_datastream(datastream['@iot.id'], top=10000)
                df = pd.DataFrame(observations)
                df = df.loc[:, ['phenomenonTime', 'result']]
                
                observations = df.rename(columns={'phenomenonTime': 'time', 'result': 'values'})
                # convert 'time' to stringformat
                observations['time'] = pd.to_datetime(observations['time'], errors="coerce", format="mixed").dt.tz_localize(None)
                observations['time'] = observations['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                observations = observations.to_dict(orient='list')
                if observations:
                    # get the first observation

                    # check if datastream['unitOfMeasurement']['symbol'] is Cel then replace it with °C
                    if datastream['unitOfMeasurement']['symbol'] == 'Cel':
                        datastream['unitOfMeasurement']['symbol'] = '°C'

                    datastream_list.append({
                        "name": datastream["name"],
                        "id": datastream["@iot.id"],
                        "description": datastream["description"],
                        'unitOfMeasurement': datastream["unitOfMeasurement"],
                        "observations": observations,

                    })

            #pprint(datastream_list)
            
            

            

            
            thing_dict = {
                "name": thing["name"],
                "description": thing["description"],
                "@iot.id": thing["@iot.id"],

                "locations": locations,
                'datastreams': datastream_list,
            }

            replace_names = {
                "box_gmr_twl-box_0924002": "Marina Kappeln",
                "box_gmr_twl-box_0924005": "Im Jaich, Stadthafen Flensburg",
            }
            # replace the name of the thing with the name in the replace_names dict
            for key, value in replace_names.items():
                if key in thing_dict["name"]:
                    thing_dict["name"] = value
                    #print(f"Replaced {key} with {value} in {thing_dict['name']}")
                    break

            thing_dicts.append(thing_dict)
            

        #pprint(thing_dicts)
        return thing_dicts



    def get_last_measurement(self, measurement):
        """Returns the latest measurement from a list of time-series data."""
        if not measurement:
            return None
        df = pd.DataFrame.from_dict(measurement).sort_values("time", ascending=False)
        return df.iloc[0] if not df.empty else None

    def get_measurements(self, measurement):
        """Converts measurement data into a sorted DataFrame."""
        if not measurement:
            return None
        df = pd.DataFrame.from_dict(measurement)
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df["values"] = pd.to_numeric(df["values"], errors="coerce")
        df.dropna(inplace=True)
        return df.sort_values("time", ascending=False) if not df.empty else None

    # st.write(st.session_state)
    def header(self):
        if "preloaded_data" not in st.session_state:
            st.session_state["preloaded_data"] = self.preload_data()
        # with st.sidebar:
        #     st.write(st.session_state["preloaded_data"])

        # st.write(st.session_state["map"])
        st.markdown("<h1 style='text-align: center;'>SOOP</h1>", unsafe_allow_html=True)
        st.divider()
        with st.expander("Marinas", expanded=True):
            self.section1()
        st.divider()
        # with st.expander("Daten", expanded=True):
        #     with st.sidebar:
        #         self.section2()
        # st.divider()
        with st.expander("Visualisierung", expanded=True):
            self.section3()
        st.divider()

    def section1(self):
        # 1) Marina-Liste initialisieren
        if "selected_marinas" not in st.session_state:
            st.session_state.selected_marinas = [
                marina["name"] for marina in st.session_state.preloaded_data
            ]
        # initialisiere den ersten Marina-Namen
        if "selected_marina" not in st.session_state:
            st.session_state.selected_marina = st.session_state.selected_marinas[0]

        # 2) Map erzeugen / cachen
        if "folium_map" not in st.session_state:
            folio_map = ShowMap(
                data=st.session_state.preloaded_data,
                zoom=7,
                control_scale=True
            ).plot()
            if not isinstance(folio_map, folium.Map):
                st.warning("Die Karte konnte nicht erstellt werden.")
                return
            st.session_state.folium_map = folio_map

        # 3) Map rendern und Klick-Data abholen
        # 1) Bildschirmmaße per JS
        
        # Liefere sofort einen numerischen Wert – keine JS-Function-Referenz!
        screen_width  = st_javascript(js_code="window.innerWidth",  key="screen_w")
        screen_height = st_javascript(js_code="window.innerHeight", key="screen_h")

        # Beim allerersten Laden kann None zurückkommen, also sicherheitshalber default-Werte nehmen:
        w = screen_width  or 800
        h = screen_height or 600
        map_data = st_folium(
            st.session_state.folium_map,
            width = w  - 40,              # z.B. 40px Rand
            height= int(h * 0.9)         # 90% der Fensterhöhe
        )

        # 4) Erstes nicht-None-Event finden
        click_event = None
        for key in (
            "last_object_clicked_tooltip",
            "last_object_clicked_popup",
            "last_object_clicked",
            "last_clicked",
        ):
            value = map_data.get(key) if map_data else None
            if value:
                click_event = (key, value)
                break

        # 5) Session-State updaten, je nach Event-Typ
        if click_event:
            event_key, event_val = click_event

            if event_key in ("last_object_clicked_tooltip", "last_object_clicked_popup"):
                # Hier steht der Marina-Name direkt im Tooltip/Popup
                st.session_state.selected_marina = event_val

            elif event_key == "last_object_clicked":
                # GeoJSON-Feature: versuche, den Namen aus properties zu holen
                props = event_val.get("properties", {})
                name = props.get("name") or props.get("title")
                if name:
                    st.session_state.selected_marina = name
                else:
                    # Fallback: benutze Koordinaten-Approach
                    coords = event_val.get("geometry", {}).get("coordinates", [])
                    lon0, lat0 = coords if len(coords) == 2 else (None, None)
                    if lat0 is not None:
                        st.session_state.selected_marina = self._closest_marina(lat0, lon0)

            else:  # last_clicked
                lat0, lon0 = event_val["lat"], event_val["lng"]
                st.session_state.selected_marina = self._closest_marina(lat0, lon0)

            # sofort neu rendern, damit die Selectbox den neuen Wert übernimmt
            #st.experimental_rerun()

        # 6) Sidebar-Selectbox mit Key auf denselben State
        # with st.sidebar:
        #     st.selectbox(
        #         "Wähle den Hafen aus:",
        #         options=st.session_state.selected_marinas,
        #         key="selected_marina"
        #     )

        # 7) Anzeige
        #st.write("Aktuell ausgewählt:", st.session_state.selected_marina)
        




    def _closest_marina(self, lat0: float, lon0: float) -> str:
        """Hilfsmethode: findet die Marina mit dem kürzesten euklidischen Abstand."""
        closest = min(
            st.session_state.preloaded_data,
            key=lambda m: (
                (m["locations"][0]["location"]["coordinates"][1] - lat0) ** 2
                + (m["locations"][0]["location"]["coordinates"][0] - lon0) ** 2
            )
        )
        return closest["name"]


    def section2(self):
        selected_marina = st.session_state.get("selected_marina", None)
        marina_data = next(
            (
                m
                for m in st.session_state["preloaded_data"]
                if m["name"] == selected_marina
            ),
            None,
        )

        if not marina_data:
            st.warning("Keine Daten verfügbar")
            return

        measurement = marina_data.get("measurement", {})

        data_dict = {
            "Wassertemperatur [°C]": self.get_last_measurement(
                measurement.get("water_temperature")
            ),
            "Wasserstand [m]": self.get_last_measurement(
                measurement.get("water_height")
            ),
            "Luft Temperatur [°C]": self.get_last_measurement(
                measurement.get("air_temperature")
            ),
            "Wind Richtung [°]": self.get_last_measurement(
                measurement.get("wind_direction")
            ),
            "Windgeschwindigkeit [km/h]": self.get_last_measurement(
                measurement.get("wind_speed")
            ),
            "Luftdruck [hPa]": self.get_last_measurement(
                measurement.get("air_pressure")
            ),
            "Luftfeuchtigkeit [%]": self.get_last_measurement(
                measurement.get("air_humidity")
            ),
        }

        current_time = self.get_last_measurement(measurement.get("water_temperature"))
        formatted_time = (
            current_time["time"].split("T")[0]
            + " "
            + current_time["time"].split("T")[1].split("+")[0]
            if current_time.all()
            else "N/A"
        )

        col1, col2, col3 = st.columns(3)
        with col2:
            # st.markdown(
            #     f"<h3 style='text-align: center;'>{selected_marina}</h3>",
            #     unsafe_allow_html=True,
            # )

            if "windrose" not in st.session_state:
                windrose = Windrose(data=None).plot()
                st.session_state["windrose"] = windrose

            # st.plotly_chart(st.session_state['windrose'])

        col1, col2 = st.columns(2)
        with col1:
            self.boxed_text("Aktuelle Zeit", formatted_time)
            st.divider()

            for key, value in list(data_dict.items())[:3]:
                self.boxed_text(
                    key, round(value["values"], 3) if value.all() else "N/A"
                )
                st.divider()

        with col2:
            for key, value in list(data_dict.items())[3:]:
                self.boxed_text(
                    key, round(value["values"], 3) if value.all() else "N/A"
                )
                st.divider()

    def boxed_text(self, title, value):
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 24px; font-weight: bold;">{title}</div>
            <div style="display: flex; justify-content: center;">
                <pre style="
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 5px;
                    border: 1px solid #ddd;
                    text-align: center;
                    font-size: 30px;  
                    font-weight: bold;  
                ">{value}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def section3(self):
        marina_name = st.session_state.get("selected_marina", None)
        marina_data = next(
            (m for m in st.session_state["preloaded_data"] if m["name"] == marina_name),
            None,
        )

        if not marina_data:
            st.warning("Keine Daten verfügbar")
            return
        
        # Plot the data
        st.markdown(
            f"<h3 style='text-align: center;'>{marina_name}</h3>",
            unsafe_allow_html=True,
        )
        
        # 1) Auswahl des Zeitraums
        timeframe = st.selectbox(
            "Zeitraum auswählen:",
            ("Letzte 24 Stunden", "Letzte 7 Tage", "Letzter Monat", "Letztes Jahr", "All Data"),
        )

        # 2) Cutoff-Zeitpunkt berechnen
        now = pd.Timestamp.now()
        if timeframe == "Letzte 24 Stunden":
            cutoff = now - pd.Timedelta(hours=24)
        elif timeframe == "Letzte 7 Tage":
            cutoff = now - pd.Timedelta(days=7)
        elif timeframe == "Letzter Monat":
            cutoff = now - pd.DateOffset(months=1)
        elif timeframe == "Letztes Jahr":
            cutoff = now - pd.DateOffset(years=1)
        elif timeframe == "All Data":
            cutoff = pd.Timestamp.min


        # 3) Figure anlegen
        fig = go.Figure()

        # 4) Units sammeln
        units = set()

        # 5) Für jeden Datastream: DataFrame bauen und filtern
        for i, datastream in enumerate(marina_data["datastreams"]):
            df = pd.DataFrame.from_dict(datastream["observations"])
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            df["values"] = pd.to_numeric(df["values"], errors="coerce")
            df.dropna(inplace=True)

            # 5a) Nur Daten ab Cutoff berücksichtigen
            df = df[df["time"] >= cutoff]
            if df.empty:
                continue

            # 5b) Unit-Symbol hinzufügen
            unit = datastream.get("unitOfMeasurement", {}).get("symbol", "")
            if unit:
                units.add(unit)

            # 6) Sichtbarkeit: nur erstes Trace direkt sichtbar
            visible = True if i == 0 else "legendonly"

            # 7) Trace hinzufügen
            name = (
                datastream["name"]
                .split("*")[0]
                .strip()
                .capitalize()
                .replace("_", " ")
            )
            # add unit to name
            if unit:
                name += f" [{unit}]"
            
            fig.add_trace(
                go.Scatter(
                    x=df["time"],
                    y=df["values"],
                    mode="lines",
                    name=name,
                    visible=visible,
                )
            )


            # 9) Layout anpassen
            fig.update_layout(
                title=f"Messwerte — {timeframe}",
                xaxis_title="Zeit",
                yaxis_title="Messwert",
                legend_title="Datastreams",
                height=500,
                width=1500,
            )

        # 10) Plot anzeigen
        st.plotly_chart(fig, use_container_width=True)

      


if __name__ == "__main__":
    app = StreamlitApp()
    #app.preload_data()

    app.header()
    
    
    # app.header()
    # data = app.preload_data()

    # json_data = json.dumps(data, default=convert_timestamps, indent=4)
    # print(data[0]['measurement'].keys())
    # print(type(json_data))

    # df = pd.DataFrame(data[0]['measurement']['water_temperature'])
    
    # df['time'] = pd.to_datetime(df['time'])
    # print(df.info())
    # print(df.describe())
    # # df = pd.DataFrame(data)
    # print(df)
    # print(df.info())

