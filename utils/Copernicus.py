import copernicusmarine
import xarray as xr
import os

class AdvancedCopernicus:
    def __init__(self):
        self.client = copernicusmarine  # Using composition to access copernicusmarine functions

    def get_dataset(self, dataset_id):
        return self.client.get_dataset(dataset_id)
    
    def get_subset(self, 
                   dataset_id: str, 
                   dataset_version: str, 
                   variables: list, 
                   minimum_longitude: float, 
                   maximum_longitude: float, 
                   minimum_latitude: float, 
                   maximum_latitude: float, 
                   start_datetime: str, 
                   end_datetime: str,
                   minimum_depth: float = 0.5016462206840515,
                   maximum_depth: float = 0.5016462206840515, 
                   coordinates_selection_method: str = "strict-inside", 
                   disable_progress_bar: bool = False, 
                   username: str = 'mbanzhaf', 
                   password: str = '6bF$ebvr',
                   output_filename: str = 'output.nc'
                   ):
        # Fetch subset data and save to output_filename
        self.client.subset(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            variables=variables,
            minimum_longitude=minimum_longitude,
            maximum_longitude=maximum_longitude,
            minimum_latitude=minimum_latitude,
            maximum_latitude=maximum_latitude,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            minimum_depth=minimum_depth,
            maximum_depth=maximum_depth,
            coordinates_selection_method=coordinates_selection_method,
            disable_progress_bar=disable_progress_bar,
            username=username,
            password=password,
            output_filename=output_filename
        )
        # Load the downloaded NetCDF file into an xarray Dataset
        return xr.open_dataset(output_filename)
    
    def delete_dataset(self, file_name):
        os.remove(file_name)
        
