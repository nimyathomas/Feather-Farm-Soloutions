import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth.
    Input: Latitude and Longitude of both points in decimal degrees.
    Output: Distance in kilometers.
    """
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
# utils.py


def get_region_from_coordinates(latitude, longitude):
    """
    Determine region (North/South, East/West) based on the latitude and longitude.
    """
    if latitude >= 0:
        if longitude >= 0:
            return "North-East"
        else:
            return "North-West"
    else:
        if longitude >= 0:
            return "South-East"
        else:
            return "South-West"
import requests

def get_address_from_coordinates(latitude, longitude):
    """
    Fetches address details and region based on latitude and longitude using OpenCage Geocoder.
    """
    api_key = 'cd14ce25b911440c9acf8d8ed78a61ef'
    url = f"https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            components = data['results'][0]['components']
            region = determine_region(latitude, longitude)  # Your logic for region determination
            return {
                'road': components.get('road', ''),
                'suburb': components.get('suburb', ''),
                'city': components.get('city', ''),
                'state': components.get('state', ''),
                'country': components.get('country', ''),
                'region': region,
            }
        else:
            return {'error': 'Failed to fetch data from API'}
    except Exception as e:
        return {'error': str(e)}

import requests

def get_full_address_and_region(latitude, longitude):
    """
    Fetches the full address and region from latitude and longitude.
    """
    api_key = 'cd14ce25b911440c9acf8d8ed78a61ef'
    url = f"https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                result = data['results'][0]
                components = result.get('components', {})
                region = determine_region(latitude, longitude)
                return {
                    'road': components.get('road', ''),
                    'suburb': components.get('suburb', ''),
                    'city': components.get('city', ''),
                    'state': components.get('state', ''),
                    'country': components.get('country', ''),
                    'region': region
                }
        return {'error': 'No results found'}
    except Exception as e:
        return {'error': str(e)}

def determine_region(latitude, longitude):
    """
    Determines the region based on latitude and longitude.
    """
    if latitude >= 0:
        return 'North' if longitude >= 0 else 'East'
    else:
        return 'South' if longitude >= 0 else 'West'
