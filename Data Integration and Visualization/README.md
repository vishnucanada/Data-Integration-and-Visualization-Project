# Data Integration Project

## Overview
The Data Integration Project aims to combine information from multiple data sources into a unified CSV file that provides comprehensive insights for visualization purposes. The project integrates data from a Kaggle CSV file, the `yfinance` library, and Yahoo News. The primary objective is to explore the relationship between news sentiment and stock prices, facilitating further analysis and visualization.

## Main Code
The core functionality of this project is encapsulated in the `data_integration.py` file. This script orchestrates the data retrieval and integration process, ensuring a seamless merging of data from the three sources.

## Components
### 1. Kaggle CSV File
In the `Data` folder, you will find the `sp500.csv` file. This file contains essential information about stocks, including the name, symbol, abbreviations, and descriptions. For the purposes of this project, we focus specifically on the stock **name** and **symbol**.

### 2. yfinance Library
The second data source is the `yfinance` library, a powerful tool that fetches real-time stock prices based on their symbols. This library is particularly useful because it allows for continuous updates and can retrieve the entire timeline of a stock, starting from its Initial Public Offering (IPO). This capability is crucial for analyzing historical stock performance alongside news sentiment.

### 3. Yahoo News Scraper
The third component of this project is the news scraper, which aggregates relevant news articles based on the stocks retrieved from the previous two sources. For each stock and date combination, the scraper fetches news headlines, providing valuable context for understanding market movements. The news articles are appended as an additional attribute in the final dataset.

## High-Level Overview
The workflow of the project can be broken down into several key steps:
1. **Stock Selection**: We retrieve the top **'x'** stocks in the S&P 500. For this project, we have chosen **x = 25**.
2. **Timeline Definition**: A specific date range is established to fetch information. For example, we may choose to analyze data from **2010-01-01 to 2024-12-31**.
3. **Data Retrieval**:
   - For each stock, the script fetches the **Open** price for each date within the defined timeline.
   - Once the prices are obtained, the scraper extracts the top news headlines for each stock on each specific date.
4. **Data Integration**: All gathered information is then compiled into a single CSV file, creating a comprehensive dataset for further analysis.

### Overall Concept
The primary goal of this project is to deploy sentiment analysis techniques to determine if the sentiment of news articles significantly influences stock prices. By analyzing the sentiment in conjunction with stock price movements, we aim to identify patterns and correlations that could inform trading strategies.

## Running the Code
The `sample_data.csv` file included in the repository serves as a sample output of the final CSV file. This sample contains data for five stocks over a single day, demonstrating the format and structure of the output.

### Prerequisites
Before running the code, ensure you have the necessary dependencies installed. You may need to install the following libraries:
- `pandas`
- `yfinance`
- `beautifulsoup4` (for web scraping)
- `requests` (for fetching data)

### Instructions
1. **Modify Date Range**: In `data_integration.py`, locate line 141 and modify the date range to your preferred timeline.
2. **Select Stocks**: In line 127, adjust the `stock_symbols` variable to specify how many stocks you want to analyze. For example, using `(0:5)` will give you the top five stocks.
3. **Update File Paths**: Ensure that all hardcoded file paths are correctly set according to your local environment.
4. **Execute the Script**: Run the `data_integration.py` script to initiate the data fetching and integration process.

## Conclusion
This Data Integration Project serves as a foundational tool for exploring the intricate relationship between stock market movements and news sentiment. By merging diverse data sources into a single dataset, it lays the groundwork for deeper analysis and visualization, paving the way for insights that could inform trading decisions.
