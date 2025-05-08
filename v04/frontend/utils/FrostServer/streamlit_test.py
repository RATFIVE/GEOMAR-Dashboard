import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests
from urllib.parse import urljoin


# Konstante
OBSERVATION_LIMIT = 1000  # Kannst du anpassen


# Deine vorhandene Klasse
class FrostServerClient:
    def __init__(self, base_url: str):
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url

    def get_entities(self, entity_type: str, params: dict = None) -> list:
        url = urljoin(self.base_url, entity_type)
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('value', [])

    def get_all_paginated(self, entity_type: str, params: dict = None) -> list:
        url = urljoin(self.base_url, entity_type)
        results = []
        while url:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results.extend(data.get('value', []))
            url = data.get('@iot.nextLink', None)
            params = None
        return results

    def get_observations_for_datastream(self, datastream_id: int, top: int = 100) -> list:
        entity = f"Datastreams({datastream_id})/Observations"
        params = {"$top": top, "$orderby": "phenomenonTime desc"}
        return self.get_entities(entity, params=params)

    def list_things_with_locations(self) -> list:
        return self.get_all_paginated("Things?$expand=Locations")

    def get_datastreams_for_thing(self, thing_id: int) -> list:
        return self.get_entities(f"Things({thing_id})/Datastreams")


# Streamlit-App
def main():
    st.set_page_config(layout="wide")
    st.title("🌐 FROST-Server Dashboard")

    # Client initialisieren
    client = FrostServerClient("https://timeseries.geomar.de/soop/FROST-Server/v1.1/")

    # 1) Things laden
    with st.spinner("Lade Things vom FROST-Server..."):
        things = client.list_things_with_locations()

    # Karte vorbereiten
    m = folium.Map(location=[0, 0], zoom_start=2, width=2000)
    thing_coords = []  # (lat, lon, id)

    for thing in things:
        locs = thing.get("Locations", [])
        if not locs:
            continue
        coords = locs[0].get("location", {}).get("coordinates", [None, None])
        lat, lon = coords[1], coords[0]
        if lat is None or lon is None:
            continue

        # Tooltip mit letzten Werten der Datastreams
        last_vals = []
        dss = client.get_datastreams_for_thing(thing['@iot.id'])
        for ds in dss:
            obs = client.get_observations_for_datastream(ds['@iot.id'], top=1)
            if obs:
                val = obs[0].get('result')
                last_vals.append(f"{ds['name']}: {val}")
        tooltip = "\n".join(last_vals) or "Keine Daten"

        folium.CircleMarker(
            location=(lat, lon),
            radius=6,
            tooltip=tooltip,
            popup=f"Thing ID: {thing['@iot.id']}",
        ).add_to(m)

        thing_coords.append((lat, lon, thing['@iot.id']))

    # Karte rendern
    st.subheader("Standorte der Things")
    map_data = st_folium(m, width=500)

    # Geklickter Punkt → nächstes Thing auswählen
    clicked = map_data.get("last_clicked") if map_data else None
    selected_id = st.session_state.get("selected_id")

    if clicked:
        st.write("Klickposition:", clicked)
        lat0, lon0 = clicked['lat'], clicked['lng']

        if thing_coords:
            selected = min(
                thing_coords,
                key=lambda t: (t[0] - lat0)**2 + (t[1] - lon0)**2
            )
            selected_id = selected[2]
            st.session_state["selected_id"] = selected_id

    # Daten anzeigen
    if selected_id:
        st.markdown(f"## 📊 Observations für Thing ID: **{selected_id}**")

        dss = client.get_datastreams_for_thing(selected_id)
        df_list = []

        for ds in dss:
            obs = client.get_observations_for_datastream(ds['@iot.id'], top=OBSERVATION_LIMIT)
            if not obs:
                continue
            tmp = pd.DataFrame({
                'time': [o['phenomenonTime'] for o in obs][::-1],
                ds['name']: [o['result'] for o in obs][::-1]
            })
            df_list.append(tmp.set_index('time'))

        if df_list:
            df_all = pd.concat(df_list, axis=1)
            df_all.index = pd.to_datetime(df_all.index)
            fig = px.line(
                df_all,
                x=df_all.index,
                y=df_all.columns,
                labels={'value': 'Messwert', 'time': 'Zeit'},
                title="Zeitreihen aller Datastreams",
                height=400,
                width=1500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Observations für diesen Thing gefunden.")
    else:
        st.info("Klicke auf einen Marker in der Karte oben, um ein Thing auszuwählen.")


if __name__ == '__main__':
    main()
