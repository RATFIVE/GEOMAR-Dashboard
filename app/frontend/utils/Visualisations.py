import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
import json
import numpy as np
from folium import Marker, Popup



# -----------------------------------

# Map function

class ShowMap:
    def __init__(self, data:dict, zoom:int=7, control_scale:bool=False):
        self.data = data
        self.zoom = zoom
        self.control_scale = control_scale


    

    def plot(self):
        """Generates a Plotly map with markers for marinas, displaying water temperature."""
        
        # Daten extrahieren
        latitudes = [marina.get("location", {}).get("latitude") for marina in self.data]
        longitudes = [marina.get("location", {}).get("longitude") for marina in self.data]
        names = [marina.get("name", "Unknown Marina") for marina in self.data]
        temperatures = []

        for marina in self.data:
            measurement = marina.get("measurement", {})
            water_temp_data = measurement.get("water_temperature")

            if water_temp_data:
                df = pd.DataFrame.from_dict(water_temp_data)
                df["time"] = pd.to_datetime(df["time"], errors="coerce")
                df["values"] = pd.to_numeric(df["values"], errors="coerce")
                df.dropna(inplace=True)
                df.sort_values(by="time", ascending=False, inplace=True)
                
                if not df.empty:
                    temperatures.append(round(df["values"].iloc[0], 2))
                else:
                    temperatures.append(None)
            else:
                temperatures.append(None)

        # DataFrame für Plotly erstellen
        df_map = pd.DataFrame({
            "Latitude": latitudes,
            "Longitude": longitudes,
            "Name": names,
            "Temperature": temperatures
        }).dropna()

        # Mittlere Koordinaten für Karten-Zentrierung berechnen
        lat_mean = df_map["Latitude"].mean()
        lon_mean = df_map["Longitude"].mean()

        m = folium.Map(location=[lat_mean, lon_mean], zoom_start=self.zoom, control_scale=self.control_scale)
        # Erstelle die Karte mit Plotly
        fig = go.Figure()
        # Add markers to map
        for i, row in df_map.iterrows():
            name = row["Name"]
            lat = row["Latitude"]
            lon = row["Longitude"]
            temp = row["Temperature"]

            # Custom HTML popup
            popup_html = f"""
                <div style="font-family: Arial; text-align: center;">
                    <b>{name}</b><br>
                    <hr style="margin: 5px 0;">
                    <b>Temperatur:</b> {temp}°C
                </div>
            """

            # Marker(
            #     [lat, lon],
            #     popup=Popup(popup_html, max_width=300),
            #     tooltip=name,
            #     icon=folium.Icon(icon="info-sign", color="lightred")
            # ).add_to(m)



            fig.add_trace(go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode="markers",

                marker=dict(
                        size=30,
                        color='red',
                        # symbol="marker",  # Alternativ "marker" oder "harbor"
                ),
            # text=labels  # Text für die Marker
            ))

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": 54.3233, "lon": 10.1228},
            mapbox_zoom=7,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=500
        )
        return fig
    




        # fig = go.Figure(go.Scattermap(
        # lat=df_map["Latitude"],
        # lon=df_map["Longitude"],
        # mode='markers',
        # marker=go.scattermap.Marker(
        #     size=30,
            
        #     color='rgb(255, 0, 0)',
        #     symbol='marker'
        #     #symbol='harbor'

        # ),
        # text=df_map["Name"],
        #     ))

        # fig.update_layout(
        #     #autosize=True,
        #     height=500,
        #     hovermode='closest',
        #     map=dict(
        #         bearing=0,
        #         center=dict(
        #             lat=lat_mean,
        #             lon=lon_mean
        #         ),
        #         pitch=0,
        #         zoom=self.zoom
        #     ),
        # )

        # return fig


    




class LinePlot:
    def __init__(self, x, y, title, x_label, y_label):
        self.x = x
        self.y = y
        self.x_label = x_label
        self.y_label = y_label
        self.title = title


    def plot(self):
        fig = go.Figure([go.Scatter(x=self.x, y=self.y, mode="lines", name=self.title,line=dict(color='rgb(255, 102, 102)', width=2))])
        fig.update_layout(
                title={'text': self.title, 'font': {'size': 20}},  # Titel größer
                xaxis={'title': {'text': self.x_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  # X-Achse größer
                yaxis={'title': {'text': self.y_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  # Y-Achse größer
                template='plotly_white',
                hovermode='x unified'
            )
        return fig




    
class Windrose:
    def __init__(self, data):
        self.data = data
    

    def plot(self):
        

        # Beispiel-Daten: Windrichtung in Grad (0° = N, 90° = E, 180° = S, 270° = W)
        wind_directions = [316]  # Nord
        wind_speeds = [21,3]  # Windgeschwindigkeit

        # Erstellen des Plots
        fig = go.Figure()

        fig.add_trace(go.Barpolar(
            r=wind_speeds,  # Windgeschwindigkeit als Radius
            theta=wind_directions,  # Windrichtung in Grad
            width=45,  # Breite der Balken (45° für 8 Himmelsrichtungen)
            marker=dict(
                color=wind_speeds,
                colorscale='Reds',  
                showscale=True,
                cmin=0,  # Minimaler Wert der Skala
                cmax=50,  # Maximaler Wert der Skala
                colorbar=dict(
                    x=1,  # Position der Skala
                    y=0.5,  # Vertikale Position
                    len=1.7,  # Höhe der Skala
                    title="Wind (m/s)",  # Titel der Skala
                    tickvals=[0, 10, 20, 30, 40, 50, 100],  # Definierte Werte
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