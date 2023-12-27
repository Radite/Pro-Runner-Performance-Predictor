import requests
import pandas as pd
import time

# Nominatim API for geocoding
NOMINATIM_API_ENDPOINT = "https://nominatim.openstreetmap.org/search"
# Open Elevation API for fetching altitude
OPEN_ELEVATION_API_ENDPOINT = "https://api.open-elevation.com/api/v1/lookup"

# Function to get latitude and longitude from Nominatim
def get_lat_long(location, user_agent):
    params = {'q': location, 'format': 'json'}
    headers = {'User-Agent': user_agent}
    response = requests.get(NOMINATIM_API_ENDPOINT, params=params, headers=headers)
    if response.ok:
        results = response.json()
        if results:
            return results[0]['lat'], results[0]['lon']
    return None, None

# Function to get altitude from Open Elevation API
def get_altitude(lat, lon):
    params = {'locations': f"{lat},{lon}"}
    response = requests.get(OPEN_ELEVATION_API_ENDPOINT, params=params)
    if response.ok:
        results = response.json()
        # Extracting altitude
        if results and 'results' in results and len(results['results']) > 0:
            return results['results'][0]['elevation']
    return None

# Function to save DataFrame to excel
def save_to_excel(df, file_path):
    df.to_excel(file_path, index=False)

# Load the xlsx file
file_path = 'locations.xlsx'  # Update with your file path
df = pd.read_excel(file_path)

# Find the first row with an empty 'Altitude' cell to resume from
start_index = df['Altitude'].isnull().argmax() if df['Altitude'].isnull().any() else 0

# Replace with your application's unique user-agent name
user_agent = "MyGeocodingApp"

for index in range(start_index, len(df)):
    row = df.iloc[index]
    # Check if Altitude is already filled
    if pd.isna(row['Altitude']):
        lat, lon = get_lat_long(row['Location'], user_agent)
        if lat and lon:
            altitude = get_altitude(lat, lon)
            df.at[index, 'Latitude'] = lat
            df.at[index, 'Longitude'] = lon
            df.at[index, 'Altitude'] = altitude
            print(f"Processed: {row['Location']} - Latitude: {lat}, Longitude: {lon}, Altitude: {altitude}")
        time.sleep(1)  # Sleep to respect Nominatim's rate limit

        # Save to Excel file after every 5 iterations
        if (index - start_index + 1) % 5 == 0:
            save_to_excel(df, file_path)
            print("Saved progress to excel.")

# Save any remaining progress to excel
save_to_excel(df, file_path)