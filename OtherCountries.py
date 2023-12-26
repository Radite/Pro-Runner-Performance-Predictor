import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# List or dictionary of US state abbreviations
us_states = {
    "AL": "United States", "AK": "United States", "AZ": "United States", "AR": "United States",
    "CA": "United States", "CO": "United States", "CT": "United States", "DE": "United States",
    "FL": "United States", "GA": "United States", "HI": "United States", "ID": "United States",
    "IL": "United States", "IN": "United States", "IA": "United States", "KS": "United States",
    "KY": "United States", "LA": "United States", "ME": "United States", "MD": "United States",
    "MA": "United States", "MI": "United States", "MN": "United States", "MS": "United States",
    "MO": "United States", "MT": "United States", "NE": "United States", "NV": "United States",
    "NH": "United States", "NJ": "United States", "NM": "United States", "NY": "United States",
    "NC": "United States", "ND": "United States", "OH": "United States", "OK": "United States",
    "OR": "United States", "PA": "United States", "RI": "United States", "SC": "United States",
    "SD": "United States", "TN": "United States", "TX": "United States", "UT": "United States",
    "VT": "United States", "VA": "United States", "WA": "United States", "WV": "United States",
    "WI": "United States", "WY": "United States"
}
import re

def get_country_from_event(event, geolocator, location_country_dict):
    # Split the event into possible location strings and reverse it
    possible_locations = event.split(' ')[::-1]

    # Define words to exclude
    exclude_words = {'Diamond','High','Meeting','Athletics','Championship','la','Province','Events', 'Stadiom', 'Stadium', 'Town','Permit','Event','Open','Area','Stade','Promotional','Stadion','Invitational','National','Pre-Programme','Combined','de','Games','College','events','Race','A','B','Olympiastadion','Memorial', 'Discipline', 'Development','(i)','School','Elite','TRACKS','in','Tracks',"'98",'2000','Spanish','de','Center','Limit','Special','Memorial','events'}
    # Define pattern to exclude (e.g., 'U' followed by numbers like U20, U18)
    exclude_pattern = r'U\d+'

    for location in possible_locations:
        # Skip excluded words and patterns
        if 'stadion' in location.lower() or re.match(exclude_pattern, location):
            continue

        if location in exclude_words or re.match(exclude_pattern, location):
            continue

        # Check if it's a known US state abbreviation
        if location in us_states:
            return us_states[location], location

        # Check if the location is already in the dictionary
        if location in location_country_dict:
            return location_country_dict[location], location
        else:
            country = get_country(location, geolocator)
            if country != "NAN":
                location_country_dict[location] = country
                return country, location
    return "NAN", ""




def get_country(location, geolocator):
    retries = 3
    for attempt in range(retries):
        try:
            location_info = geolocator.geocode(location, exactly_one=True, language="en", timeout=10)
            if location_info:
                country = location_info.address.split(",")[-1].strip()
                return country
            else:
                print(f"Location part '{location}' not found.")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Timeout or service error occurred: {e}")
            continue
    return "NAN"

def save_progress(df, output_file):
    df.to_csv(output_file, index=False)
    print("Progress saved.")

# Initialize the geolocator
geolocator = Nominatim(user_agent="country_finder")

# Input and output file paths
input_file = 'Others.csv'
output_file = "OtherCountries.csv"

# Read the CSV file
df = pd.read_csv(input_file)
if 'Country' not in df.columns or 'Location' not in df.columns:
    df['Country'] = ''
    df['Location'] = ''

# Dictionary to hold known location-country pairs
location_country_dict = {}

# Process events and update the 'Country' and 'Location' columns
save_interval = 5  # Save after every 5 updates
for index, row in df.iterrows():
    if pd.isna(row['Country']) or row['Country'] == '':
        country, location_part = get_country_from_event(row['Event'], geolocator, location_country_dict)
        if country != "NAN":
            df.at[index, 'Country'] = country
            df.at[index, 'Location'] = location_part
            print(f"Updated Row {index}: Country: {country}, Location part used: {location_part}")
        if index % save_interval == 0:
            save_progress(df, output_file)

# Final save after loop completion
save_progress(df, output_file)
