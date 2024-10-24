import re
from time import sleep, time
from bs4 import BeautifulSoup
import requests
import yfinance as yf
import pandas as pd
import random

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
}

def get_article(card):
    """Extract article information from the raw html"""
    try:
        headline = card.find('h4', 's-title').text
        source = card.find("span", 's-source').text
        posted = card.find('span', 's-time').text.replace('·', '').strip()
        description = card.find('p', 's-desc').text.strip()
        raw_link = card.find('a').get('href')
        unquoted_link = requests.utils.unquote(raw_link)
        pattern = re.compile(r'RU=(.+)\/RK')
        match = re.search(pattern, unquoted_link)
        clean_link = match.group(1) if match else None  # Handle cases where no match is found

        article = (headline, source, posted, description, clean_link)
        return article
    except Exception as e:
        print(f"Error extracting article: {e}")
        return (None, None, None, None, None)  # Return placeholders if extraction fails

def get_the_news(search):
    """Run the main program to fetch news articles."""
    template = 'https://news.search.yahoo.com/search?p={}'
    url = template.format(search.replace(" ", "%20"))
    articles = []
    links = set()
    
    start_time = time()  # Start timing for news fetching
    retries = 3  # Number of retries for failed requests

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            print(f"Fetching URL: {url} | Status Code: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                cards = soup.find_all('div', 'NewsArticle')

                # Extract articles from the page
                for card in cards:
                    article = get_article(card)
                    link = article[-1]
                    if link and link not in links:
                        links.add(link)
                        articles.append(article)

                break  # Break the loop if successful
            else:
                print(f"Error fetching news: {response.status_code}")
                if attempt < retries - 1:
                    print("Retrying...")
                    sleep(random.uniform(1, 3))  # Random sleep to avoid hitting the server too quickly
        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < retries - 1:
                print("Retrying...")
                sleep(random.uniform(1, 3))  # Random sleep to avoid hitting the server too quickly

    end_time = time()  # End timing for news fetching
    print(f"Fetching news for '{search}' took {end_time - start_time:.2f} seconds.")
    
    return articles

def get_news_for_dates(stock_symbol, date_range):
    """Fetch news articles and open price for the given stock symbol within the specified date range."""
    results = []
    
    try:
        # Fetch stock data for the entire date range
        st = yf.Ticker(stock_symbol)
        his = st.history(start=min(date_range), end=max(date_range))
        
        # Reset index and ensure 'Date' is in datetime format
        df_reset = his.reset_index()
        df_reset['Date'] = pd.to_datetime(df_reset['Date'])  # Ensure Date column is datetime
        
        for date_str in date_range:
            try:
                # Get the opening price for the specific date
                open_price = df_reset.loc[df_reset['Date'] == date_str, 'Open']
                open_price_value = open_price.values[0] if not open_price.empty else None
                
                search_term = f"{stock_symbol} {date_str}"
                
                # Get news articles
                articles = get_the_news(search_term)
                
                # Consolidate articles into a single entry
                if articles:
                    article_entries = []
                    for art in articles:  # Iterate over each article
                        article_entries.append(f"Headline: {art[0]}; Source: {art[1]}; Posted: {art[2]}; Description: {art[3]}; Link: {art[4]}")
                    consolidated_articles = "\n".join(article_entries)
                    results.append((date_str, stock_symbol, open_price_value, consolidated_articles))
                else:
                    results.append((date_str, stock_symbol, open_price_value, None))  # No articles found
            
                sleep(0.5)  # Sleep to avoid hitting the server too fast

            except Exception as e:
                print(f"Error fetching news for {stock_symbol} on {date_str}: {e}")
                results.append((date_str, stock_symbol, None, None))  # Append placeholders on error

    except Exception as e:
        print(f"Error fetching historical data for {stock_symbol}: {e}")

    return results

def fetch_all_news_from_csv(stock_file, start_date, end_date):
    """Read stock symbols from CSV and fetch news for the specified date range."""
    try:
        stocks_df = pd.read_csv(stock_file)
        all_results = []
        
        # Generate date range
        date_range = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()

        # Iterate over stock symbols correctly
        start_time = time()  # Start timing for stock fetching
        for stock_symbol in stocks_df['Symbol'][0:25]:  # Iterate through the 'Symbol' column directly
            try:
                stock_results = get_news_for_dates(stock_symbol, date_range)
                all_results.extend(stock_results)  # Add the results for this stock to the overall list
            except Exception as e:
                print(f"Error processing stock {stock_symbol}: {e}")

        end_time = time()  # End timing for stock fetching
        print(f"Fetching news for all stocks took {end_time - start_time:.2f} seconds.")
        
        # Create DataFrame and save to CSV
        final_df = pd.DataFrame(all_results, columns=['Date', 'Stock', 'Open Price', 'Articles'])
        final_df.to_csv('test.csv', index=False, encoding='utf-8')
        
    except Exception as e:
        print(f"Error fetching data from CSV: {e}")

# Example usage with timing
if __name__ == '__main__':
    start_time = time()
    try:
        fetch_all_news_from_csv('/Users/vishnu/Desktop/Erasmus/Fall/Data Integration and Visualization/Data/kaggle_s&p/sp500_companies.csv', '2021-01-01', '2024-10-21')
    except Exception as e:
        print(f"Error in main execution: {e}")
    end_time = time()

    print(f"Program ran in {end_time - start_time:.2f} seconds.")
