import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import os

def find_athlete_profile_link(driver, first_name, last_name, country):
    """
    Finds the athlete profile link based on the provided first name, last name, and country.

    Args:
    driver: Selenium WebDriver instance.
    first_name (str): The first name of the athlete.
    last_name (str): The last name of the athlete.
    country (str): The country of the athlete.

    Returns:
    str: The href attribute of the athlete's profile link, if found.
    None: If no link is found.
    """

    # Wait for the search results to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'AthleteSearch_name__2z8I1'))
        )
    except TimeoutException:
        print("Timed out waiting for page to load")
        return None
    
    # Create the href pattern to search for
    href_pattern = f"/athletes/{country.lower().replace(' ', '-')}/{first_name.lower()}-{last_name.lower()}-"
    
    # Find all athlete name cells on the page
    athlete_cells = driver.find_elements(By.CLASS_NAME, 'AthleteSearch_name__2z8I1')

    # Loop through each cell to find a matching link
    for cell in athlete_cells:
        link = cell.find_element(By.TAG_NAME, 'a')
        if href_pattern in link.get_attribute('href'):
            profile_link = link.get_attribute('href')
            print(profile_link)
            return profile_link

    return None

def get_outdoor_results(driver, athlete_data):
    try:
        # Find all divs containing the distance name and corresponding table
        race_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'profileStatistics_statsTable__')]")

        for div in race_divs:
            # Extract the distance name
            distance_name = div.find_element(By.CLASS_NAME, 'profileStatistics_tableName__2qDVZ').text

            # Find the corresponding table within the div
            table = div.find_element(By.TAG_NAME, 'table')

            # Get the table's HTML
            table_html = table.get_attribute('outerHTML')

            # Parse with BeautifulSoup
            soup = BeautifulSoup(table_html, 'html.parser')

            # Extract data from the table
            for row in soup.find_all('tr')[1:]:  # Skip header row
                columns = row.find_all('td')
                date = columns[0].text.strip()
                competition = columns[1].text.strip()
                result = columns[3].text.strip()
                wind_speed = columns[4].text.strip() if len(columns) > 4 and columns[4].text.strip() else 'N/A'

                # Append the result to athlete_data
                athlete_data['results'].append({
                    'distance': distance_name,
                    'date': date,
                    'competition': competition,
                    'result': result,
                    'wind_speed': wind_speed
                })

    except Exception as e:
        print(f"An error occurred: {e}")

# Read athletes from the CSV file
athletes_df = pd.read_csv('athletes.csv')

# Set up the driver (e.g., ChromeDriver)
driver = webdriver.Chrome()

# List to store athlete results
athletes_results = []

# Counter for batches of 5 athletes
athlete_counter = 0

# Check if the file already exists
file_exists = os.path.exists('athlete_results.csv')

# Open the file for writing in append mode or create a new file if it doesn't exist
with open('athlete_results.csv', 'a', encoding='utf-8') as file:
    # Write the header row if the file is newly created
    if not file_exists:
        file.write("Name,Country,Distance,Date,Competition,Result,Wind Speed\n")

    # Iterate over each athlete in the dataframe
    for index, row in athletes_df.iterrows():
        athlete_name = row['Athlete']
        country = row['Country']

        # Splitting the athlete's name to handle first and last names, including hyphenated names
        name_parts = athlete_name.split(' ')
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Format the country string to replace spaces with hyphens
        formatted_country = country.replace(' ', '-')

        # Go to the athlete search page
        driver.get('https://worldathletics.org/athletes')

        # Find the search input and submit the athlete's name
        try:
            wait = WebDriverWait(driver, 10)
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.AthleteSearch_searchInput__37_Nk')))
            search_input.clear()  # Clear the field before sending keys
            search_input.send_keys(athlete_name)  # Use the full athlete name
            search_input.send_keys(Keys.RETURN)

            # Find the athlete's profile link
            profile_link = find_athlete_profile_link(driver, first_name, last_name, formatted_country)

            if profile_link:
                driver.get(profile_link)
            else:
                print(f"Profile not found for {athlete_name}")
                continue

            # Wait for the tabs to be visible and clickable
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_all_elements_located((By.CLASS_NAME, 'profileStatistics_tab__1Blal'))
                )
            except TimeoutException:
                print("Timeout while waiting for tabs to be visible")

            # Find the 'Results' tab
            results_tab = None
            tabs = driver.find_elements(By.CLASS_NAME, 'profileStatistics_tab__1Blal')
            for tab in tabs:
                if 'Results' in tab.text:
                    results_tab = tab
                    break

            if results_tab:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", results_tab)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'profileStatistics_tab__1Blal')))
                    results_tab.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", results_tab)
            else:
                print("Results tab not found")

            # Find the year selector dropdown
            year_selector = Select(driver.find_element(By.ID, 'resultsYearSelect'))
            years = [int(option.get_attribute('value')) for option in year_selector.options]
            years.sort()
            current_year_index = years.index(max(years))
            desired_years = years[max(current_year_index-2, 0):current_year_index+1]

            # Create a dictionary to store athlete's results
            athlete_data = {'name': athlete_name, 'country': country, 'results': []}

            for year in desired_years:
                year_selector.select_by_value(str(year))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'profileStatistics_table__1o71p')))
                get_outdoor_results(driver, athlete_data)

            # Append data to the athletes_results list
            athletes_results.append(athlete_data)
            athlete_counter += 1
            print(athletes_results)

            # Save data to file every 5 athletes
            if athlete_counter % 5 == 0:
                for athlete in athletes_results:
                    for result in athlete['results']:
                        file.write(f"{athlete['name']},{athlete['country']},{result['distance']},{result['date']},{result['competition']},{result['result']},{result['wind_speed']}\n")

                athletes_results = []  # Clear the list after saving

        except TimeoutException:
            print(f"Timeout occurred while searching for {athlete_name}")
            continue

# Save any remaining data that didn't fit into a batch of 5
for athlete in athletes_results:
    for result in athlete['results']:
        file.write(f"{athlete['name']},{athlete['country']},{result['distance']},{result['date']},{result['competition']},{result['result']},{result['wind_speed']}\n")

# Close the driver
driver.quit()
