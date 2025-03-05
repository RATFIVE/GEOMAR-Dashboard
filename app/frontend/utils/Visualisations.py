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
        """Generates a Folium map with markers for marinas, displaying water temperature."""
        
        # Get the averate latitude and longitude of all marinas
        latitudes = [marina.get("location", {}).get("latitude") for marina in self.data]
        longitudes = [marina.get("location", {}).get("longitude") for marina in self.data]

        latitude_mean = np.mean([lat for lat in latitudes if lat is not None])
        longitude_mean = np.mean([lon for lon in longitudes if lon is not None])

        print(f"Centering map on {latitude_mean}, {longitude_mean}")

        # Initialize map centered on Kiel
        m = folium.Map(location=[latitude_mean, longitude_mean], 
                       zoom_start=self.zoom, control_scale=self.control_scale)
        
        for marina in self.data:
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