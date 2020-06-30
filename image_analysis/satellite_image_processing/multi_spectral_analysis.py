from pathlib import Path
import json
from sentinelsat import SentinelAPI
import geopandas as gpd
import folium
from shapely.geometry import MultiPolygon, Polygon
import matplotlib.pyplot as plt
import os
from os import listdir
from os.path import isfile, join
import rasterio as rio
from rasterio.mask import mask
from pyproj import Transformer
from retrieve_sentinel_data import get_count_vertices

with open('year_name_json.json', 'r') as inputFile:
    year_name_json = json.load(inputFile)
    years = list(year_name_json.keys())

'''
The below function will return a dict with the following schema
{
    2020 : {
        "bands" : {
            "b01" : "as",
            "b02" : "as"
        },
        "parent_dir" : "parent_direc"
    },
    2019 : {
        "bands" : {
            "b01" : "as",
            "b02" : "as"
        },
        "parent_dir" : "parent_direc"
    }

}

'''


def get_band_paths():
    tempList = [f.path for f in os.scandir('multi_spectral_images') if f.is_dir()]
    parent_path_list = []

    for filePath in tempList:
        # childFormat = filePath+ '\GRANULE\\'
        child_format = '{}\GRANULE\\'.format(filePath)
        child = [f.path for f in os.scandir(child_format) if f.is_dir()][0]
        parent_path_list.append('{}\IMG_DATA\\'.format(child))

    year_dict = {}
    year = 0
    for parent in parent_path_list:
        child_list = [f for f in listdir(parent) if isfile(join(parent, f))]
        # child_list = [f.path for f in os.scandir(parent) if f.is_dir()]
        child = child_list[0]
        child = child.split('_')

        year = int(child[1][:4])
        # year = '01'+parent
        band_dict = dict()
        for x in range(1, 13):
            band_id = 'B' + str(x).zfill(2)
            band_dict[band_id] = [s for s in child_list if band_id in s][0]

        band_dict['TCI'] = [s for s in child_list if 'TCI' in s][0]
        sub_dict = dict()
        sub_dict['parent_dir'] = parent
        sub_dict['bands'] = band_dict

        year_dict[year] = sub_dict

    return year_dict




def rgb(year_info, year):
    parent_dir = year_info['parent_dir']
    b4 = rio.open(parent_dir + year_info['bands']['B04'])
    b3 = rio.open(parent_dir + year_info['bands']['B03'])
    b2 = rio.open(parent_dir + year_info['bands']['B02'])

    # Create an RGB image
    with rio.open("processed\{}_RGB.tiff".format(year), 'w', driver='GTiff', width=b4.width, height=b4.height, count=3,
                  crs=b4.crs, transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
        rgb.write(b2.read(1), 3)
        rgb.write(b3.read(1), 2)
        rgb.write(b4.read(1), 1)
        rgb.close()


def clip(county, year_info, year, read_name, out_name):
    parent_dir = year_info['parent_dir']
    b4 = rio.open(parent_dir + year_info['bands']['B04'])
    county_proj = county.to_crs(b4.crs)
    print(b4.crs, get_count_vertices(county_proj))

    with rio.open(read_name) as src:
        out_image, out_transform = mask(src, county_proj.geometry, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})

    with rio.open(out_name, "w", **out_meta) as dest:
        dest.write(out_image)


def create_rgb_county(band_path):
    for year in band_path.keys():
        county = gpd.read_file('franklin_boundary/frankling_boundary.shp')
        year_info = band_path[year]
        print('Starting rgb')
        rgb(year_info, year)
        print('Starting to clip')
        read_name = "processed\{}_RGB.tiff".format(year)
        out_name = "processed\{}_RGB_masked.tiff".format(year)
        clip(county, year_info, year, read_name, out_name)


def create_ndiv(year_info, year):
    parent_dir = year_info['parent_dir']
    b4 = rio.open(parent_dir + year_info['bands']['B04'])
    b8 = rio.open(parent_dir + year_info['bands']['B08'])

    red = b4.read()
    nir = b8.read()

    #Calculate ndvi

    ndvi = (nir.astype(float) - red.astype(float))/(nir.astype(float)+red.astype(float))
    meta = b4.meta
    meta.update(driver = 'GTiff')
    meta.update(dtype = rio.float32)
    with rio.open('processed\{}_NDVI.tif'.format(year), 'w', **meta) as dest:
        dest.write(ndvi.astype(rio.float32))


def create_ndvi_county(band_path):
    for year in band_path.keys():
        county = gpd.read_file('franklin_boundary/frankling_boundary.shp')
        year_info = band_path[year]
        print('Starting NDVI Calculation')
        create_ndiv(year_info, year)
        print('Starting to clip')
        read_name = "processed\{}_NDVI.tif".format(year)
        out_name = "processed\{}_NDVI_masked.tif".format(year)
        clip(county, year_info, year, read_name, out_name)

band_path = get_band_paths()
create_ndvi_county(band_path)