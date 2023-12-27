import requests
import pandas as pd
import time

API_ENDPOINT = "https://nominatim.openstreetmap.org/search"

def get_lat_long(location, user_agent):
    params = {'q': location, 'format': 'json'}
    headers = {'User-Agent': user_agent}
    response = requests.get(API_ENDPOINT, params=params, headers=headers)
    if response.ok:
        results = response.json()
        if results:
            return results[0]['lat'], results[0]['lon']
    return None, None

# Update with your file path
file_path = 'locations2.xlsx'
df = pd.read_excel(file_path)

# Replace 'MyGeocodingApp' with a unique name for your application
user_agent = "MyGeocodingApp"

for index, row in df.iterrows():
    lat, lon = get_lat_long(row['Location'], user_agent)
    df.at[index, 'Latitude'] = lat
    df.at[index, 'Longitude'] = lon
    print(f"Processed: {row['Location']} - Latitude: {lat}, Longitude: {lon}")
    time.sleep(1)  # Sleep for 1 second to respect the rate limit

df.to_excel(file_path, index=False)
