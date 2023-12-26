from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

current_directory = os.getcwd()

# Combine the current directory with the filename
csv_file_path = os.path.join(current_directory, 'FilteredCountries.csv')

# Read the CSV file
country_codes_df = pd.read_csv(csv_file_path)


# List of disciplines
disciplines = ['100', '200', '400', '800', '1500', '3000', '5000', '10K', '110H', '100H', '400H']

# Selenium setup
driver = webdriver.Chrome()

seen_names = set()  # To track seen athlete names

# Function to scrape athlete names and DOBs
def scrape_athletes(country_code, discipline, gender, seen_names, required_number=5):
    url = f"https://worldathletics.org/athletes-home?countryCode={country_code}&disciplineCode={discipline}&gender={gender}&environment=outdoor"
    driver.get(url)
    time.sleep(5)  # Wait for the JavaScript to load the content

    athletes_data = []
    athlete_elements = driver.find_elements(By.CSS_SELECTOR, "td[class*='AthleteSearch_name'] a[href*='/athletes/']")

    # Counter for unique athletes found
    athletes_found = 0

    for athlete_element in athlete_elements:
        if athletes_found >= required_number:
            break  # Stop if we have found the required number of athletes

        athlete_name = athlete_element.text.strip()
        reversed_name = ' '.join(athlete_name.split()[::-1]).lower()

        # Check if the athlete has already been processed
        if reversed_name in seen_names:
            continue  # Skip this athlete and go to the next one

        seen_names.add(reversed_name)  # Mark this athlete as seen
        athlete_profile_url = athlete_element.get_attribute('href')

        # Open the athlete's profile in a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(athlete_profile_url)
        
        # Wait for the page to load
        time.sleep(3)

        # Scrape the DOB from the athlete's profile
        try:
            dob_element = driver.find_element(By.CSS_SELECTOR, "div.profileBasicInfo_dob__1hssI")
            dob_text = dob_element.text.strip()
        except:
            dob_text = None  # If DOB not found

        # Close the current tab
        driver.close()
        
        # Switch back to the main tab
        driver.switch_to.window(driver.window_handles[0])

        # Append the athlete's name and DOB to the list and increment the counter
        athletes_data.append((reversed_name, dob_text))
        athletes_found += 1

    return athletes_data

def save_data_to_csv(data, file_path):
    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=['CountryCode', 'Nationality', 'Country', 'Discipline', 'Gender', 'Athlete', 'DOB'])
    if not os.path.isfile(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode='a', header=False, index=False)


def get_last_saved_point(file_path):
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        if not df.empty:
            last_row = df.iloc[-1]
            return last_row['CountryCode'], str(last_row['Discipline']), last_row['Gender']
    return None, None, None


last_country_code, last_discipline, last_gender = get_last_saved_point('athletes.csv')

resume = False
if last_country_code and last_discipline and last_gender:
    resume = True


data = []
batch_size = 50  # Adjust as needed

for _, row in country_codes_df.iterrows():
    country_code = row['Codes']
    nationality = row['Nationality']
    country_name = row['Country']

    if resume and country_code < last_country_code:
        continue  # Skip to the last saved country code

    for discipline in disciplines:
        if resume and discipline < last_discipline:
            continue  # Skip to the last saved discipline

        for gender in ['male', 'female']:
            if resume and gender < last_gender:
                continue  # Skip to the last saved gender

            resume = False  # Reset resume flag after reaching resumption point

            athletes_data = scrape_athletes(country_code, discipline, gender, seen_names)
            for athlete_name, athlete_dob in athletes_data:
                data.append([country_code, nationality, country_name, discipline, gender, athlete_name, athlete_dob])

                if len(data) >= batch_size:
                    save_data_to_csv(data, 'athletes.csv')
                    data = []  # Reset data after saving

# Save any remaining data after the loop
if data:
    save_data_to_csv(data, 'athletes.csv')

driver.quit()