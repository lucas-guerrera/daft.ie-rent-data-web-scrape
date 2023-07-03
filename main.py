import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import concurrent.futures
from geopy.distance import geodesic
from datetime import datetime

# CSV desktop path and file name
csv_path = r'C:\Users\Odafaz\Desktop\Daft Project'
csv_file = 'listing.csv'

properties_list = get_properties_urls()
properties_final_info_list = get_properties_info(properties_list)

# Filter out None or empty dictionaries
filtered_property_info_final = [d for d in properties_final_info_list if d is not None and bool(d)]


# Create a DataFrame from the filtered list of dictionaries
df = pd.DataFrame(filtered_property_info_final)
df.dropna(subset=['Rent'], inplace=True) 
df['Region'] = df['Region'].str.extract(r'(Dublin \d+)', expand=False)
df.drop(df[df['Rent'] == 'Ignore'].index, inplace=True)

df['Date Entered/Renewed'] = pd.to_datetime(df['Date Entered/Renewed'], format ='%d/%m/%Y')
df['Views'] = df['Views'].str.replace(',', '').astype(int)
df['Rent'] = pd.to_numeric(df['Rent'].astype(str).str.replace(',', ''), errors='coerce')
df['Bedroom']= df['Bedroom'].astype(int)
df['Bathroom']= df['Bathroom'].astype(int)


# Define the distance groups
bins = [0, 1, 3, 5, 7, 10, 15, 20, 30, 40, 50, float('inf')]
# Create labels for the bins
labels = ['< 1 km', '1 - 3 km', '3 - 5 km', '5 - 7 km', '7 - 10 km', '10 - 15 km', '15 - 20 km', '20 - 30 km', '30 - 40 km', '40 - 50 km', '> 50 km']
df['Distance Category'] = pd.cut(df['Distance From City Centre'], bins=bins, labels=labels)

# Save DataFrame to CSV
df.to_csv(csv_path + '\\' + csv_file, encoding='utf-8')
