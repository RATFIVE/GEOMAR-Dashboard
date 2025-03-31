#import app.backend.Layout as st
import pandas as pd
import numpy as np
import sys
import subprocess


import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import time 
from streamlit_folium import st_folium
import json
import folium
import requests

st.set_page_config(layout="wide", page_title="SOOP-Dashboard", page_icon=":shark:")



# Prussian blue
# #053246
# R5 G50 B70

# Mantis
# #78D278
# R120 G210 B120

# Bittersweet
# #FF6666
# R255 G102 B102


# Color Theme
# [theme]
# base="light"
# primaryColor="#ff6666"
# secondaryBackgroundColor="#78d278"
# textColor="#053246"




class StreamlitApp:

    def __init__(self):

        self.api_url = "http://localhost:8000"
        self.api_data = "/data"

        self.data = self.api_url + self.api_data
        #self.fig = fig

        if 'preloaded_data' not in st.session_state:
            st.session_state['preloaded_data'] = self.preload_data()
        self.preloaded_data = st.session_state['preloaded_data']
            
        

    def header(self):
        
        st.markdown("""<h1 style="text-align: center;">SOOP</h1>""", unsafe_allow_html=True)
        st.divider()


        with st.expander("Marinas", expanded=True):
            self.section1()
        st.divider()

        #st.markdown("""<h2 style="text-align: center;">Akutelle Daten</h2>""", unsafe_allow_html=True)
        with st.expander("Daten", expanded=True):
            self.section2()
        st.divider()

        #st.markdown("""<h2 style="text-align: center;">Visualisierung von Temperaturdaten</h2>""", unsafe_allow_html=True)
        with st.expander("Visualisierung", expanded=True):
            
            self.section3()
        st.divider()

    

    
    

    def section1(self):
        

        # Nur initialisieren, wenn die Marinas noch nicht gespeichert wurden
        if 'selected_marinas' not in st.session_state:
            st.session_state['selected_marinas'] = [marina['name'] for marina in self.preloaded_data]

        # Selectbox mit bestehender Liste aus session_state
        self.selected_marina = st.selectbox(
            label='Wähle den Hafen aus:', 
            options=st.session_state['selected_marinas']
    )

        if 'map' not in st.session_state:
            st.session_state['map'] = self.make_map()

        m = st.session_state['map']
        st_folium(m, 
                  width=1000, 
                  height=500)

        
    



    def section2(self):
        for marina in self.preloaded_data:
            if marina['name'] == self.selected_marina:
                

                name = marina.get("name", "Unknown Marina")
                location = marina.get("location", {})
                latitude = location.get("latitude")
                longitude = location.get("longitude")
                measurement = marina.get("measurement", {})

                def get_last_measurement(measurement):
                    if not measurement:
                        return None
                    last_measurement = {}
                    df = pd.DataFrame.from_dict(measurement)
                    df.sort_values(by="time", ascending=False, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    last_measurement = df.iloc[0]

                    return last_measurement

                
                current_water_temperature = get_last_measurement(measurement.get("water_temperature")).get("values")
                current_water_heigth = get_last_measurement(measurement.get("water_height")).get("values")
                current_wind_speed = get_last_measurement(measurement.get("wind_speed")).get("values")
                current_wind_direction = get_last_measurement(measurement.get("wind_direction")).get("values")
                current_air_temperature = get_last_measurement(measurement.get("air_temperature")).get("values")
                current_air_pressure = get_last_measurement(measurement.get("air_pressure")).get("values")
                current_air_humidity = get_last_measurement(measurement.get("air_humidity")).get("values")
                
                current_time = get_last_measurement(measurement.get("water_temperature")).get("time")
                break
        
        
        def boxed_text(text, value):

            with st.container():
                st.markdown(
                    f"""
                    <div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 10px;">
                        {text}
                    </div>
                    <div style="display: flex; justify-content: center;">
                        <pre style="
                            background-color: #f0f0f0;
                            padding: 10px;
                            border-radius: 5px;
                            border: 1px solid #ddd;
                            text-align: left;
                            width: fit-content;
                            max-width: 100%;
                            white-space: pre-wrap;
                            word-wrap: break-word;
                            font-size: 30px;  
                            font-weight: bold;  
                        ">
                    {value}
                        </pre>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # convert marina time from 2025-02-19T10:00:00+00:00 to 2025-02-19 10:00:00
        time = current_time.split('T')[0] + ' ' + current_time.split('T')[1].split('+')[0]
        col1, col2, col3 = st.columns(3, vertical_alignment='center')
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>{name}</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            boxed_text('Aktuelle Zeit', time)
            st.divider()
            boxed_text('Wassertemperatur [°C]', round(current_water_temperature, 3))
            st.divider()
            boxed_text('Wasserstand [m]', round(current_water_heigth, 3))
            st.divider()
            boxed_text('Luft Temperatur [°C]', round(current_air_temperature, 3))
            
            
                
            
        with col2:
            boxed_text('Wind Richtung [°]', round(current_wind_direction,3 ))
            st.divider()
            boxed_text('Windgeschwindigkeit [km/h]', round(current_wind_speed, 3))
            st.divider()
            boxed_text('Luftdruck [hPa]', round(current_air_pressure, 3))
            st.divider()
            boxed_text('Luftfeuchtigkeit [%]', round(current_air_humidity,3))
                       
            
            
        
        
        
        

    



    def section3(self):
        fig = go.Figure()

        marina_name = self.selected_marina
        data_water_temperature = data_water_heigth = data_wind_speed = None
        data_wind_direction = data_air_temperature = data_air_pressure = data_air_humidity = None

        # Durchsuche die preloaded_data nach der gewählten Marina
        for marina in self.preloaded_data:
            if marina['name'] == marina_name:
                name = marina.get("name", "Unknown Marina")
                location = marina.get("location", {})
                latitude = location.get("latitude")
                longitude = location.get("longitude")
                measurement = marina.get("measurement", {})

                def get_measurements(measurement):
                    if not measurement:
                        return None
                    df = pd.DataFrame.from_dict(measurement)
                    if df.empty:
                        return None
                    df['time'] = pd.to_datetime(df['time'], errors='coerce')
                    df['values'] = pd.to_numeric(df['values'], errors='coerce')
                    df.dropna(inplace=True)
                    df.sort_values(by="time", ascending=False, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    return df if not df.empty else None

                # Messwerte abrufen
                data_water_temperature = get_measurements(measurement.get("water_temperature"))
                data_water_heigth = get_measurements(measurement.get("water_height"))
                data_wind_speed = get_measurements(measurement.get("wind_speed"))
                data_wind_direction = get_measurements(measurement.get("wind_direction"))
                data_air_temperature = get_measurements(measurement.get("air_temperature"))
                data_air_pressure = get_measurements(measurement.get("air_pressure"))
                data_air_humidity = get_measurements(measurement.get("air_humidity"))

                # Falls keine Wassertemperatur-Daten vorhanden sind, setze data_time auf None
                data_time = data_water_temperature["time"] if data_water_temperature is not None else None
                break

        # Sicherstellen, dass Daten existieren, bevor len() aufgerufen wird
        if data_water_temperature is not None:
            st.write(len(data_water_temperature))
        else:
            st.write("Keine Daten zur Wassertemperatur vorhanden.")

        col1, col2, col3 = st.columns(3, vertical_alignment='center')
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>{marina_name}</h3>", unsafe_allow_html=True)

        def make_line_plot(x, y, title, x_label, y_label):
            if x is None or y is None:
                return None  # Falls keine Daten vorhanden sind, keinen Plot erstellen

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                name=title,
                line=dict(color='rgb(255, 102, 102)', width=2)
            ))

            fig.update_layout(
                title={'text': title, 'font': {'size': 20}},  # Titel größer
                xaxis={'title': {'text': x_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  # X-Achse größer
                yaxis={'title': {'text': y_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  # Y-Achse größer
                template='plotly_white',
                hovermode='x unified'
            )

            return fig

        # Liste der Diagramme erstellen, nur wenn Daten vorhanden sind
        fig_names = {
            "Wassertemperatur": (data_water_temperature, "Temperatur [°C]"),
            "Wasserstand": (data_water_heigth, "Wasserstand [m]"),
            "Windgeschwindigkeit": (data_wind_speed, "Windgeschwindigkeit [km/h]"),
            "Windrichtung": (data_wind_direction, "Windrichtung [°]"),
            "Lufttemperatur": (data_air_temperature, "Temperatur [°C]"),
            "Luftdruck": (data_air_pressure, "Luftdruck [hPa]"),
            "Luftfeuchtigkeit": (data_air_humidity, "Luftfeuchtigkeit [%]"),
        }

        figures = []
        for name, (data, y_label) in fig_names.items():
            if data is not None:
                fig = make_line_plot(data["time"], data["values"], name, "Zeit", y_label)
                if fig:
                    figures.append(fig)


        # if 'figures' not in st.session_state:
        #     st.session_state['figures'] = figures
        # figures = st.session_state['figures']



        figure_selection = st.radio("", fig_names, horizontal=True)
        if figure_selection == "Wassertemperatur":

            st.plotly_chart(figures[0])

        if figure_selection == "Wasserstand":
            st.plotly_chart(figures[1])

        if figure_selection == "Windgeschwindigkeit":
            st.plotly_chart(figures[2])
        
        if figure_selection == "Windrichtung":
            st.plotly_chart(figures[3])
        
        if figure_selection == "Lufttemperatur":
            st.plotly_chart(figures[4])

        if figure_selection == "Luftdruck":
            st.plotly_chart(figures[5])

        if figure_selection == "Luftfeuchtigkeit":
            st.plotly_chart(figures[6])





    def get_json_data(self, file):
        with open(file) as f:
            data = json.load(f)
        return data


    
    def get_current_temperature_and_time(self):
        data = self.df_obs
        current_temp = data["result"].iloc[-1]
        current_time = data["phenomenonTime"].iloc[-1]

        return current_temp, current_time
    





    def sidebar(self):
        st.sidebar.header("Settings")
        st.sidebar.write("Choose the temperature data to display")
        self.thing = st.sidebar.selectbox(
            "Select a Thing",
            ["Things(3)", "Things(4)"]
        )


    def get_frost_observations(self, thing="Things(3)"):
        try:
            pass
            # #print('Get data')
            # server = FrostServer(thing=thing)
            # all_observations = server.get_all_observations()
            # df_obs = pd.DataFrame(all_observations)
            # df_obs["phenomenonTime"] = pd.to_datetime(df_obs["phenomenonTime"])
            # df_obs["resultTime"] = pd.to_datetime(df_obs["resultTime"])
            # # convert result to float
            # df_obs["result"] = df_obs["result"].astype(float)
            return None
            
        except Exception as e:
            print(e)


    def get_position_data(self):
        pass
        # server = FrostServer()
        # position_url = server.get_position_url()
        # content = server.get_content(position_url)
        # #print(content)
        return None
    



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
                       zoom_start=7)
        
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





if __name__ == '__main__':

    app = StreamlitApp()
    app.header()
    data = app.preload_data()
    for marina in data:
        print(marina.keys())
        break
    #app.sidebar()
