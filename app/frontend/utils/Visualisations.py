import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
import json
import numpy as np
from folium import Marker, Popup



# -----------------------------------
class ShowMap:
    def __init__(self, data: list[dict], zoom: int = 7, control_scale: bool = False):
        """
        Initialisiert die Klasse zur Darstellung einer Karte mit Marinas.
        
        :param data: Liste von Marinas mit Standort- und Messwertinformationen.
        :param zoom: Zoom-Stufe der Karte.
        :param control_scale: Ob eine Skalierungssteuerung angezeigt werden soll.
        """
        self.data = data
        self.zoom = zoom
        self.control_scale = control_scale

    def extract_temperature(self, marina: dict) -> float | None:
        """
        Extrahiert die aktuellste verfügbare Wassertemperatur aus den Messwerten einer Marina.
        
        :param marina: Dictionary mit Messwerten der Marina.
        :return: Letzte bekannte Wassertemperatur oder None, falls keine verfügbar.
        """
        measurement = marina.get("measurement", {})
        water_temp_data = measurement.get("water_temperature")
        
        if water_temp_data:
            df = pd.DataFrame.from_dict(water_temp_data)
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            df["values"] = pd.to_numeric(df["values"], errors="coerce")
            df.dropna(inplace=True)
            df.sort_values(by="time", ascending=False, inplace=True)
            
            return round(df["values"].iloc[0], 2) if not df.empty else None
        return None

    def plot(self):
        """
        Erstellt eine interaktive Karte mit den Marinas und deren Wassertemperatur.
        """
        # Standort- und Temperaturdaten extrahieren
        latitudes = [marina.get("location", {}).get("latitude") for marina in self.data]
        longitudes = [marina.get("location", {}).get("longitude") for marina in self.data]
        names = [marina.get("name", "Unknown Marina") for marina in self.data]
        temperatures = [self.extract_temperature(marina) for marina in self.data]

        # DataFrame für die Karte erstellen
        df_map = pd.DataFrame({
            "Latitude": latitudes,
            "Longitude": longitudes,
            "Name": names,
            "Temperature": temperatures
        }).dropna()

        # Falls keine Daten vorhanden sind, abbrechen
        if df_map.empty:
            print("Keine gültigen Daten für die Karte verfügbar.")
            return

        # Mittelwerte für die Karten-Zentrierung berechnen
        lat_mean = df_map["Latitude"].mean()
        lon_mean = df_map["Longitude"].mean()

        # Individuelle Hover-Informationen erstellen
        df_map["hover_name"] = df_map.apply(
            lambda row: f"{row['Name']}<br>Temperatur: {row['Temperature']}°C", axis=1
        )

        df_map['size'] = 20  # Einheitliche Punktgröße

        # Hex-Farbe in RGB umwandeln
        hex_color = "#78d278"
        rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

        # Karte mit Plotly erstellen
        fig = px.scatter_map(
            df_map,
            lat="Latitude",
            lon="Longitude",
            hover_name="hover_name",
            hover_data={"Latitude": False, "Longitude": False, "size": False},
            color_discrete_sequence=[f"rgb(255, 102, 102)"],
            size='size',
            zoom=self.zoom,
            height=500
        )

        # Layout der Karte anpassen
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": lat_mean, "lon": lon_mean},
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        return fig
    






    



class LinePlot:
    def __init__(self, x, y, title, x_label, y_label):
        self.x = x
        self.y = y
        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        
        # Konvertiere x in ein Datetime-Format, falls es nicht bereits ist
        self.x = pd.to_datetime(self.x)

    def plot(self):
        # Erstelle den Plot
        fig = go.Figure([go.Scatter(x=self.x, y=self.y, mode="lines", name=self.title, line=dict(color='rgb(255, 102, 102)', width=2))])

        # Dropdown-Menü für Zeitausschnitte
        fig.update_layout(
            title={'text': self.title, 'font': {'size': 20}},  
            xaxis={'title': {'text': self.x_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  
            yaxis={'title': {'text': self.y_label, 'font': {'size': 18}}, 'tickfont': {'size': 14}},  
            template='plotly_white',
            hovermode='x unified',
            updatemenus=[dict(
                type="buttons",
                x=1.05,  # Position der Buttons außerhalb des Plots (rechts)
                y=1,      # Position der Buttons oberhalb des Plots
                xanchor="left",  # Verankerung der Buttons an der linken Seite
                yanchor="top",   # Verankerung der Buttons an der oberen Seite
                showactive=False,
                direction="down",  # Die Buttons werden untereinander angezeigt
                buttons=[
                    dict(
                        label="Letzte 24 Stunden",
                        method="relayout",
                        args=["xaxis.range", [self.x.max() - pd.Timedelta(days=1), self.x.max()]]
                    ),
                    dict(
                        label="Letzte 7 Tage",
                        method="relayout",
                        args=["xaxis.range", [self.x.max() - pd.Timedelta(days=7), self.x.max()]]
                    ),
                    dict(
                        label="Letzter Monat",
                        method="relayout",
                        args=["xaxis.range", [self.x.max() - pd.Timedelta(days=31), self.x.max()]]
                    ),
                    dict(
                        label="Letztes Jahr",
                        method="relayout",
                        args=["xaxis.range", [self.x.max() - pd.Timedelta(days=365), self.x.max()]]
                    )
                ]
            )]
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
    

if __name__ == '__main__':
    test_data = [
        {
            "name": "Marina Kiel",
            "location": {"latitude": 54.321, "longitude": 10.134},
            "measurement": {
                "water_temperature": [
                    {"time": "2025-03-19T12:00:00Z", "values": 6.3},
                    {"time": "2025-03-18T12:00:00Z", "values": 6.1}
                ]
            }
        },
        {
            "name": "Marina Lübeck",
            "location": {"latitude": 53.869, "longitude": 10.687},
            "measurement": {
                "water_temperature": [
                    {"time": "2025-03-19T12:00:00Z", "values": 5.8},
                    {"time": "2025-03-18T12:00:00Z", "values": 5.5}
                ]
            }
        },
        {
            "name": "Marina Flensburg",
            "location": {"latitude": 54.793, "longitude": 9.433},
            "measurement": {
                "water_temperature": [
                    {"time": "2025-03-19T12:00:00Z", "values": 4.9},
                    {"time": "2025-03-18T12:00:00Z", "values": 4.7}
                ]
            }
        }
    ]

    # map = ShowMap(test_data)
    # map.plot().show()


    # Test von Line plot


    # Erstellen von Testdaten
    # Angenommen, die x-Achse ist ein Zeitraum von einem Jahr und y sind zufällige Werte.
    date_range = pd.date_range(start="2023-03-21", end="2024-03-21", freq="h")
    y_values = np.random.randn(len(date_range))  # Zufällige Daten für y-Werte

    # Die Testdaten für die LinePlot-Klasse
    x_test = date_range
    y_test = y_values
    title_test = "Testdaten für LinePlot"
    x_label_test = "Zeit"
    y_label_test = "Wert"

    # Rückgabe der Testdaten
    #x_test, y_test, title_test, x_label_test, y_label_test

    line_plot = LinePlot(x_test, y_test, title_test, x_label_test, y_label_test)
    fig = line_plot.plot()
    fig.show()