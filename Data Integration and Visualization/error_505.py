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
    """Extract article information from the raw html."""
    try:
        headline = card.find('h4', 's-title').text
        source = card.find("span", 's-source').text
        posted = card.find('span', 's-time').text.replace('·', '').strip()
        description = card.find('p', 's-desc').text.strip()
        raw_link = card.find('a').get('href')
        unquoted_link = requests.utils.unquote(raw_link)
        pattern = re.compile(r'RU=(.+)\/RK')
        match = re.search(pattern, unquoted_link)
        clean_link = match.group(1) if match else None

        article = (headline, source, posted, description, clean_link)
        return article
    except Exception as e:
        print(f"Error extracting article: {e}")
        return (None, None, None, None, None)

def get_the_news(search):
    """Run the main program to fetch news articles."""
    template = 'https://news.search.yahoo.com/search?p={}'
    url = template.format(search.replace(" ", "%20"))
    articles = []
    links = set()
    
    start_time = time()
    wait_time = 1

    while True:
        try:
            response = requests.get(url, headers=headers)
            print(f"Fetching URL: {url} | Status Code: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                cards = soup.find_all('div', 'NewsArticle')

                for card in cards:
                    article = get_article(card)
                    link = article[-1]
                    if link and link not in links:
                        links.add(link)
                        articles.append(article)
                break
            elif response.status_code == 500:
                print("Server error 500. Waiting longer before retrying...")
                sleep(wait_time)
                wait_time = min(wait_time * 2, 3600)
            elif response.status_code == 429:
                print("Too many requests. Waiting longer before retrying...")
                sleep(wait_time)
                wait_time = min(wait_time * 2, 3600)
            else:
                print(f"Error fetching news: {response.status_code}")
                sleep(random.uniform(1, 3))

        except requests.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sleep(random.uniform(1, 3))

    end_time = time()
    print(f"Fetching news for '{search}' took {end_time - start_time:.2f} seconds.")
    
    return articles

def save_progress(data, file_name):
    """Save the current progress of fetched news data to a CSV file and verify saving."""
    try:
        df = pd.DataFrame(data, columns=['Date', 'Stock', 'Open Price', 'Articles'])
        df.to_csv(file_name, index=False, encoding='utf-8')
        print(f"Progress saved to {file_name}.")
        
        # Verify file was saved
        try:
            # Check if the file exists and is readable
            saved_df = pd.read_csv(file_name)
            if saved_df.empty:
                print(f"Warning: {file_name} was saved but appears empty.")
            else:
                print(f"File {file_name} saved and verified successfully.")
        except Exception as verify_err:
            print(f"Error verifying saved file {file_name}: {verify_err}")

    except Exception as save_err:
        print(f"Error saving progress to {file_name}: {save_err}")

def get_news_for_dates(stock_symbol, date_range):
    """Fetch news articles and open price for the given stock symbol within the specified date range."""
    results = []
    
    try:
        st = yf.Ticker(stock_symbol)
        his = st.history(start=min(date_range), end=max(date_range))
        df_reset = his.reset_index()
        df_reset['Date'] = pd.to_datetime(df_reset['Date'])
        
        for date_str in date_range:
            try:
                open_price = df_reset.loc[df_reset['Date'] == date_str, 'Open']
                open_price_value = open_price.values[0] if not open_price.empty else None
                
                search_term = f"{stock_symbol} {date_str}"
                articles = get_the_news(search_term)
                
                if articles:
                    article_entries = []
                    for art in articles:
                        article_entries.append(f"Headline: {art[0]}; Source: {art[1]}; Posted: {art[2]}; Description: {art[3]}; Link: {art[4]}")
                    consolidated_articles = "\n".join(article_entries)
                    results.append((date_str, stock_symbol, open_price_value, consolidated_articles))
                else:
                    results.append((date_str, stock_symbol, open_price_value, None))
                
                sleep(0.5)

            except Exception as e:
                print(f"Error fetching news for {stock_symbol} on {date_str}: {e}")
                results.append((date_str, stock_symbol, None, None))
            
    except Exception as e:
        print(f"Error fetching historical data for {stock_symbol}: {e}")

    return results

def fetch_all_news_from_csv(stock_file, start_date, end_date):
    """Read stock symbols from CSV and fetch news for the specified date range."""
    try:
        stocks_df = pd.read_csv(stock_file)
        all_results = []
        date_range = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
        
        start_time = time()
        stocks_symbols = stocks_df['Symbol'][0:5].tolist()
        stocks_symbols = random.sample(stocks_symbols, len(stocks_symbols))

        print(stocks_symbols)
        for stock_symbol in stocks_symbols:
            
            try:
                stock_results = get_news_for_dates(stock_symbol, date_range)

                # Save results for each stock after processing all its dates
                stock_file_name = f'{stock_symbol}_news.csv'
                save_progress(stock_results, stock_file_name)
                all_results.extend(stock_results)
            except Exception as e:
                print(f"Error processing stock {stock_symbol}: {e}")
                continue  # Continue with the next stock

        end_time = time()
        print(f"Fetching news for all stocks took {end_time - start_time:.2f} seconds.")
        
    except Exception as e:
        print(f"Error fetching data from CSV: {e}")

# Example usage with timing
if __name__ == '__main__':
    start_time = time()
    try:
        fetch_all_news_from_csv('/Users/vishnu/Desktop/Erasmus/Fall/Data Integration and Visualization/Data/kaggle_s&p/sp500_companies.csv', '2022-01-01', '2023-12-31')
    except Exception as e:
        print(f"Error in main execution: {e}")
    end_time = time()

    print(f"Program ran in {end_time - start_time:.2f} seconds.")
