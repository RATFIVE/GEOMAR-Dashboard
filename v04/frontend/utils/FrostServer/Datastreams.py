
import json

import pandas as pd
import requests
import datetime
from pprint import pprint



class Datastreams:
    def __init__(self):
        self.url = "https://timeseries.geomar.de/soop/FROST-Server/v1.1/Datastreams"
        self.content = self.get_content(self.url)

    
    def get_content(self, url:str):
        """Fetches content from the specified URL.

        Args:
            url (str): The URL to fetch content from.

        Returns:
            dict: The parsed JSON content from the response.
        """
        response = requests.get(url)
        content = response.text
        
        return json.loads(content)
    



if __name__ == "__main__":
    datastream = Datastreams()
    things_list = datastream.content
    print(f'Number of datastreams: {len(things_list["value"])}')
    pprint(things_list['value'][6])
