import pandas as pd

# Read the CSV file into a DataFrame with specified encoding
# Try different encodings if needed (e.g., 'ISO-8859-1', 'latin1')
encodings_to_try = ['utf-8', 'ISO-8859-1', 'latin1']
for encoding in encodings_to_try:
    try:
        df = pd.read_csv('ConsolidatedCountries.csv', encoding=encoding)
        break  # If successful, break the loop
    except UnicodeDecodeError:
        print(f"Failed to read with encoding '{encoding}'")

# Function to map state abbreviations to full state names
def map_state_abbreviations(state_abbr):
    state_mapping = {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        'AR': 'Arkansas',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'IA': 'Iowa',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'ME': 'Maine',
        'MD': 'Maryland',
        'MA': 'Massachusetts',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MS': 'Mississippi',
        'MO': 'Missouri',
        'MT': 'Montana',
        'NE': 'Nebraska',
        'NV': 'Nevada',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NY': 'New York',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VT': 'Vermont',
        'VA': 'Virginia',
        'WA': 'Washington',
        'WV': 'West Virginia',
        'WI': 'Wisconsin',
        'WY': 'Wyoming'
    }
    return state_mapping.get(state_abbr, state_abbr)

# Function to update "Location" and "Country" columns
def update_location_and_country(row):
    event = row['Event']
    parts = event.split()
    last_word = parts[-1]
    if len(last_word) == 2:  # Check if the last word is a state abbreviation
        full_state_name = map_state_abbreviations(last_word)
        row['Location'] = full_state_name
        row['Country'] = 'United States'
        print(f"Updated Location to: {full_state_name}, Country to: United States for Event: {event}")
    return row

# Apply the update_location_and_country function to each row
df = df.apply(update_location_and_country, axis=1)

# Save the updated DataFrame back to a CSV file
df.to_csv('updatedConsolidated.csv', index=False)
