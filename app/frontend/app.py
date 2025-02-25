import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium
import requests

# Colors
# [theme]
# base="light"
# primaryColor="#ff6666"
# secondaryBackgroundColor="#78d278"
# textColor="#053246"

st.set_page_config(layout="wide", page_title="SOOP-Dashboard", page_icon=":shark:")

API_URL = "http://localhost:8000/data"

class StreamlitApp:
    def __init__(self):
        if 'preloaded_data' not in st.session_state:
            st.session_state['preloaded_data'] = self.preload_data()
        self.preloaded_data = st.session_state['preloaded_data']

    def preload_data(self):
        try:
            return requests.get(API_URL).json()
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
        if "selected_marinas" not in st.session_state:
            st.session_state["selected_marinas"] = [marina["name"] for marina in self.preloaded_data]

        selected_marina = st.selectbox("Wähle den Hafen aus:", st.session_state["selected_marinas"])
        st.session_state["selected_marina"] = selected_marina

        if "map" not in st.session_state:
            st.session_state["map"] = self.make_map()

        st_folium(st.session_state["map"], width=1000, height=500)

    def section2(self):
        selected_marina = st.session_state.get("selected_marina", None)
        marina_data = next((m for m in self.preloaded_data if m["name"] == selected_marina), None)

        if not marina_data:
            st.warning("Keine Daten verfügbar")
            return

        measurement = marina_data.get("measurement", {})

        data_dict = {
            "Wassertemperatur [°C]": self.get_last_measurement(measurement.get("water_temperature")),
            "Wasserstand [m]": self.get_last_measurement(measurement.get("water_height")),
            "Luft Temperatur [°C]": self.get_last_measurement(measurement.get("air_temperature")),
            "Wind Richtung [°]": self.get_last_measurement(measurement.get("wind_direction")),
            "Windgeschwindigkeit [km/h]": self.get_last_measurement(measurement.get("wind_speed")),
            "Luftdruck [hPa]": self.get_last_measurement(measurement.get("air_pressure")),
            "Luftfeuchtigkeit [%]": self.get_last_measurement(measurement.get("air_humidity")),
        }

        current_time = self.get_last_measurement(measurement.get("water_temperature"))
        formatted_time = current_time["time"].split("T")[0] + " " + current_time["time"].split("T")[1].split("+")[0] if current_time.all() else "N/A"

        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>{selected_marina}</h3>", unsafe_allow_html=True)
            windrose = self.make_windrose(measurement.get("wind_direction"))
            st.plotly_chart(windrose)
        col1, col2 = st.columns(2)
        with col1:
            self.boxed_text("Aktuelle Zeit", formatted_time)
            st.divider()
            
            for key, value in list(data_dict.items())[:3]:
                self.boxed_text(key, round(value["values"], 3) if value.all() else "N/A")
                st.divider()

        with col2:

            for key, value in list(data_dict.items())[3:]:
                self.boxed_text(key, round(value["values"], 3) if value.all() else "N/A")
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
        marina_data = next((m for m in self.preloaded_data if m["name"] == marina_name), None)

        if not marina_data:
            st.warning("Keine Daten verfügbar")
            return

        measurement = marina_data.get("measurement", {})
        data_dict = {
            "Wassertemperatur": (self.get_measurements(measurement.get("water_temperature")), "Temperatur [°C]"),
            "Wasserstand": (self.get_measurements(measurement.get("water_height")), "Wasserstand [m]"),
            "Windgeschwindigkeit": (self.get_measurements(measurement.get("wind_speed")), "Windgeschwindigkeit [km/h]"),
            "Windrichtung": (self.get_measurements(measurement.get("wind_direction")), "Windrichtung [°]"),
            "Lufttemperatur": (self.get_measurements(measurement.get("air_temperature")), "Temperatur [°C]"),
            "Luftdruck": (self.get_measurements(measurement.get("air_pressure")), "Luftdruck [hPa]"),
            "Luftfeuchtigkeit": (self.get_measurements(measurement.get("air_humidity")), "Luftfeuchtigkeit [%]"),
        }

        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>{marina_name}</h3>", unsafe_allow_html=True)

        figures = []
        for name, (data, y_label) in data_dict.items():
            if data is not None:
                fig = self.make_line_plot(data["time"], data["values"], name, "Zeit", y_label)
                figures.append(fig)
                
        if 'figures' not in st.session_state:
            st.session_state['figures'] = figures
        
        selected_figure = st.radio("", list(data_dict.keys()), horizontal=True)
        if selected_figure in data_dict:
            fig_index = list(data_dict.keys()).index(selected_figure)
            st.plotly_chart(st.session_state['figures'][fig_index])
        

    def make_line_plot(self, x, y, title, x_label, y_label):
        fig = go.Figure([go.Scatter(x=x, y=y, mode="lines", name=title,line=dict(color='rgb(255, 102, 102)', width=2))])
        fig.update_layout(
                title={'text': title, 'font': {'size': 20}},  # Titel größer
                xaxis={'title': {'text': x_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  # X-Achse größer
                yaxis={'title': {'text': y_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  # Y-Achse größer
                template='plotly_white',
                hovermode='x unified'
            )
        return fig
    
    def make_map(self):
        """Generates a Folium map with markers for marinas, displaying water temperature."""
        
        # Get the averate latitude and longitude of all marinas
        latitudes = [marina.get("location", {}).get("latitude") for marina in self.preloaded_data]
        longitudes = [marina.get("location", {}).get("longitude") for marina in self.preloaded_data]

        latitude_mean = np.mean([lat for lat in latitudes if lat is not None])
        longitude_mean = np.mean([lon for lon in longitudes if lon is not None])

        print(f"Centering map on {latitude_mean}, {longitude_mean}")

        # Initialize map centered on Kiel
        m = folium.Map(location=[latitude_mean, longitude_mean], 
                       zoom_start=7, control_scale=False)
        
        for marina in self.preloaded_data:
            try:
                name = marina.get("name", "Unknown Marina")
                location = marina.get("location", {})
                latitude = location.get("latitude")
                longitude = location.get("longitude")
                measurement = marina.get("measurement", {})
                water_temp_data = measurement.get("water_temperature")

                # Ensure we have valid coordinates and data
                if latitude is None or longitude is None or not water_temp_data:
                    print(f"Skipping {name} due to missing data.")
                    continue

                # Convert dictionary to DataFrame
                df = pd.DataFrame.from_dict(water_temp_data)

                # Ensure correct data types
                df["time"] = pd.to_datetime(df["time"], errors="coerce")
                df["values"] = pd.to_numeric(df["values"], errors="coerce")

                # Drop NaN values and sort by time
                df.dropna(inplace=True)
                df.sort_values(by="time", ascending=False, inplace=True)

                if df.empty:
                    print(f"No valid water temperature data for {name}. Skipping.")
                    continue

                # Get the most recent temperature
                current_temp = round(df["values"].iloc[0], 2)
                current_time = df["time"].iloc[0].strftime("%Y-%m-%d %H:%M")

                # Create a custom HTML popup
                popup_html = f"""
                    <div style="font-family: Arial; text-align: center;">
                        <b>{name}</b><br>
                        <hr style="margin: 5px 0;">
                        <b>Zeit:</b> {current_time} <br>
                        <b>Temperatur:</b> {current_temp}°C
                    </div>
                """
                from folium import Marker, Popup
                # Add marker with custom popup
                Marker(
                    [latitude, longitude],
                    popup=Popup(popup_html, max_width=300),  # Define popup with max width
                    tooltip=name,
                    icon=folium.Icon(icon="info-sign", color="lightred")
                ).add_to(m)

            except Exception as e:
                print(f"Error processing {name}: {e}")

        return m
    
    def make_windrose(self, data):
        import plotly.graph_objects as go

        # Beispiel-Daten: Windrichtung in Grad (0° = N, 90° = E, 180° = S, 270° = W)
        wind_directions = [0]  # Nord
        wind_speeds = [30]  # Windgeschwindigkeit

        # Erstellen des Plots
        fig = go.Figure()

        fig.add_trace(go.Barpolar(
            r=wind_speeds,  # Windgeschwindigkeit als Radius
            theta=wind_directions,  # Windrichtung in Grad
            width=45,  # Breite der Balken (45° für 8 Himmelsrichtungen)
            marker=dict(
                color=wind_speeds,
                colorscale='Oranges',  
                showscale=True,
                cmin=0,  # Minimaler Wert der Skala
                cmax=50,  # Maximaler Wert der Skala
                colorbar=dict(
                    x=1,  # Position der Skala
                    y=0.5,  # Vertikale Position
                    len=1,  # Höhe der Skala
                    title="Wind (m/s)",  # Titel der Skala
                    tickvals=[0, 10, 20, 30, 40, 50],  # Definierte Werte
                    #ticktext=["0", "Leicht", "Mittel", "Stark", "Sehr stark", "Extrem"]  # Eigene Labels
                )
            )
        ))

        # Theme anwenden
        fig.update_layout(
            
            plot_bgcolor="#78d278",  # Hintergrund des Plots
            font=dict(color="#053246"),  # Allgemeine Textfarbe
            # size
            width=300,
            height=300,
            polar=dict(
                radialaxis=dict(showticklabels=False, ticksuffix=" m/s"),
                angularaxis=dict(direction="clockwise", tickmode="array",
                                tickvals=[0, 90, 180, 270],
                                ticktext=['N', 'E', 'S', 'W'])  # Himmelsrichtungen
            )
        )

        return fig




app = StreamlitApp()
app.header()
