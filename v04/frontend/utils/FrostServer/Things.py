
import json

import pandas as pd
import requests
import datetime
from pprint import pprint



class Things:
    def __init__(self):
        self.url = "https://timeseries.geomar.de/soop/FROST-Server/v1.1/Things"
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
    things = Things()
    things_list = things.content
    print(f'Number of things: {len(things_list["value"])}')
    pprint(things_list['value'][6])
