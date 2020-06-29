from pathlib import Path
import json
from sentinelsat import SentinelAPI
import geopandas as gpd
import folium
from shapely.geometry import MultiPolygon, Polygon
import matplotlib.pyplot as plt

login_json_path = str(Path(__file__).parents[2]) + r'\login_info.json'

with open(login_json_path) as a:
    login_info = json.load(a)

def get_count_vertices(df):
    for i, row in df.iterrows():
        # It's better to check if multigeometry
        multi = row.geometry.type.startswith("Multi")

        if multi:
            n = 0
            # iterate over all parts of multigeometry
            for part in row.geometry:
                n += len(part.exterior.coords)
        else:  # if single geometry like point, linestring or polygon
            n = len(row.geometry.exterior.coords)

        return n


api = SentinelAPI(login_info['copernicus_username'], login_info['copernicus_password'], 'https://scihub.copernicus.eu/dhus')
# api = SentinelAPI(user='s5pguest', password='s5pguest', api_url='https://s5phub.copernicus.eu/dhus')
county = gpd.read_file('franklin_boundary/frankling_boundary.shp')
county_simplified = county.copy()
county_simplified.geometry = county.geometry.simplify(tolerance=0.002, preserve_topology=True)
footprint = None
for i in county_simplified['geometry']:
    footprint = i

print(get_count_vertices(county_simplified))

years = [2017,2018, 2020]
# Years 2017 and 2018 are in LTA. The user has to wait hours before they can download the images
#I would not suggest using this method to retrive past data, rather maintain a temp db with all the needed
#images


#The below loop downloads the 1st images (ordered by cloudcoveragepercentage asc) for each year

#TODO   Implement renaming the downloading zip files

for year in years:
    products = api.query(footprint,
                         date = ('{}0501'.format(str(year)), '{}0601'.format(str(year))),
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 30))


    products_gdf = api.to_geodataframe(products)

    products_gdf = products_gdf.sort_values(['cloudcoverpercentage'], ascending=[True])
    product_id = products_gdf.uuid.iloc[0]
    print('Starting to download {} for year {} with cloud cover percentage {}%'.format(str(product_id), str(year), products_gdf.cloudcoverpercentage.iloc[0]))
    api.download(product_id)
    print('Finished Downloading')




