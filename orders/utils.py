import requests
from django.conf import settings

def get_distance_duration(lat1, lng1, lat2, lng2):
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={lat1},{lng1}&destinations={lat2},{lng2}&key={api_key}"
    )

    response = requests.get(url)
    data = response.json()
    print("Google API response:", data)

    if data["status"] == "OK" and data["rows"]:
        element = data["rows"][0]["elements"][0]
        if element["status"] == "OK":
            return {
                "distance_text": element["distance"]["text"],
                "distance_value": element["distance"]["value"],  # in meters
                "duration_text": element["duration"]["text"],
                "duration_value": element["duration"]["value"]  # in seconds
            }
    return None