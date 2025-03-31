import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import requests

st.set_page_config(layout="wide", page_title="SOOP-Dashboard", page_icon=":shark:")

class StreamlitApp:

    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.api_data = "/data"
        self.data = self.api_url + self.api_data

        # Load preloaded data from session state once
        if 'preloaded_data' not in st.session_state:
            st.session_state['preloaded_data'] = self.preload_data()

        self.preloaded_data = st.session_state['preloaded_data']

    def header(self):
        st.markdown("<h1 style='text-align: center;'>SOOP</h1>", unsafe_allow_html=True)
        st.divider()

        with st.expander("Marinas", expanded=True):
            self.section1()
        st.divider()

        with st.expander("Daten", expanded=True):
            self.section2()
        st.divider()

        with st.expander("Visualisierung", expanded=True):
            self.section3()
        st.divider()

    def section1(self):
        if 'selected_marinas' not in st.session_state:
            st.session_state['selected_marinas'] = [marina['name'] for marina in self.preloaded_data]

        selected_marina = st.selectbox(
            label='Wähle den Hafen aus:', 
            options=st.session_state['selected_marinas']
        )

        if 'map' not in st.session_state:
            st.session_state['map'] = self.make_map()

        st_folium(st.session_state['map'], width=1000, height=500)

    def section2(self):
        selected_marina = self.selected_marina
        marina_data = next(marina for marina in self.preloaded_data if marina['name'] == selected_marina)
        last_measurement = self.get_last_measurement(marina_data['measurement'])
        self.display_measurements(last_measurement)

    def section3(self):
        marina_name = self.selected_marina
        marina_data = next(marina for marina in self.preloaded_data if marina['name'] == marina_name)
        measurements = marina_data.get("measurement", {})

        # Optimized: Create plots for all available data types
        fig_names = {
            "Wassertemperatur": "water_temperature",
            "Wasserstand": "water_height",
            "Windgeschwindigkeit": "wind_speed",
            "Windrichtung": "wind_direction",
            "Lufttemperatur": "air_temperature",
            "Luftdruck": "air_pressure",
            "Luftfeuchtigkeit": "air_humidity"
        }

        figures = []
        for name, measurement_key in fig_names.items():
            data = self.get_measurements(measurements.get(measurement_key))
            if data:
                fig = self.make_line_plot(data["time"], data["values"], name, "Zeit", name)
                figures.append(fig)

        figure_selection = st.radio("", fig_names.keys(), horizontal=True)
        fig_index = list(fig_names.keys()).index(figure_selection)
        st.plotly_chart(figures[fig_index])

    def get_last_measurement(self, measurement):
        df = pd.DataFrame.from_dict(measurement)
        df.sort_values(by="time", ascending=False, inplace=True)
        return df.iloc[0] if not df.empty else {}

    def display_measurements(self, last_measurement):
        time = last_measurement.get("time", "").split('T')[0] + ' ' + last_measurement.get("time", "").split('T')[1].split('+')[0]
        measurements = {
            "Aktuelle Zeit": time,
            "Wassertemperatur [°C]": round(last_measurement.get("water_temperature", {}).get("values", 0), 3),
            "Wasserstand [m]": round(last_measurement.get("water_height", {}).get("values", 0), 3),
            "Luft Temperatur [°C]": round(last_measurement.get("air_temperature", {}).get("values", 0), 3),
            "Wind Richtung [°]": round(last_measurement.get("wind_direction", {}).get("values", 0), 3),
            "Windgeschwindigkeit [km/h]": round(last_measurement.get("wind_speed", {}).get("values", 0), 3),
            "Luftdruck [hPa]": round(last_measurement.get("air_pressure", {}).get("values", 0), 3),
            "Luftfeuchtigkeit [%]": round(last_measurement.get("air_humidity", {}).get("values", 0), 3)
        }

        for key, value in measurements.items():
            self.boxed_text(key, value)

    def boxed_text(self, text, value):
        with st.container():
            st.markdown(f"""
            <div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 10px;">{text}</div>
            <div style="display: flex; justify-content: center;">
                <pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; border: 1px solid #ddd; text-align: left; font-size: 30px; font-weight: bold;">
                {value}
                </pre>
            </div>
            """, unsafe_allow_html=True)

    def make_line_plot(self, x, y, title, x_label, y_label):
        if x is None or y is None:
            return None  # Avoid plotting if data is missing

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=title, line=dict(color='rgb(255, 102, 102)', width=2)))
        fig.update_layout(title=title, xaxis_title=x_label, yaxis_title=y_label, template='plotly_white', hovermode='x unified')
        return fig

    def get_measurements(self, measurement):
        if not measurement:
            return None
        df = pd.DataFrame.from_dict(measurement)
        if df.empty:
            return None
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df['values'] = pd.to_numeric(df['values'], errors='coerce')
        df.dropna(inplace=True)
        df.sort_values(by="time", ascending=False, inplace=True)
        return df if not df.empty else None

    def make_map(self):
        latitudes = [marina.get("location", {}).get("latitude") for marina in self.preloaded_data]
        longitudes = [marina.get("location", {}).get("longitude") for marina in self.preloaded_data]
        latitude_mean = np.mean([lat for lat in latitudes if lat is not None])
        longitude_mean = np.mean([lon for lon in longitudes if lon is not None])

        m = folium.Map(location=[latitude_mean, longitude_mean], zoom_start=7)
        for marina in self.preloaded_data:
            try:
                name = marina.get("name", "Unknown Marina")
                location = marina.get("location", {})
                folium.Marker([location.get("latitude"), location.get("longitude")], popup=name).add_to(m)
            except Exception as e:
                print(f"Error creating map marker for marina {marina.get('name')}: {e}")
        return m

    def preload_data(self):
        # Load data from FastAPI as a dict
        response = requests.get(self.data)

        # Ensure request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()  # Convert JSON to dict
            return data
        else:
            print(f"Error: Failed to fetch data, status code {response.status_code}")
            return None


app = StreamlitApp()
app.header()
