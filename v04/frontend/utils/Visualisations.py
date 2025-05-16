import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pprint import pprint
import folium
from streamlit_folium import st_folium
from folium import Popup, IFrame

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

    def extract_measurements(self, marina: dict, measurement_key:str) -> float | None:
        """
        Extrahiert die aktuellste verfügbare Wassertemperatur aus den Messwerten einer Marina.

        :param marina: Dictionary mit Messwerten der Marina.
        :return: Letzte bekannte Wassertemperatur oder None, falls keine verfügbar.
        """
        measurement = marina.get("measurement", {})
        water_temp_data = measurement.get(measurement_key)

        if water_temp_data:
            df = pd.DataFrame.from_dict(water_temp_data)
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            df["values"] = pd.to_numeric(df["values"], errors="coerce")
            df.dropna(inplace=True)
            df.sort_values(by="time", ascending=False, inplace=True)

            return round(df["values"].iloc[0], 2) if not df.empty else None
        return None

    def plot(self):
        m = folium.Map(location=[54.3323, 10.1519], zoom_start=self.zoom)

        for marina in self.data:
            loc = marina["locations"][0]["location"]["coordinates"]
            lat, lon = loc[1], loc[0]

            # Popup-HTML zusammenbauen
            ds = marina.get("datastreams", [])
            popup_html = "<br>".join(
                f"{ds_item['name'].split('*')[0].strip().capitalize().replace('_', ' ')}: "
                f"{ds_item['observations']['values'][0]} "
                f"{ds_item.get('unitOfMeasurement',{}).get('symbol','')}"
                for ds_item in ds if ds_item.get("observations",{}).get("values")
            )

            # 1) Einfaches Popup mit max_width
            popup = Popup(popup_html, max_width=400)

            # Alternativ 2) IFrame, um auch Höhe zu steuern und HTML komplexer zu gestalten:
            # iframe = IFrame(html=popup_html, width=300, height=150)
            # popup = Popup(iframe, max_width=400)

            folium.Marker(
                location=(lat, lon),
                tooltip=marina["name"],
                popup=popup,
            ).add_to(m)

        return m

      


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
        fig = go.Figure(
            [
                go.Scatter(
                    x=self.x,
                    y=self.y,
                    mode="lines",
                    name=self.title,
                    line=dict(color="rgb(255, 102, 102)", width=2),
                )
            ]
        )

        # Dropdown-Menü für Zeitausschnitte
        fig.update_layout(
            title={"text": self.title, "font": {"size": 20}},
            xaxis={
                "title": {"text": self.x_label, "font": {"size": 18}},
                "tickfont": {"size": 14},
            },
            yaxis={
                "title": {"text": self.y_label, "font": {"size": 18}},
                "tickfont": {"size": 14},
            },
            template="plotly_white",
            hovermode="x unified",
            updatemenus=[
                dict(
                    type="buttons",
                    x=1.05,  # Position der Buttons außerhalb des Plots (rechts)
                    y=1,  # Position der Buttons oberhalb des Plots
                    xanchor="left",  # Verankerung der Buttons an der linken Seite
                    yanchor="top",  # Verankerung der Buttons an der oberen Seite
                    showactive=False,
                    direction="down",  # Die Buttons werden untereinander angezeigt
                    buttons=[
                        dict(
                            label="Letzte 24 Stunden",
                            method="relayout",
                            args=[
                                "xaxis.range",
                                [self.x.max() - pd.Timedelta(days=1), self.x.max()],
                            ],
                        ),
                        dict(
                            label="Letzte 7 Tage",
                            method="relayout",
                            args=[
                                "xaxis.range",
                                [self.x.max() - pd.Timedelta(days=7), self.x.max()],
                            ],
                        ),
                        dict(
                            label="Letzter Monat",
                            method="relayout",
                            args=[
                                "xaxis.range",
                                [self.x.max() - pd.Timedelta(days=31), self.x.max()],
                            ],
                        ),
                        dict(
                            label="Letztes Jahr",
                            method="relayout",
                            args=[
                                "xaxis.range",
                                [self.x.max() - pd.Timedelta(days=365), self.x.max()],
                            ],
                        ),
                    ],
                )
            ],
        )

        return fig


