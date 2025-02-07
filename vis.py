import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from frost_server import FrostServer

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

