import copernicusmarine
import xarray as xr


class Copernicus:
    def __init__(self):
        self.copernicusmarine = copernicusmarine.CopernicusMarine()

    def get_copernicusmarine(self):
        return self.copernicusmarine
    
    def get_dataset(self, dataset_id):
        return self.copernicusmarine.get_dataset(dataset_id)
    
    def get_subset(self, dataset_id, dataset_version, variables, minimum_longitude, maximum_longitude, minimum_latitude, maximum_latitude, start_datetime, end_datetime, coordinates_selection_method, disable_progress_bar, username, password):
        return self.copernicusmarine.get_subset(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            variables=variables,
            minimum_longitude=minimum_longitude,  # Angepasste Koordinate
            maximum_longitude=maximum_longitude,
            minimum_latitude=minimum_latitude,  # Angepasste Koordinate
            maximum_latitude=maximum_latitude,    # Angepasste Koordinate
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            coordinates_selection_method=coordinates_selection_method,
            disable_progress_bar=disable_progress_bar,
            username=username,
            password=password
        )
    
    def delete