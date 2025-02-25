import app.Layout as st
import pandas as pd
import numpy as np
import sys
import subprocess
from utils.frost_server import FrostServer

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import time 
from streamlit_folium import st_folium
import json
import folium
from utils.Copernicus import AdvancedCopernicus
from utils.OpenMeteoWeather import OpenMeteoWeather
#st.set_page_config(layout="wide", page_title="SOOP-Dashboard", page_icon=":shark:")

ac = AdvancedCopernicus() 

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
        #self.fig = fig
        if 'df_obs' not in st.session_state:
            st.session_state['df_obs'] = self.get_frost_observations()
        self.df_obs = st.session_state['df_obs']

        if 'position_data' not in st.session_state:
            st.session_state['position_data'] = self.get_position_data()
        self.position_data = st.session_state['position_data']

        if 'marinas' not in st.session_state:
            st.session_state['marinas'] = self.get_json_data('marinas.json')
        self.marinas = st.session_state['marinas']

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
        st_folium(m, width=2000, height=500)

        
    



    def section2(self):
        for marina in self.preloaded_data:
            if marina['name'] == self.selected_marina:
                marina_name = marina['name']
                marina_coordinates = marina['coordinates']
                

                marina_time = marina['measurements']['time'][-1]
                marina_water_temperature = marina['measurements']['water_temperature'][-1]
                marina_water_heigth = marina['measurements']['water_heigth'][-1]
                marina_wind_speed = marina['measurements']['wind_speed'][-1]
                marina_wind_direction = marina['measurements']['wind_direction'][-1]
                marina_air_temperature = marina['measurements']['air_temperature'][-1]
                marina_air_pressure = marina['measurements']['air_pressure'][-1]
                marina_air_humidity = marina['measurements']['air_humidity'][-1]

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
        marina_time = marina_time.split('T')[0] + ' ' + marina_time.split('T')[1].split('+')[0]
        col1, col2, col3 = st.columns(3, vertical_alignment='center')
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>{marina_name}</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            boxed_text('Aktuelle Zeit', marina_time)
            st.divider()
            boxed_text('Wassertemperatur [°C]', round(marina_water_temperature, 3))
            st.divider()
            boxed_text('Wasserstand [m]', round(marina_water_heigth, 3))
            st.divider()
            boxed_text('Luft Temperatur [°C]', round(marina_air_temperature, 3))
            
            
                
            
        with col2:
            boxed_text('Wind Richtung [°]', round(marina_wind_direction,3 ))
            st.divider()
            boxed_text('Windgeschwindigkeit [km/h]', round(marina_wind_speed, 3))
            st.divider()
            boxed_text('Luftdruck [hPa]', round(marina_air_pressure, 3))
            st.divider()
            boxed_text('Luftfeuchtigkeit [%]', round(marina_air_humidity,3))
                       
            
            
        
        
        
        

    


    def section3(self):
        

        fig = go.Figure()

        marina_name = self.selected_marina
        for marina in self.preloaded_data:
            if marina['name'] == marina_name:
                marina_name = marina['name']
                marina_coordinates = marina['coordinates']
                

                marina_time = marina['measurements']['time']
                marina_water_temperature = marina['measurements']['water_temperature']
                marina_water_heigth = marina['measurements']['water_heigth']
                marina_wind_speed = marina['measurements']['wind_speed']
                marina_wind_direction = marina['measurements']['wind_direction']
                marina_air_temperature = marina['measurements']['air_temperature']
                marina_air_pressure = marina['measurements']['air_pressure']
                marina_air_humidity = marina['measurements']['air_humidity']
                break
        col1, col2, col3 = st.columns(3, vertical_alignment='center')
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>{marina_name}</h3>", unsafe_allow_html=True)

        def make_line_plot(x, y, title, x_label, y_label):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                name=title,
                line=dict(color='rgb(255, 102, 102)', 
                          width=2)
            ))

            fig.update_layout(
                title={'text': title, 'font': {'size': 20}},  # Titel größer
                xaxis={
                    'title': {'text': x_label, 'font': {'size': 18}},  # X-Achsenbeschriftung größer
                    'tickfont': {'size': 14}  # X-Achsenticks größer
                },
                yaxis={
                    'title': {'text': y_label, 'font': {'size': 18}},  # Y-Achsenbeschriftung größer
                    'tickfont': {'size': 14}  # Y-Achsenticks größer
                },
                template='plotly_white',
                hovermode='x unified'
            )

            return fig
        
        fig_names = ["Wassertemperatur", "Wasserstand", "Windgeschwindigkeit", "Windrichtung", "Lufttemperatur", "Luftdruck", "Luftfeuchtigkeit"]
        figures = []
        for name in fig_names:
            if name == "Wassertemperatur":
                fig = make_line_plot(marina_time, marina_water_temperature, "Wassertemperatur", "Zeit", "Temperatur [°C]")
                figures.append(fig)
            if name == "Wasserstand":
                fig = make_line_plot(marina_time, marina_water_heigth, "Wasserstand", "Zeit", "Wasserstand [m]")
                figures.append(fig)
            if name == "Windgeschwindigkeit":
                fig = make_line_plot(marina_time, marina_wind_speed, "Windgeschwindigkeit", "Zeit", "Windgeschwindigkeit [km/h]")
                figures.append(fig)
            if name == "Windrichtung":
                fig = make_line_plot(marina_time, marina_wind_direction, "Windrichtung", "Zeit", "Windrichtung [°]")
                figures.append(fig)
            if name == "Lufttemperatur":
                fig = make_line_plot(marina_time, marina_air_temperature, "Lufttemperatur", "Zeit", "Temperatur [°C]")
                figures.append(fig)
            if name == "Luftdruck":
                fig = make_line_plot(marina_time, marina_air_pressure, "Luftdruck", "Zeit", "Luftdruck [hPa]")
                figures.append(fig)
            if name == "Luftfeuchtigkeit":
                fig = make_line_plot(marina_time, marina_air_humidity, "Luftfeuchtigkeit", "Zeit", "Luftfeuchtigkeit [%]")
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

            #print('Get data')
            server = FrostServer(thing=thing)
            all_observations = server.get_all_observations()
            df_obs = pd.DataFrame(all_observations)
            df_obs["phenomenonTime"] = pd.to_datetime(df_obs["phenomenonTime"])
            df_obs["resultTime"] = pd.to_datetime(df_obs["resultTime"])
            # convert result to float
            df_obs["result"] = df_obs["result"].astype(float)
            return df_obs
            
        except Exception as e:
            print(e)


    def get_position_data(self):
        server = FrostServer()
        position_url = server.get_position_url()
        content = server.get_content(position_url)
        #print(content)
        return content
    


    def make_map(self):

        # Initialize a map centered around the coordinates
        m = folium.Map(
            
            # locatio to kiel
            location=[54.330123, 10.162420],
            width='100%',
            
           
            # zoom to Europa
            zoom_start=5,)
        
        for marina in self.preloaded_data:
            name = marina['name']
            coordinates = marina['coordinates']
            latitude = coordinates[1]
            longitude = coordinates[0]

            current_temp = marina['measurements']['water_temperature'][-1]
            current_temp = round(current_temp, 2)

            # Add a T-Box 
            folium.Marker(
                [latitude, longitude],
                popup=f"{name} \n Aktuelle Temperatur: {current_temp}°C",
                tooltip=f'{name}',
                icon=folium.Icon(icon="info-sign", color="lightred")
            ).add_to(m)


        return m
    

    def preload_data(self):

        today = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        one_week_before = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 60*60*24*7))
        output_filename = 'subset_output.nc'

        # Get ALL Timeseries data from FROST-Server
        server = FrostServer(thing="Things(3)")
        all_observations = server.get_all_observations()
        df_water_temperature = pd.DataFrame(all_observations)
        df_water_temperature["phenomenonTime"] = pd.to_datetime(df_water_temperature["phenomenonTime"])
        df_water_temperature["resultTime"] = pd.to_datetime(df_water_temperature["resultTime"])
        df_water_temperature["phenomenonTime"] = df_water_temperature["phenomenonTime"].dt.round('h') # round phenomenonTime to YYYY-MM-DD HH:MM:SS
        df_water_temperature["result"] = df_water_temperature["result"].astype(float)
        df_water_temperature = df_water_temperature.loc[:, ['phenomenonTime', 'result']].drop_duplicates()

        # Get position data of T-Box
        position_url = server.get_position_url()
        content = server.get_content(position_url)
        coordinates_t_box =  content['value'][0]['location']['coordinates']
        longitude, latitude = coordinates_t_box[0], coordinates_t_box[1]

        thing_name = server.get_thing_name()


        start_datetime = df_water_temperature["phenomenonTime"].min()
        start_datetime = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        start_datetime = start_datetime.split(' ')[0]

        end_datetime = today.split(' ')[0]

        # get weather data
        omw = OpenMeteoWeather(latitude=latitude, 
                        longitude=longitude, 
                        start_date=start_datetime, 
                        end_date=end_datetime
                        )
        df_omw = omw.get_weather_dataframe()

        cols = ['date', 'wind_speed_10m', 'wind_direction_10m', 'temperature_2m', 'pressure_msl', 'relative_humidity_2m']
        df_omw = df_omw[cols]
        df_omw["date"] = pd.to_datetime(df_omw["date"])

        marina_radius = 0.1

        minimum_longitude = longitude - marina_radius
        maximum_longitude = longitude + marina_radius

        minimum_latitude = latitude - marina_radius
        maximum_latitude = latitude + marina_radius

        marina_data = ac.get_subset(
                dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
                dataset_version="202406",
                variables=["so", "thetao", "vo", "zos", "uo"], 
                minimum_longitude=minimum_longitude,
                maximum_longitude=maximum_longitude,
                minimum_latitude=minimum_latitude,
                maximum_latitude=maximum_latitude,
                start_datetime=one_week_before,
                end_datetime=today,
                minimum_depth=0.49402499198913574,
                maximum_depth=0.49402499198913574,
                coordinates_selection_method="strict-inside",
                disable_progress_bar=False,
                output_filename=output_filename
                )
        ac.delete_dataset(output_filename)

        marina_df = marina_data.to_dataframe().reset_index()
        marina_df = marina_df.dropna(axis=0, how='any')
        marina_df_grouped = marina_df.groupby('time').mean().reset_index()
        marina_df_grouped.sort_values(by='time', ascending=False, inplace=True)
        marina_df_grouped['time'] = pd.to_datetime(marina_df_grouped['time']).dt.tz_localize('UTC')


        #merge weather data with water temperature data
        df_merged = pd.merge(df_water_temperature, df_omw, left_on='phenomenonTime', right_on='date', how='left').drop('date', axis=1)
        # merge df_merge with marina data
        df_merged = pd.merge(df_merged, marina_df_grouped, left_on='phenomenonTime', right_on='time', how='left').drop('time', axis=1)

        # convert datetime to isoformat
        df_merged["phenomenonTime"] = df_merged["phenomenonTime"].apply(lambda x: x.isoformat())


    
        preload_data = [{
            'name': thing_name,
            'coordinates': coordinates_t_box,
            'measurements': {
                'time': df_merged['phenomenonTime'].tolist(),
                'water_temperature': df_merged['result'].tolist(),
                'water_heigth': df_merged['zos'].tolist(),
                'wind_speed': df_merged['wind_speed_10m'].tolist(),
                'wind_direction': df_merged['wind_direction_10m'].tolist(),
                'air_temperature': df_merged['temperature_2m'].tolist(),
                'air_pressure': df_merged['pressure_msl'].tolist(),
                'air_humidity': df_merged['relative_humidity_2m'].tolist()
                
            }
        }]
        
        # Preload marinas from marinas.json

        marinas = self.get_json_data('marinas.json')
        for marina in marinas:
            marina_name = marina['name']
            marina_latitude = marina['location']['latitude']
            marina_longitude = marina['location']['longitude']
            marina_radius = 0.1

            minimum_longitude = marina_longitude - marina_radius
            maximum_longitude = marina_longitude + marina_radius

            minimum_latitude = marina_latitude - marina_radius
            maximum_latitude = marina_latitude + marina_radius

            marina_data = ac.get_subset(
                dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
                dataset_version="202406",
                variables=["so", "thetao", "vo", "zos", "uo"], 
                minimum_longitude=minimum_longitude,
                maximum_longitude=maximum_longitude,
                minimum_latitude=minimum_latitude,
                maximum_latitude=maximum_latitude,
                start_datetime=one_week_before,
                end_datetime=today,
                minimum_depth=0.49402499198913574,
                maximum_depth=0.49402499198913574,
                coordinates_selection_method="strict-inside",
                disable_progress_bar=False,
                output_filename=output_filename
                )
            ac.delete_dataset(output_filename)

            marina_df = marina_data.to_dataframe().reset_index()
            marina_df = marina_df.dropna(axis=0, how='any')
            marina_df_grouped = marina_df.groupby('time').mean().reset_index()
            marina_df_grouped.sort_values(by='time', ascending=False, inplace=True)
            marina_df_grouped['time'] = pd.to_datetime(marina_df_grouped['time']).dt.tz_localize('UTC')

            omw = OpenMeteoWeather(latitude=marina_latitude, 
                        longitude=marina_longitude, 
                        start_date=start_datetime, 
                        end_date=end_datetime
                        )
            df_omw = omw.get_weather_dataframe()

            cols = ['date', 'wind_speed_10m', 'wind_direction_10m', 'temperature_2m', 'pressure_msl', 'relative_humidity_2m']
            df_omw = df_omw[cols]
            df_omw["date"] = pd.to_datetime(df_omw["date"])

            #merge weather data with water temperature data
            df_merged = pd.merge(marina_df_grouped, df_omw, left_on='time', right_on='date', how='left').drop('date', axis=1)

            marina_df_grouped["time"] = marina_df_grouped["time"].apply(lambda x: x.isoformat())

            marina_data = {
                'name': marina_name,
                'coordinates': [marina_longitude, marina_latitude],
                'measurements': {
                    'time': marina_df_grouped['time'].tolist(),
                    'water_temperature': marina_df_grouped['thetao'].tolist(),
                    'water_heigth': marina_df_grouped['zos'].tolist(),
                    'wind_speed': df_merged['wind_speed_10m'].tolist(),
                    'wind_direction': df_merged['wind_direction_10m'].tolist(),
                    'air_temperature': df_merged['temperature_2m'].tolist(),
                    'air_pressure': df_merged['pressure_msl'].tolist(),
                    'air_humidity': df_merged['relative_humidity_2m'].tolist()
                }
            }


            preload_data.append(marina_data)
            #print(preload_data[0]['measurements'].keys())
            #break

        # # # save reload_data to json file
        # with open('preload_data.json', 'w') as f:
        #     json.dump(preload_data, f, indent=4, ensure_ascii=True)
        
        





        return preload_data




    def run_streamlit(self):
        subprocess.run([sys.executable, "-m", "streamlit", "run", "Layout.py"])

if __name__ == '__main__':

    app = StreamlitApp()
    app.header()
    #app.sidebar()
