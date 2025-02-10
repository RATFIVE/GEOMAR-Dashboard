import Layout as st
import pandas as pd
import numpy as np
import sys
import subprocess
from frost_server import FrostServer
from vis import make_line_plot, make_map
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import time 
from streamlit_folium import st_folium



class StreamlitApp:

    def __init__(self):
        #self.fig = fig
        self.df_obs = self.get_data()
        self.position_data = self.get_position_data()
        

    def header(self):
        
        st.markdown("""<h1 style="text-align: center;">Förde - Temperaturdaten</h1>""", unsafe_allow_html=True)
        st.divider()

        st.markdown("""<h2 style="text-align: center;">Akutelle Daten</h2>""", unsafe_allow_html=True)
        self.section1()
        st.divider()

        st.markdown("""<h2 style="text-align: center;">Karte</h2>""", unsafe_allow_html=True)
        self.section2()
        st.divider()

        st.markdown("""<h2 style="text-align: center;">Visualisierung von Temperaturdaten</h2>""", unsafe_allow_html=True)
        self.section3()
        st.divider()

    
    def section1(self):

        current_temp, current_time = self.get_current_temperature_and_time()
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f'Current Temp: {current_temp}\nCurrent Time: {current_time}')
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            st.markdown(f"<h4> Aktuelle Temperatur: {current_temp}°C um {current_time}</h4>", unsafe_allow_html=True)

    

    def section2(self):
        #print(data)
        m = make_map(self.position_data)
        st_folium(m, width=1000, height=500)


    def section3(self):
        fig = make_line_plot(self.df_obs)
        st.plotly_chart(fig)


    
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
            
        
        



    def run_streamlit(self):
        subprocess.run([sys.executable, "-m", "streamlit", "run", "Layout.py"])

if __name__ == '__main__':

    app = StreamlitApp()
    app.header()
    app.sidebar()
