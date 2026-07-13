from langchain.tools import tool
import requests
import json

@tool
def get_sunrise_sunset(lng:float, lat:float, date:str='today', city=str) -> str:
    """
    Makes API request to sunrise-sunset, and returns the date, timezone, latitude, longitude, sunrise and sunset
    """
    url = "https://api.sunrise-sunset.org/v2"
    params = {
        "lng": lng,
        "lat": lat,
        "date": date,
    }
    response = requests.get(url, params=params)
    resp_dict = json.loads(response.text)
    sunrise_sunset = {
        "date": resp_dict["date"],
        "timezone": resp_dict["tzid"],
        "UTC_offset": resp_dict["utc_offset"],
        "City": city,
        "latitude": resp_dict["lat"],
        "longitude": resp_dict["lng"],
        "sunrise": resp_dict["sunrise"],
        "sunset": resp_dict["sunset"]
    }
    return sunrise_sunset