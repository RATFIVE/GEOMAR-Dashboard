import pandas as pd
import streamlit as st
from utils.Visualisations import ShowMap, LinePlot, Windrose
from utils.data_loader import get_marina_data
import json
import plotly.graph_objects as go


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
        # mode = 'forecast'
        # latitudes = [52.52, 52.52, 52.52]
        # longitudes = [13.41, 13.41, 13.41]
        # features = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
        # start_date = "2024-12-19"
        # end_date = "2025-03-19"

        # url_weather_forcast = f'https://api.open-meteo.com/v1/forecast?latitude=52.52,52.52,52.52&longitude=13.41,13.41,13.41&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&start_date=2024-12-19&end_date=2025-03-19'
        # url_weather_forcast = f'https://api.open-meteo.com/v1/{mode}?latitude={latitudes}&longitude={longitudes}&hourly={features}&start_date={start_date}&end_date={end_date}'

        # data = requests.get(url_weather_forcast).json()
        # print(data)

        try:
            marinas = get_marina_data()
            # print(marinas)
            # # put marina into json format
            # marinas = json.loads(marinas)

            marinas = json.dumps(marinas, default=convert_timestamps, indent=4)
            marinas = json.loads(marinas)
            #print(marinas)
            return marinas
            # return None
            # return requests.get(API_URL).json()
        except:
            return []

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

        # st.write(st.session_state["map"])
        st.markdown("<h1 style='text-align: center;'>SOOP</h1>", unsafe_allow_html=True)
        st.divider()
        with st.expander("Marinas", expanded=True):
            self.section1()
        st.divider()
        with st.expander("Daten", expanded=True):
            with st.sidebar:
                self.section2()
        st.divider()
        with st.expander("Visualisierung", expanded=True):
            self.section3()
        st.divider()

    def section1(self):
        if "selected_marinas" not in st.session_state:
            st.session_state["selected_marinas"] = [
                marina["name"] for marina in st.session_state["preloaded_data"]
            ]
        with st.sidebar:
            selected_marina = st.selectbox(
                "Wähle den Hafen aus:", st.session_state["selected_marinas"]
            )
        st.session_state["selected_marina"] = selected_marina
        #print(st.session_state["preloaded_data"])
        if "map" not in st.session_state:
            showmap = ShowMap(
                data=st.session_state["preloaded_data"], zoom=7, control_scale=True
            )
            # m = folium.Map(location=[54.3233, 10.1228], zoom_start=10)  # Beispiel Kiel
            # folium.Marker([54.3233, 10.1228], tooltip="Kiel").add_to(m)
            # st.session_state["map"] = m
            m = showmap.plot()
            st.session_state["map"] = m
            if not isinstance(m, go.Figure):  # Überprüfen, ob ein gültiges Plotly-Objekt zurückgegeben wird
                st.warning("Die Karte konnte nicht erstellt werden.")
                return
        st.plotly_chart(st.session_state["map"], width=1000, height=1000)

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

        measurement = marina_data.get("measurement", {})
        data_dict = {
            "Wassertemperatur": (
                self.get_measurements(measurement.get("water_temperature")),
                "Temperatur [°C]",
            ),
            "Wasserstand": (
                self.get_measurements(measurement.get("water_height")),
                "Wasserstand [m]",
            ),
            "Windgeschwindigkeit": (
                self.get_measurements(measurement.get("wind_speed")),
                "Windgeschwindigkeit [km/h]",
            ),
            "Windrichtung": (
                self.get_measurements(measurement.get("wind_direction")),
                "Windrichtung [°]",
            ),
            "Lufttemperatur": (
                self.get_measurements(measurement.get("air_temperature")),
                "Temperatur [°C]",
            ),
            "Luftdruck": (
                self.get_measurements(measurement.get("air_pressure")),
                "Luftdruck [hPa]",
            ),
            "Luftfeuchtigkeit": (
                self.get_measurements(measurement.get("air_humidity")),
                "Luftfeuchtigkeit [%]",
            ),
        }

        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown(
                f"<h3 style='text-align: center;'>{marina_name}</h3>",
                unsafe_allow_html=True,
            )

        figures = []
        for name, (data, y_label) in data_dict.items():
            if data is not None:
                fig = LinePlot(
                    data["time"], data["values"], name, "Zeit", y_label
                ).plot()
                # fig = self.make_line_plot(data["time"], data["values"], name, "Zeit", y_label)
                figures.append(fig)

        if "figures" not in st.session_state:
            st.session_state["figures"] = figures

        selected_figure = st.radio("", list(data_dict.keys()), horizontal=True)
        if selected_figure in data_dict:
            fig_index = list(data_dict.keys()).index(selected_figure)
            st.plotly_chart(st.session_state["figures"][fig_index])


if __name__ == "__main__":
    app = StreamlitApp()
    app.header()
    data = app.preload_data()

    json_data = json.dumps(data, default=convert_timestamps, indent=4)
    print(data[0]['measurement'].keys())
    print(type(json_data))

    df = pd.DataFrame(data[0]['measurement']['water_temperature'])
    
    df['time'] = pd.to_datetime(df['time'])
    print(df.info())
    print(df.describe())
    # df = pd.DataFrame(data)
    print(df)
    print(df.info())