class Windrose:
    def __init__(self, data):
        self.data = data

    def plot(self):
        # Beispiel-Daten: Windrichtung in Grad (0° = N, 90° = E, 180° = S, 270° = W)
        wind_directions = [316]  # Nord
        wind_speeds = [21, 3]  # Windgeschwindigkeit

        # Erstellen des Plots
        fig = go.Figure()

        fig.add_trace(
            go.Barpolar(
                r=wind_speeds,  # Windgeschwindigkeit als Radius
                theta=wind_directions,  # Windrichtung in Grad
                width=45,  # Breite der Balken (45° für 8 Himmelsrichtungen)
                marker=dict(
                    color=wind_speeds,
                    colorscale="Reds",
                    showscale=True,
                    cmin=0,  # Minimaler Wert der Skala
                    cmax=50,  # Maximaler Wert der Skala
                    colorbar=dict(
                        x=1,  # Position der Skala
                        y=0.5,  # Vertikale Position
                        len=1.7,  # Höhe der Skala
                        title="Wind (m/s)",  # Titel der Skala
                        tickvals=[0, 10, 20, 30, 40, 50, 100],  # Definierte Werte
                        # ticktext=["0", "Leicht", "Mittel", "Stark", "Sehr stark", "Extrem"]  # Eigene Labels
                    ),
                ),
            )
        )

        # Theme anwenden
        fig.update_layout(
            plot_bgcolor="#78d278",  # Hintergrund des Plots
            font=dict(color="#053246"),  # Allgemeine Textfarbe
            # size
            width=300,
            height=300,
            polar=dict(
                radialaxis=dict(showticklabels=False, ticksuffix=" m/s"),
                angularaxis=dict(
                    direction="clockwise",
                    tickmode="array",
                    tickvals=[0, 90, 180, 270],
                    ticktext=["N", "E", "S", "W"],
                ),  # Himmelsrichtungen
            ),
        )

        return fig


if __name__ == "__main__":
    test_data = [{'@iot.id': 3,
  'datastreams': [{'description': 'WTemp c7991906-983b-4bf3-849f-14a139ffe4f3',
                   'id': 1,
                   'name': 'WTemp* measured by sensor '
                           '*c7991906-983b-4bf3-849f-14a139ffe4f3*',
                   'observations': {'time': ['2025-05-13 10:36:59',
                                             '2025-05-13 09:37:00',
                                             '2025-05-13 08:37:04',
                                             '2025-05-13 07:37:19',
                                             '2025-05-13 06:37:09'],
                                    'values': [14.62,
                                               14.37,
                                               14.18,
                                               14.0,
                                               13.87]}}],
  'description': 'LoRaWan box for temperature at Kiel, Reventlou.',
  'locations': [{'@iot.id': 1,
                 '@iot.selfLink': 'https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)',
                 'HistoricalLocations@iot.navigationLink': 'https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)/HistoricalLocations',
                 'Things@iot.navigationLink': 'https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)/Things',
                 'description': 'Measuring point',
                 'encodingType': 'application/geo+json',
                 'location': {'coordinates': [10.1519, 54.3323],
                              'type': 'Point'},
                 'name': 'Position lat 54.3323, lon 10.1519'}],
  'name': 'Badesteg Reventlou'},
 ]


    map = ShowMap(test_data)
    m = map.plot()
    st_folium(m, width=500)
    # Display folium map in browser
    #m.save("map.html")

    # Test von Line plot

    # Erstellen von Testdaten
    # Angenommen, die x-Achse ist ein Zeitraum von einem Jahr und y sind zufällige Werte.
    # date_range = pd.date_range(start="2023-03-21", end="2024-03-21", freq="h")
    # y_values = np.random.randn(len(date_range))  # Zufällige Daten für y-Werte

    # # Die Testdaten für die LinePlot-Klasse
    # x_test = date_range
    # y_test = y_values
    # title_test = "Testdaten für LinePlot"
    # x_label_test = "Zeit"
    # y_label_test = "Wert"

    # # Rückgabe der Testdaten
    # # x_test, y_test, title_test, x_label_test, y_label_test

    # line_plot = LinePlot(x_test, y_test, title_test, x_label_test, y_label_test)
    # fig = line_plot.plot()
    # fig.show()
