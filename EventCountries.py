import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_country(location, geolocator):
    retries = 3  # Increase if needed
    for attempt in range(retries):
        try:
            # Increased timeout
            location_info = geolocator.geocode(location, exactly_one=True, language="en", timeout=10)
            if location_info:
                country = location_info.address.split(",")[-1].strip()
                print(f"Attempt {attempt + 1}: Location: {location}, Country: {country}")
                return country
            else:
                # Handle None response
                print(f"Attempt {attempt + 1}: Location: {location} not found.")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Attempt {attempt + 1}: Timeout or service error occurred: {e}")
            continue  # or implement backoff strategy
    # After all retries
    print(f"All retries exhausted for location: {location}")
    return "NAN"

def save_progress(df, output_file):
    df.to_csv(output_file, index=False)
    print("Progress saved.")

# Initialize the geolocator
geolocator = Nominatim(user_agent="country_finder")

# Input and output file paths
input_file = 'ConsolidatedEvents.csv'
output_file = "ConsolidatedCountries.csv"

# Read the CSV file, ensuring there's a Country column with default empty strings
df = pd.read_csv(input_file)
if 'Country' not in df.columns:
    df['Country'] = ''

# Process locations and update the 'Country' column
save_interval = 10  # Save after every 10 locations processed
for index, row in df.iterrows():
    # Check if the country is already found, skip if so
    if pd.isna(row['Country']) or row['Country'] == '':
        country = get_country(row['Location'], geolocator)
        df.at[index, 'Country'] = country
        if index % save_interval == 0:
            save_progress(df, output_file)

# Final save after loop completion
save_progress(df, output_file)
