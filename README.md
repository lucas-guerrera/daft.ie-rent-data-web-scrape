# Daft.ie Dublin Rental Property Project

Welcome to my Python project, a web scraping application designed to collect and store data from Daft.ie, Ireland's largest and most visited Real Estate website. This project focuses on gathering essential information about Dublin's rental properties listed on the website, including rent prices, number of bedrooms, bathrooms, latitude, longitude, and distance from the city center.

The application performs a daily scrape of Daft.ie to ensure that the collected data is up-to-date and comprehensive. By leveraging web scraping techniques, I can efficiently gather a wide range of property details, providing valuable insights into the rental market.

Once the scraping process is complete, the project proceeds with data exploratory analysis, enabling us to uncover patterns, trends, and statistical information about the rental properties. This analysis helps us gain a deeper understanding of the market dynamics and enables us to make informed decisions.

To ensure data quality, a data cleaning process is applied, which addresses any inconsistencies or missing values within the collected dataset. By cleaning the data, we create a reliable and consistent foundation for further analysis and insights.

Finally, the project stores the cleaned and analyzed data in a local CSV file for easy access and future reference. This local storage solution allows for convenient data retrieval and utilization in various applications or further data processing.

By combining web scraping, data exploration, cleaning, and storage, this Python project provides a comprehensive solution for gathering, analyzing, and utilizing real estate rental data from Daft.ie.

## What am I trying to achieve?

This project aims to provide insights into the current rental market by analyzing listings uploaded on Daft.ie over a minimum duration of 20 consecutive days.

The project's primary goal is not to analyze current rental rates but to provide insights into the rental prices of existing listings on Daft.ie. As such, the data collected may not reflect the average rent in Dublin. However, it can offer valuable information about the rental prices for properties available on the market moving forward.

After the collection of 20 consecutive days of data (06/07/2023 - 26/07/2023), the idea is to train a linear regression model to predict rental prices based on key features like number of bedrooms, number of bathrooms and distance from city centre.

## Common questions you may have

Question: What if someone lists the rent one day and updates it the other? How does it handle duplicate data?

Answer: The script checks whether a listing's daft_id is already stored in the CSV file. If it is, the script compares the current rent with the previously recorded rent. If the rent has changed, the updated listing is added to the CSV file. If the listing remains the same, with no rent change or address update, it will be appended in the CSV file.

Question: How is distance from city centre calculated?

Answer: The distance from the city centre is calculated based on the straight-line distance from Temple Bar, a renowned pub situated in the heart of Dublin. This distance measurement serves as a radius from Temple Bar and provides a general understanding of each property's proximity to the city centre.


