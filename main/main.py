from scraper_functions import get_properties_urls, get_properties_info
import pandas as pd
import os
import datetime

# CSV desktop path and file name
csv_path = r'C:\Users\Odafaz\Desktop\Daft Project\daft_listings'
csv_file = 'listing.csv'

properties_list = get_properties_urls()
properties_final_info_list = get_properties_info(properties_list)

# Filter out None or empty dictionaries
filtered_property_info_final = [d for d in properties_final_info_list if d is not None and bool(d)]
df = pd.DataFrame(filtered_property_info_final)

# Remove duplicates based on 'property_id'
df.drop_duplicates(subset='property_id', inplace=True)
df.reset_index(drop=True, inplace=True)


# Check if CSV file exists
csv_filepath = os.path.join(csv_path, csv_file)
if os.path.exists(csv_filepath):
    # Read existing property_ids from CSV
    existing_ids = pd.read_csv(csv_filepath)['property_id']

    # Filter DataFrame to keep only unique property_ids
    df = df[~df['property_id'].isin(existing_ids)]
    
#df.to_csv(csv_filepath, encoding='utf-8')

# Append filtered DataFrame to CSV file
df.to_csv(csv_filepath, mode='a', index=False, header=False, encoding='utf-8')


# Save run log in a txt file
file = open(r'C:\Users\Odafaz\Desktop\Daft Project\task.txt','a')
file.write(f'{datetime.datetime.now()}\n')

