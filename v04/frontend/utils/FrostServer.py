import requests
from urllib.parse import urljoin
from pprint import pprint

class FrostServerClient:
    def __init__(self, base_url: str):
        """
        base_url: z.B. 'https://timeseries.geomar.de/soop/FROST-Server/v1.1/'
        """
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url

    def get_entities(self, entity_type: str, params: dict = None) -> list:
        """
        entity_type: 'Things', 'Datastreams', 'Observations', 'Locations', etc.
        params: Optional: Dictionary mit OData-Parametern wie $filter, $expand, $top, etc.
        Rückgabe: Liste mit Objekten (dicts)
        """
        url = urljoin(self.base_url, entity_type)
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('value', [])

    def get_all_paginated(self, entity_type: str, params: dict = None) -> list:
        """
        Holt alle Daten einer Entität, auch wenn sie über mehrere Seiten verteilt sind.
        """
        url = urljoin(self.base_url, entity_type)
        results = []
        while url:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results.extend(data.get('value', []))
            url = data.get('@iot.nextLink', None)
            params = None  # nur beim ersten Request nötig
        return results

    def get_observations_for_datastream(self, datastream_id: int, top: int = 100) -> list:
        """
        Holt die letzten 'top' Beobachtungen eines bestimmten Datastreams.
        """
        entity = f"Datastreams({datastream_id})/Observations"
        params = {"$top": top, "$orderby": "phenomenonTime desc"}
        return self.get_entities(entity, params=params)

    def get_thing_with_datastreams(self, thing_id: int) -> dict:
        """
        Gibt ein Thing mit seinen Datastreams zurück (per $expand).
        """
        entity = f"Things({thing_id})"
        params = {"$expand": "Datastreams"}
        result = self.get_entities(entity, params=params)
        return result[0] if result else {}

    def list_things(self) -> list:
        """
        Gibt eine Liste aller Things zurück.
        """
        return self.get_all_paginated("Things")

    def list_datastreams(self) -> list:
        """
        Gibt eine Liste aller Datastreams zurück.
        """
        return self.get_all_paginated("Datastreams")




# Beispiel-Nutzung:
if __name__ == "__main__":
    frost = FrostServerClient("https://timeseries.geomar.de/soop/FROST-Server/v1.1/")
    
    things = frost.list_things()
    print(f"Anzahl Things: {len(things)}")

    thing = things[3] # Select Specific Thing

    print("\nThing Keys:", thing.keys())
    print("\nThing Name:", thing['name'])
    print("\nThing Description:", thing['description'])
    print("\nThing ID:", thing['@iot.id'])

    print("\nThing Properties:", thing['properties'])
    print("\nThing Datastream Link:", thing['Datastreams@iot.navigationLink'])

    datastream = frost.get_entities(entity_type=f'Things({thing["@iot.id"]})/Datastreams')
    #print("\nDatastreams:", datastream)

    #pprint(len(datastream))

    # get Locations of the Thing
    locations = frost.get_entities(entity_type=f'Things({thing["@iot.id"]})/Locations')
    print("\nLocations:", locations)


    # datastreams = frost.get_entities("Things({})/Datastreams".format(thing['@iot.id']))
    # # print(f"Datastreams für '{thing['name']}': {[ds['name'] for ds in datastreams]}")

    # pprint("Datastreams für '{}':".format(thing['name']))
    # for ds in datastreams:
    #     print(f"  - {ds['name']} (ID: {ds['@iot.id']})")
    
    # # Beispiel: Beobachtungen für den ersten Datastream
    # if datastreams:
    #     first_datastream = datastreams[0]
    #     observations = frost.get_observations_for_datastream(first_datastream['@iot.id'])
    #     print(f"Anzahl Beobachtungen für '{first_datastream['name']}': {len(observations)}")
    #     if observations:
    #         print("Letzte Beobachtung:", observations[0])
    # else:
    #     print("Keine Datastreams gefunden.")





