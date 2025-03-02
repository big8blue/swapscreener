import requests
import pandas as pd

# CoinDCX API for active future swaps
API_URL = "https://public.coindcx.com/exchange/ticker"

def fetch_data():
    """Fetch all USDT pair tickers from CoinDCX API."""
    try:
        response = requests.get(API_URL)
        data = response.json()

        if not data:
            print("No data found.")
            return pd.DataFrame()

        # Convert the data to a DataFrame
        df = pd.DataFrame(data)

        # Filter for USDT pairs
        df = df[df["market"].str.endswith("USDT")]

        # Select relevant columns
        df = df[["market", "last_price", "volume"]]
        df.columns = ["Symbol", "Price (USDT)", "Volume"]

        df["Price (USDT)"] = df["Price (USDT)"].astype(float)
        df["Volume"] = df["Volume"].astype(float)

        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def display_data(df):
    """Display the filtered data in a simple format."""
    if not df.empty:
        print(df)
    else:
        print("No data to display.")

def main():
    # Fetch data
    df = fetch_data()

    # Display data
    display_data(df)

if __name__ == "__main__":
    main()
