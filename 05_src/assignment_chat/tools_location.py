from langchain.tools import tool
import json
import requests


@tool
def get_longitude_latitude(city:str):
    """
    Return longitude and latitude of a location from latlng API
    """
    url = "https://api.latlng.work/api"
    params = {
        "q": city
    }
    response = requests.get(url, params=params)
    resp_dict = json.loads(response.text)
    coordinates_dict = {
        "lat": resp_dict["features"]["geometry"]["coordinates"][0],
        "lng": resp_dict["features"]["geometry"]["coordinates"][1],
        "location": city
    }
    return coordinates_dict