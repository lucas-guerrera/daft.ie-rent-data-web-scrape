from functions import get_actual_rent_value, get_coordinates_and_distance_from_city_centre, get_property_specifications
from bs4 import BeautifulSoup
import requests
import re
import concurrent.futures
from concurrent import futures
from datetime import datetime
import hashlib



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

    property_daft_id_element = soup.find('p', class_='DaftIDText__StyledDaftIDParagraph-vbn7aa-0 glbfmV')
    if property_daft_id_element is not None:
        property_daft_id = property_daft_id_element.text.split(":")[1].strip()
    else:
        return


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

    # Get property views and entered/renewed date
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

    # Create an unique columm based on type, num_bedroom, num_bathroom, address and rent value
    property_id = property_daft_id + str(property_rent_value)
    # Hash property_id
    hashed_property_id = hashlib.sha256(property_id.encode()).hexdigest()

    return {'daft_id': property_daft_id,
            'date_entered': property_date,
            'views': property_views,
            'type': property_type,
            'rent': property_rent_value,    
            'num_bedroom': property_bedroom,
            'num_bathroom': property_bathroom,
            'available_from': property_available_from,
            'furnished': property_furnished,
            'lease' : property_lease,
            'ber_rating': property_ber_rating,
            'address': property_address,
            'distance_from_city_centre': property_distance_from_city_centre,
            'latitude': property_latitude,
            'longitude': property_longitude,
            'region': property_address.split(",")[-1],
            'url': 'https://www.daft.ie' + url,
            'input_date': datetime.now().strftime('%d/%m/%Y'),
            'property_id': hashed_property_id}


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
    
    # Determine total number of pages
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