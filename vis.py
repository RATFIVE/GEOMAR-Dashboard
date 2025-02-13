import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.frost_server import FrostServer
import folium
import json

# # Initialize the FrostServer class
# server = FrostServer()

# server = FrostServer(thing='Things(3)')
# observation_url = server.get_observations_url()
# content = server.get_content(observation_url)
# all_observations = server.get_all_observations()

# df_obs = pd.DataFrame(all_observations)
# df_obs["phenomenonTime"] = pd.to_datetime(df_obs["phenomenonTime"])
# df_obs["resultTime"] = pd.to_datetime(df_obs["resultTime"])

# # convert result to float
# df_obs["result"] = df_obs["result"].astype(float)

#print(df_obs.head(3))



def make_line_plot(data:pd.DataFrame):

    fig = px.line(
        data, 
        x='phenomenonTime', 
        y='result', 
        title='Observations Over Time',
        labels={'phenomenonTime': 'Time', 'result': 'Measurement Value'},
        line_shape='spline'  # Smooth line
    )

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Result',
        template='plotly_white',  # Optional: dark theme
        hovermode='x unified'    # Unified hover for better interactivity
    )
    return fig

def make_line_plot2(data:pd.DataFrame):

    # Plot with Plotly
    fig = px.line(
        data, 
        x='phenomenonTime', 
        y='result', 
        title='Observations Over Time',
        labels={'phenomenonTime': 'Time', 'result': 'Measurement Value'},
        line_shape='spline'
    )

    # Add interactive date range slider and buttons
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Result',
        template='plotly_white',
        hovermode='x unified',
        
        # Add range slider
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="Last 7 Days", step="day", stepmode="backward"),
                    dict(count=1, label="Last Month", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(step="all")  # Show all data
                ])
            ),
            rangeslider=dict(visible=True),  # Enable the range slider
            type="date"
        )
    )


def make_map(data):


    # Your JSON data
    # data = {
    #     "value": [
    #         {
    #             "@iot.selfLink": "https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)",
    #             "@iot.id": 1,
    #             "name": "Position lat 54.3323, lon 10.1519",
    #             "description": "Measuring point",
    #             "encodingType": "application/geo+json",
    #             "location": {
    #                 "type": "Point",
    #                 "coordinates": [10.1519, 54.3323]  # [longitude, latitude]
    #             },
    #             "HistoricalLocations@iot.navigationLink": "https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)/HistoricalLocations",
    #             "Things@iot.navigationLink": "https://timeseries.geomar.de/soop/FROST-Server/v1.1/Locations(1)/Things"
    #         }
    #     ]
    # }
    #print('Data:')
    #print(data)
    # Extract coordinates
    coordinates = data["value"][0]["location"]["coordinates"]
    longitude, latitude = coordinates[0], coordinates[1]
    #print(longitude, latitude)

    # Initialize a map centered around the coordinates
    m = folium.Map(
        #location=[54.3323, 10.1519],
        location=[latitude, longitude], 
        zoom_start=12)

    # Add a marker
    folium.Marker(
        [latitude, longitude],
        popup=f"Reventolou Brücke\nCurrent Temperature: ",
        tooltip="Click for info"
    ).add_to(m)

    return m

    # Display the map in a Jupyter Notebook (optional)
    #m  # Uncomment this if you're using Jupyter

    # Save the map as an HTML file
    #m.save("interactive_map.html")

    #print("Map saved as interactive_map.html")

#make_map()