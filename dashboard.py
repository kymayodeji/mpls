# MinneapolisDashboard
# dashboard for statistics and analysis of the city of Minneaplis
# Details

#| Title           | Description                                                    |
#|-----------------|----------------------------------------------------------------|
#| Author          | Kymberly Ayodeji                                               |
#| Start Date      | 2024-05-21                                                       |
#| End Date        | 2024-                                                          |
#| Datasets		    |                                                                |
#| Products        |                                                                |
#| Summary         |                                                                |
#
# 0: Install Libraries and Packages
# for Numerical
import pandas as pd
import numpy as np
# for Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
# Dashboard Libraries
import dash
from dash import html
from dash import dcc

# 1: Load Data
business_licenses_url = "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/Active_Rental_Licenses/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

#Data is from: 

# 2: Data Cleaning


# Application Constructor
app = dash.Dash(__name__)

app.layout = html.P("Title: Minneapolis Dashboard")

if __name__ == "__main__":
    app.run_server(debug=True)
    
