#!/usr/bin/env python3
"""
Debug Finnhub API connection
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_finnhub_direct():
    api_key = os.getenv('FINNHUB_API_KEY')
    print(f"API Key: {api_key}")
    
    # Test basic quote
    url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={api_key}"
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Quote data: {data}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test metrics endpoint with different symbols
    test_symbols = ['AAPL', 'PLTR', 'SOFI', 'AMC', 'GME']
    
    for symbol in test_symbols:
        print(f"\n{'='*50}")
        print(f"Testing metrics for {symbol}...")
        
        url2 = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={api_key}"
        
        try:
            response2 = requests.get(url2, timeout=10)
            print(f"Status Code: {response2.status_code}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"Has metric key: {'metric' in data2}")
                if 'metric' in data2:
                    metric = data2['metric']
                    print(f"Shares Outstanding: {metric.get('sharesOutstanding')}")
                    print(f"Float Shares: {metric.get('floatShares')}")
                    print(f"Market Cap: {metric.get('marketCapitalization')}")
                    print(f"Available keys: {list(metric.keys())[:10]}...")  # First 10 keys
                else:
                    print(f"No metric data: {data2}")
            else:
                print(f"Error response: {response2.text}")
                
        except Exception as e:
            print(f"Error: {e}")
            
        # Small delay between calls
        import time
        time.sleep(1)

if __name__ == "__main__":
    test_finnhub_direct()