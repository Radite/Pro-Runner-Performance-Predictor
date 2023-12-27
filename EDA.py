import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('Final.csv')

# Convert 'Event Date' to datetime
data['Event Date'] = pd.to_datetime(data['Event Date'], format='%d-%b-%y', errors='coerce')

# Settings to improve plot readability
plt.rcParams.update({'figure.max_open_warning': 0})  # For opening multiple figures
sns.set(style="whitegrid")  # For grid background in plots

# Analysis separated by Distance, including Event Date, Age, and Country
unique_distances = data['Distance'].unique()

for distance in unique_distances:
    print(f"\nAnalysis for Distance: {distance}")
    data_distance = data[data['Distance'] == distance]
    
    
    # Gender distribution for the specific distance
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Gender', data=data_distance)
    plt.title(f'Gender Distribution for {distance}')
    plt.show()

    # Average RaceTime by Gender for the specific distance
    plt.figure(figsize=(8, 6))
    sns.barplot(x='Gender', y='RaceTime', data=data_distance)
    plt.title(f'Average RaceTime by Gender for {distance}')
    plt.show()
    
    # RaceTime Distribution for the specific distance
    plt.figure(figsize=(8, 6))
    sns.histplot(data_distance['RaceTime'], kde=True)
    plt.title(f'RaceTime Distribution for {distance}')
    plt.show()
    
    # Wind Speed vs. RaceTime for the specific distance
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='Wind', y='RaceTime', data=data_distance)
    plt.title(f'Wind Speed vs. RaceTime for {distance}')
    plt.show()
    
    # Altitude vs. RaceTime for the specific distance
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='Altitude', y='RaceTime', data=data_distance)
    plt.title(f'Altitude vs. RaceTime for {distance}')
    plt.show()

    # Event Date vs. RaceTime for the specific distance, separated by year
    data_distance['Event Date'] = pd.to_datetime(data_distance['Event Date'])  # Ensure datetime type
    data_distance['Event Year'] = data_distance['Event Date'].dt.year
    years = sorted(data_distance['Event Year'].unique())
    
    for year in years:
        plt.figure(figsize=(8, 6))
        data_year = data_distance[data_distance['Event Year'] == year]
        sns.scatterplot(x=data_year['Event Date'].dt.month, y='RaceTime', data=data_year)
        plt.title(f'Event Date vs. RaceTime for {distance} ({year})')
        plt.xlabel('Month')
        plt.xticks(range(1, 13))
        plt.show()

    # Age vs. RaceTime for the specific distance
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='Age', y='RaceTime', data=data_distance)
    plt.title(f'Age vs. RaceTime for {distance}')
    plt.show()

    # Country vs. RaceTime for the specific distance (only if unique countries <= 20)
    if len(data_distance['Country'].unique()) <= 20:
        plt.figure(figsize=(15, 8))
        ax = sns.boxplot(x='Country', y='RaceTime', data=data_distance)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.title(f'RaceTime Distribution by Country for {distance}')
        plt.show()
        print(f"\nCountry Statistics for Distance: {distance}")
        countries = data_distance['Country'].unique()
        for country in countries:
            country_data = data_distance[data_distance['Country'] == country]
            min_race_time = country_data['RaceTime'].min()
            max_race_time = country_data['RaceTime'].max()
            q1_race_time = country_data['RaceTime'].quantile(0.25)
            median_race_time = country_data['RaceTime'].median()
            q3_race_time = country_data['RaceTime'].quantile(0.75)
            
            print(f"\nCountry: {country} - Distance: {distance}")
            print(f"Min: {min_race_time:.2f}")
            print(f"25th Percentile (Q1): {q1_race_time:.2f}")
            print(f"Median: {median_race_time:.2f}")
            print(f"75th Percentile (Q3): {q3_race_time:.2f}")
            print(f"Max: {max_race_time:.2f}")
         # Calculate and plot correlation matrix for selected numerical variables
        plt.figure(figsize=(10, 8))
        # Selecting a subset of the data with relevant numerical variables
        numerical_data = data_distance[['RaceTime', 'Age', 'Wind', 'Altitude']]
        corr_matrix = numerical_data.corr()  # Calculating the correlation matrix
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title(f'Correlation Matrix for {distance}')
        plt.show()



print("Analysis completed for each Distance, including Event Date, Age, and Country.")
