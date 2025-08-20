from flask import Flask, jsonify
import pandas as pd
import requests
import schedule
import time
import threading

app = Flask(__name__)

# Global variable to store paddy prices
paddy_prices = []

def fetch_paddy_prices():
    global paddy_prices
    url = "YOUR_SOURCE_URL"  # Replace with your actual data source URL
    tables = pd.read_html(url)  # Scrape data
    paddy_prices = tables[0].to_dict(orient="records")
    print("Updated paddy prices!")

# Schedule the function to run every 24 hours
schedule.every().day.at("06:00").do(fetch_paddy_prices)

# Run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler, daemon=True).start()

@app.route('/api/paddy-prices', methods=['GET'])
def get_paddy_prices():
    return jsonify(paddy_prices)

if __name__ == '__main__':
    fetch_paddy_prices()  # Fetch data when the server starts
    app.run(debug=True)
