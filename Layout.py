import Layout as st
import pandas as pd
import numpy as np
import sys
import subprocess
from utils.frost_server import FrostServer
from vis import make_line_plot, make_map
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import time 
from streamlit_folium import st_folium
import json
import folium
from utils.Copernicus import AdvancedCopernicus as ac


ac = ac() 


class StreamlitApp:

    def __init__(self):
        #self.fig = fig
        self.df_obs = self.get_data()
        self.position_data = self.get_position_data()
        self.marinas = self.get_json_data('marinas.json')
        

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
        # get all marinas names as list
        marinas = []
        for marina in self.marinas:
            marinas.append(marina['name'])
        self.selected_marina = st.selectbox(label='Wähle den Hafen aus:', options=marinas)

        m = self.make_map()
        st_folium(m, width=1000, height=500)

        
    



    def section2(self):

        if self.selected_marina == 'Badesteg Reventlou':
            position_data = self.get_position_data()
            coordinates = position_data["value"][0]["location"]["coordinates"]
            longitude, latitude = coordinates[0], coordinates[1]

            current_temp, current_time = self.get_current_temperature_and_time()
            current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # get position data of selected marina
            for marina in self.marinas:
                if marina['name'] == self.selected_marina:

                    # find name = Hafen Flensburg Sonwik in marinas.json
                    def find_marina(name, marinas):
                        return [marina for marina in marinas if marina['name'] == name][0]

                    marina = find_marina(marina['name'], self.marinas)


                    marina_name = marina['name']
                    marina_latitude = marina['location']['latitude']
                    marina_longitude = marina['location']['longitude']
                    marina_radius = 0.1

                    # st.write(f"Marina: {marina_name}")
                    # st.write(f"Latitude: {marina_latitude}")
                    # st.write(f"Longitude: {marina_longitude}")

                    minimum_longitude = marina_longitude - marina_radius
                    maximum_longitude = marina_longitude + marina_radius

                    minimum_latitude = marina_latitude - marina_radius
                    maximum_latitude = marina_latitude + marina_radius

                    today = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    one_week_before = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 60*60*24*7))
                    output_filename = 'subset_output.nc'

                    # so: Sea water salinityso [/ 103]
                    # thetao: Sea water potential temperaturethetao [°C]
                    # vo: Northward sea water velocityvo [m/s]
                    # zos: Sea surface height above geoidzos [m]
                    # uo: Eastward sea water velocityuo [m/s]

                    self.marina_data = ac.get_subset(
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
                    
                    marina_df = self.marina_data.to_dataframe().reset_index()
                    marina_df = marina_df.dropna(axis=0, how='any')
                    marina_df_grouped = marina_df.groupby('time').mean().reset_index()
                    marina_df_grouped.sort_values(by='time', ascending=False, inplace=True)

                    def round_data(data, digits=5):
                        data = round(float(data), digits)
                        return data
                    
                    # get current temperature
                    current_thetao = round_data(marina_df_grouped['thetao'].iloc[0])
                    current_so = round_data(marina_df_grouped['so'].iloc[0])
                    current_uo = round_data(marina_df_grouped['uo'].iloc[0])
                    current_vo = round_data(marina_df_grouped['vo'].iloc[0])
                    current_zos = round_data(marina_df_grouped['zos'].iloc[0])

                    current_time = marina_df_grouped['time'].iloc[0]

                    ac.delete_dataset(output_filename)

                    break



        def boxed_text(text, value):
            with st.container():
                st.markdown(
                    f"""
                    <div style="text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 10px;">
                        {text}:
                    </div>
                    <div style="display: flex; justify-content: center;">
                        <pre style="
                            background-color: #f0f0f0;
                            padding: 10px;
                            border-radius: 5px;
                            border: 1px solid #ddd;
                            text-align: left;
                            width: fit-content;
                            max-width: 80%;
                            white-space: pre-wrap;
                            word-wrap: break-word;
                        ">
                    {value}
                        </pre>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        
        col1, col2 = st.columns(2)
        with col1:
            boxed_text('Aktuelle Zeit', current_time)
            st.divider()
            boxed_text('Wassertemperatur [°C]', current_thetao)
            st.divider()
            boxed_text('Salinität [/10³]', current_so)
                
            
        with col2:
            boxed_text('Nördliche Wassergeschwindigkeit [m/s]', current_vo)
            st.divider()
            boxed_text('Östliche Wassergeschwindigkeit [m/s]', current_uo)
            st.divider()
            boxed_text('Seeoberflächenhöhe [m]', current_zos)
                       
            
            
        
        
        
        

    


    def section3(self):
        fig = go.Figure()

        if self.selected_marina == 'Badesteg Reventlou':
            self.df_obs = self.get_data()

            # get the last 7 days
            last_7_days = self.df_obs["phenomenonTime"].iloc[-1] - pd.DateOffset(days=7)
            df_obs_last_7_days = self.df_obs[self.df_obs["phenomenonTime"] >= last_7_days]


            fig.add_trace(go.Scatter(
                x=df_obs_last_7_days["phenomenonTime"],
                y=df_obs_last_7_days["result"],
                mode='lines',
                name='Temperature'
            ))
        else:
            marina_data = self.marina_data.to_dataframe().reset_index()
            marina_data = marina_data.dropna(axis=0, how='any')
            marina_data_grouped = marina_data.groupby('time').mean().reset_index()
            marina_data_grouped.sort_values(by='time', ascending=False, inplace=True)

            fig.add_trace(go.Scatter(
                x=marina_data_grouped['time'],
                y=marina_data_grouped['thetao'],
                mode='lines',
                name='Temperature'
            ))



        # fig = make_line_plot(self.df_obs)

        


        fig.update_layout(
            title='Temperature Over Time',
            xaxis_title='Time',
            yaxis_title='Temperature',
            template='plotly_white',
            hovermode='x unified'
        )

        st.plotly_chart(fig)




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


    def get_data(self, thing="Things(3)"):
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
            
            # locatio to middle of Germany
            location=[51.1657, 10.4515],
           
            # zoom to Europa
            zoom_start=5,)

        # T- Box
        coordinates = self.position_data["value"][0]["location"]["coordinates"]
        name = self.position_data["value"][0]["name"]
        
        longitude, latitude = coordinates[0], coordinates[1]

        current_temp, current_time = self.get_current_temperature_and_time()

        # Add a T-Box 
        folium.Marker(
            [latitude, longitude],
            popup=f"{name} Pos: {latitude}, {longitude} \n Akteulle Temperatur: {current_temp}°C",
            tooltip=f'{name}'
        ).add_to(m)

        # Add coordinates of marinas
        for marina in self.marinas:
            latitude = marina['location']['latitude']
            longitude = marina['location']['longitude']
            name = marina['name']
            folium.Marker(
                [latitude, longitude],
                popup=f"{name}",
                tooltip=f"{name}"
            ).add_to(m)
            

        return m
            
        
        



    def run_streamlit(self):
        subprocess.run([sys.executable, "-m", "streamlit", "run", "Layout.py"])

if __name__ == '__main__':

    app = StreamlitApp()
    app.header()
    #app.sidebar()
