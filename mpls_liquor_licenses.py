# Minneapolis Liquor Licenses (mpls_liquor_licenses.py)
# - extract, transform and load data from the Minneapolis Liquor Licenses dataset
# 

#| Title           | Description                                                    |
#|-----------------|----------------------------------------------------------------|
#| Author          | Kymberly Ayodeji                                               |
#| Start Date      | 2024-05-25                                                       |
#| End Date        | 2024-05-25                                                          |
#| Datasets		   | https://opendata.minneapolismn.gov/datasets/cityoflakes::on-sale-liquor                                                               |
#
# 0: Install Libraries and Packages
# Import Packages and Libraries needed for the project
import pandas as pd
import numpy as np

# for data processing
import requests
import json

# for datetime
from datetime import datetime

# for Geospatial data
import geopandas as gpd
import contextily 

# for Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# Defined Functions
def a_load_data(url):
    # Load GeoPandas data from OpenData.Minneapolis.Gov open On-Sale Liquor Licenses in the City of Minneapolis
    response = requests.get(url)
    data = json.loads(response.text)
    # since the data contains nested dictionaries we need to flatten the data from the outer features key
    data2 = pd.json_normalize(data['features'])
    # Rename the nested dictionary keys of geometry and  properties columns by removing geometry and properties.
    data2.columns = data2.columns.str.replace('geometry.', '')
    data2.columns = data2.columns.str.replace('properties.', '')
    return data2

def b_clean_data(df):
    num_rows = df.shape[0]
    # Convert coordinates column to two separate columns for the x and y coordinates
    # Separate the pairs into two lists
    df['X'] = [pair[0] for pair in df['coordinates']]
    df['Y'] = [pair[1] for pair in df['coordinates']]
    df['X'] = df['X'].astype('float64')
    df['Y'] = df['Y'].astype('float64')
    
    # Drop columns that are not needed
    cols_not_needed = ['coordinates','type', 'id', 'type', 'OBJECTID','liquorType', 'lat', 'long', 'xWebMercator', 'yWebMercator']
    df.drop(columns=cols_not_needed, inplace=True, axis=1)
   
    # Convert object columns to other data types. Step 1: Fill missing values with 0
    object_columns = ['ward', 'issueDate', 'expirationDate', 'lastUpdateDate']
    df[object_columns] = df[object_columns].fillna(0)
    
    # Convert to integer
    df['ward'] = df['ward'].astype('int64')
    
    # Convert object columns to datetime   
    df['issueDate'] = pd.to_datetime(df['issueDate'], unit='ms')
    df['expirationDate'] = pd.to_datetime(df['expirationDate'], unit='ms') 
    df['lastUpdateDate'] = pd.to_datetime(df['lastUpdateDate'], unit='ms')
   
    # Drop rows with missing values
    df.dropna(inplace=True)
    
    # Convert expirationYear to integer
    df['expirationYear'] = df['expirationYear'].astype('int64')
    #print(f'Dropped {num_rows - df.shape[0]} rows')
    
    return df

def c_address_messy_data(df):
    num_rows = df.shape[0]
    # Remove data where issue date is less than 2020
    df = df[df['issueDate'].dt.year >= 2010]
    
    # Remove data where expiration date is less than 2020
    df = df[df['expirationDate'].dt.year >= 2020]
    
    # Remove data when the Ward is not 1 to 13
    df= df[df['ward'].between(1, 13)]
    #print(f'Rows removed: {num_rows - df.shape[0]}')
    return df

def d_feature_engineering(df):
    # Extract month, year from the issue date and calculate the duration of the license
    df['issueMonth'] = df['issueDate'].dt.month
    df['issueYear'] = df['issueDate'].dt.year   
    df['duration'] = df['expirationDate'] - df['issueDate']
    
    # Split up the endorsements column into separate columns
    endorsements = df['endorsements'].str.split('[,;]').explode().unique()
    endorsements = [e.strip() for e in endorsements]
    for e in endorsements:
        df[e] = df['endorsements'].str.contains(e, regex=False)

    return df

def e_load_prep_shapefile(mpls_zip):
    df = gpd.read_file(mpls_zip)
    # Rename column and convert to integer
    df.rename(columns={'BDNUM':'ward'}, inplace=True)
    df['ward']=df['ward'].astype('int64')
    
    return df

def f_plot_wards(df):
    # Plot the wards
    plt.rcParams.update({'font.size': 15})
    fig, ax = plt.subplots(figsize=(18, 9))
    df.plot(column ='ward', alpha=0.9, legend=False,      #plotting geometry data
        edgecolor = 'white', cmap='viridis', ax=ax)
    df.apply(lambda x: ax.annotate(text = x['ward'],      #annotations
                               xy = x.geometry.centroid.coords[0],
                               color = 'white',
                               ha = 'center'), axis = 1)
    ax = contextily.add_basemap(ax, crs=df.crs.to_string())
    plt.title('Minneapolis Wards')
    plt.show()
    
def g_plot_liquor_licenses(df, mpls_df, endorsement = 'On Sale'):
    # Plot the wards
    if endorsement not in df.columns:
        endorsement = 'On Sale'
    cmap = 'cividis'
    plt.rcParams.update({'font.size': 15})
    fig, ax = plt.subplots(figsize=(25, 15))
    mpls_df.plot(column ='ward', alpha=0.9, legend=False,      #plotting geometry data
        edgecolor = 'white', cmap=cmap, ax=ax)
    mpls_df.apply(lambda x: ax.annotate(text = x['ward'],      #annotations
                               xy = x.geometry.centroid.coords[0],
                               color = 'white',
                               ha = 'center'), axis = 1)
    ax = contextily.add_basemap(ax, crs=mpls_df.crs.to_string())
    df_endorsement = df[df[endorsement] == True ]
    cnt = df[endorsement].sum()
    plt.title(f'{endorsement} Locations ({cnt}) in Minneapolis')
    plt.scatter(df_endorsement['X'], df_endorsement['Y'], c=df_endorsement[endorsement], s=10, alpha=0.5)
    plt.show()

if __name__ == "__main__":
    licenses_url = "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/On_Sale_Liquor/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
    raw_data = a_load_data(licenses_url)
    df = b_clean_data(raw_data)
    df = c_address_messy_data(df)
    df = d_feature_engineering(df)
    
    mpls_zip = "data/City_Council_Wards-shp.zip"    
    mpls_df = e_load_prep_shapefile(mpls_zip)
    liquorType = 'Wine'
    g_plot_liquor_licenses(df, mpls_df, liquorType)