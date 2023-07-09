import re
from geopy.distance import geodesic
from scraper_functions import *


def get_actual_rent_value(rent_value):

    if '€' in rent_value:
        cleaned_real_rent = float(re.sub(r'\D', '', rent_value))
    
        if cleaned_real_rent:
            if 'per month' in rent_value:
                return cleaned_real_rent
            elif 'per week' in rent_value:
                return (cleaned_real_rent * 52) / 12 # Transforms weekly into monthly rent
            else:
                return 0.0
    else:
        return 'Ignore'


def get_distance_from_city_centre(latitude, longitude):

    # Temple Bar coordinates
    city_centre_latitude = 53.3454357
    city_centre_longitude = -6.2672549
    city_centre_coord = (city_centre_latitude, city_centre_longitude)

    listing_coord = (latitude, longitude)
    
    distance = float(geodesic(city_centre_coord, listing_coord).kilometers)

    return distance


def get_coordinates_and_distance_from_city_centre(google_url):

    lat_start_index = google_url.index("loc:") + 4
    lat_end_index = google_url.index("+-")

    long_start_index = google_url.index("+-") + 1
    long_end_index = len(google_url)

    # Extract coordinates from google_url
    latitude = float(google_url[lat_start_index:lat_end_index])
    longitude = float(google_url[long_start_index:long_end_index])
    distance_from_city_centre = get_distance_from_city_centre(latitude, longitude)

    return latitude, longitude, distance_from_city_centre


def get_property_specifications(property_overview_info):
    property_bedroom = 0
    property_bathroom = 0
    property_available_from = ''
    property_furnished = ''
    property_lease = ''

    for listing in property_overview_info:
        property_info, property_info_data = listing.text.split(':', 1)
        
        if 'Bedroom' in property_info:
            property_bedroom += int(property_info_data)
        elif property_info == 'Bathroom':
            property_bathroom = property_info_data
        elif property_info == 'Available From':
            property_available_from = property_info_data
        elif property_info == 'Furnished':
            property_furnished = property_info_data
        elif property_info == 'Lease':                      
            property_lease = property_info_data

    return property_bedroom, property_bathroom, property_available_from, property_furnished, property_lease




            

