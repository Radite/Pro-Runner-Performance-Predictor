from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

current_directory = os.getcwd()
print(current_directory)

# Combine the current directory with the filename
csv_file_path = os.path.join(current_directory, 'FilteredCountries.xlsx')

# Read the CSV file
country_codes_df = pd.read_csv(csv_file_path)


# List of disciplines
disciplines = ['100', '200', '400', '800', '1500', '3000', '5000', '10K', '110H', '100H', '400H']

# Selenium setup
driver = webdriver.Chrome()

seen_names = set()  # To track seen athlete names

# Function to scrape athlete names and DOBs
def scrape_athletes(country_code, discipline, gender, seen_names, required_number=10):
    url = f"https://worldathletics.org/athletes-home?countryCode={country_code}&disciplineCode={discipline}&gender={gender}&environment=outdoor"
    driver.get(url)
    time.sleep(5)  # Wait for the JavaScript to load the content

    athletes_data = []
    athlete_elements = driver.find_elements(By.CSS_SELECTOR, "td[class*='AthleteSearch_name'] a[href*='/athletes/']")

    # Counter for unique athletes found
    athletes_found = 0

    for athlete_element in athlete_elements:
        print(seen_names)
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

data = []

for _, row in country_codes_df.iterrows():
    country_code = row['Codes']
    nationality = row['Nationality']
    country_name = row['Country']

    for discipline in disciplines:
        for gender in ['male', 'female']:
            athletes_data = scrape_athletes(country_code, discipline, gender, seen_names)
            for athlete_name, athlete_dob in athletes_data:
                data.append([country_code, nationality, country_name, discipline, gender, athlete_name, athlete_dob])


# Close the WebDriver
driver.quit()

# Create a DataFrame and save to CSV
df = pd.DataFrame(data, columns=['CountryCode', 'Nationality', 'Country', 'Discipline', 'Gender', 'Athlete', 'DOB'])
df.to_csv('athletes.csv', index=False)
