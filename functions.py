from bs4 import BeautifulSoup
import requests
import re
import concurrent.futures
from concurrent import futures
from geopy.distance import geodesic
from datetime import datetime


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
        info, info_data = listing.text.split(':', 1)
        
        if 'Bedroom' in info:
            property_bedroom += int(info_data)
        elif info == 'Bathroom':
            property_bathroom = info_data
        elif info == 'Available From':
            property_available_from = info_data
        elif info == 'Furnished':
            property_furnished = info_data
        elif info == 'Lease':
            property_lease = info_data

    return property_bedroom, property_bathroom, property_available_from, property_furnished, property_lease


def get_actual_rent_value(rent_value):

    if '€' in rent_value:
        cleaned_real_rent = float(re.sub(r'\D', '', rent_value))
    
        if cleaned_real_rent:
            if 'per month' in rent_value:
                return cleaned_real_rent
            elif 'per week' in rent_value:
                return (cleaned_real_rent * 52) / 12
            else:
                return 0.0
    else:
        return 'Ignore'
            
def scrape_property(url):
    listing_html = requests.get('https://www.daft.ie' + url)
    soup = BeautifulSoup(listing_html.content, 'lxml')

    # Ensuring all element variables are None to avoid potential UnboundLocalErrors
    property_type_element = None
    rent_value_element = None
    property_statistics_element = None
    property_ber_element = None
    property_address_element = None
    property_google_url_element = None
    property_specifications_element = None
    bedroom_card_element = None 
    bathroom_card_element = None

    # Get property type (Apartment, House, Studio,...)
    property_type_element = soup.find('p', class_='TitleBlock__CardInfoItem-sc-1avkvav-9 cKZYAr')
    if property_type_element is not None:
        property_type = property_type_element.text
    else:
        return

    # Get rent value, call get_actual_rent_value function to clean it and make it monthly rent value.
    rent_value_element = soup.find('h2', class_='TitleBlock__StyledCustomHeading-sc-1avkvav-5 blbeVq')
    if rent_value_element is not None:
        property_rent_value = get_actual_rent_value(rent_value_element.text)
    else:
        property_rent_value = '0.0'

    # Get property view and entered/renewed date
    property_statistics_element = soup.find_all('p', class_ = 'Statistics__StyledLabel-sc-15tgae4-1 iDjRee')
    if property_statistics_element is not None:
        property_date = property_statistics_element[0].text
        property_views = property_statistics_element[1].text
    else:
        property_date = 'NA'
        property_views = 'NA'

    # Get BER Rating
    property_ber_element = soup.find('img', class_='BerDetails__BerImage-sc-14a3wii-0 oeukv')
    if property_ber_element and 'SI_666' in property_ber_element['alt']:
        property_ber_rating = 'BER Exempt'
    elif property_ber_element:
        property_ber_rating = property_ber_element['alt']
    else:
        property_ber_rating = 'NA'

    # Get Address
    property_address_element = soup.find('h1', class_ = 'TitleBlock__Address-sc-1avkvav-8 dzihxK')
    if property_address_element is not None:
        property_address = property_address_element.text
    else:
        property_address = 'NA'

    # Get google maps URL and call a function to extract coordinates (latitude and longitude)
    property_google_url_element = soup.find('div', class_='NewButton__ButtonContainer-yem86a-4 deYANw button-container')
    if property_google_url_element is not None:
        property_google_url = property_google_url_element.a['href']
        property_latitude, property_longitude, property_distance_from_city_centre = get_coordinates_and_distance_from_city_centre(property_google_url)
    else:
        property_latitude, property_longitude, property_distance_from_city_centre = '', '', ''

    # Get property specifications such as number of bedrooms, bathrooms, furnished, lease from Property Overview 
    property_specifications_element = soup.find('div', {"data-testid" : "overview"})
    if property_specifications_element is not None:
        property_specifications = property_specifications_element.find_all('li')
        property_bedroom, property_bathroom, property_available_from, property_furnished, property_lease = get_property_specifications(property_specifications)

        # If a property is not a Studio and is missing the number of bedrooms or bathrooms in the Property Overview section
        if (property_bedroom == 0 or property_bathroom == 0) and property_type != 'Studio':
            bedroom_card_element = soup.find('p', {"data-testid" : "beds"})
            bathroom_card_element = soup.find('p', {"data-testid" : "baths"})
            if bedroom_card_element is not None:  
                property_bedroom = int(re.match(r'\d+', bedroom_card_element.text).group())
            elif bathroom_card_element is not None:
                property_bathroom = int(re.match(r'\d+', bathroom_card_element.text).group())
            else:
                property_bedroom = 0
                property_bathroom = 0
    else:
        property_bedroom = 0
        property_bathroom = 0
        property_available_from = 'NA'
        property_furnished = 'NA'
        property_lease = 'NA'


    return {'Date Entered/Renewed': property_date,
            'Views': property_views,
            'Type': property_type,
            'Rent': property_rent_value,
            'Bedroom': property_bedroom,
            'Bathroom': property_bathroom,
            'Available From': property_available_from,
            'Furnished': property_furnished,
            'Lease' : property_lease,
            'BER Rating': property_ber_rating,
            'Address': property_address,
            'Distance From City Centre': property_distance_from_city_centre,
            'Latitude': property_latitude,
            'Longitude': property_longitude,
            'Region': property_address.split(",")[-1],
            'Url': 'https://www.daft.ie' + url,
            'Input Date': datetime.now().strftime('%d/%m/%Y')}


def get_listing_urls(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'lxml')
    search_results = soup.find('div', class_='SearchPage__MainColumn-gg133s-0 gXNFtp')

    if search_results is None:
        return []

    listing_links = search_results.find_all('a')

    urls = []
    for link in listing_links:
        href = link['href']
        if '/for-rent/' in href:
            urls.append(href)

    return urls


def get_properties_urls(num_properties=20):
    base_url = "https://www.daft.ie/property-for-rent/dublin?pageSize=20&from="
    html = requests.get(base_url + "0")
    soup = BeautifulSoup(html.content, 'lxml')

    search_results = soup.find('div', class_='SearchPage__MainColumn-gg133s-0 gXNFtp')
    num_properties = int(search_results.find('div', class_='styles__SearchResultsHeader-sc-1t5gb6v-2 iiBovf').h1.text.split()[0])
    listing_urls = []
    
    # Determine the number of pages required
    page_size = 20
    num_pages = (num_properties + page_size - 1) // page_size
    

    with futures.ThreadPoolExecutor() as executor:
        # Create a list of URLs to fetch
        urls = [base_url + str(page * page_size) for page in range(num_pages)]

        # Submit the requests and collect the futures
        future_to_url = {executor.submit(get_listing_urls, url): url for url in urls}

        # Process the completed futures
        for future in futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                listing_urls.extend(future.result())
            except Exception as e:
                print(f"Error occurred while fetching URL: {url}\n{e}")

    return listing_urls



def get_properties_info(listing_urls):
    results = []
    
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = [executor.submit(scrape_property, url) for url in listing_urls]
        
        # Retrieve results from the futures as they become available
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
    
    return results