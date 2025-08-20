from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import pandas as pd
import hashlib
import json
import mysql.connector
from time import time

app = Flask(__name__)
CORS(app)

try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Error: model.pkl not found!")

try:
    forecast = pd.read_csv("forecast.csv")
except FileNotFoundError:
    print("Error: forecast.csv not found!")


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(date="Genesis", predicted_price=0, actual_price=0, previous_hash="0")

    def create_block(self, date, predicted_price, actual_price=0, previous_hash=None):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "date": date,
            "predicted_price": predicted_price,
            "actual_price": actual_price,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }
        self.chain.append(block)
        return block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def verify_chain(self):
        for i in range(1, len(self.chain)):
            if self.chain[i]["previous_hash"] != self.hash(self.chain[i - 1]):
                return False
        return True

blockchain = Blockchain()

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="K@v!2006",
    database="agriguard_users"
)
cursor = db.cursor()

@app.route('/today_price', methods=['GET'])
def today_price():
    today = pd.Timestamp.today().normalize()

    # Ensure 'ds' column is in datetime format
    forecast['ds'] = pd.to_datetime(forecast['ds'])

    predicted_price = forecast.loc[forecast['ds'] == today, 'yhat']

    if predicted_price.empty:
        default_price = 1600.0
        blockchain.create_block(date=str(today.date()), predicted_price=default_price)

        # Insert default price into MySQL
        save_price_to_db(today.date(), default_price)

        return jsonify({
            "date": str(today.date()),
            "predicted_price": default_price,
            "note": "No prediction found. Default price used."
        })

    price = round(predicted_price.values[0], 2)
    blockchain.create_block(date=str(today.date()), predicted_price=price)

    # Insert predicted price into MySQL
    save_price_to_db(today.date(), price)

    return jsonify({
        "date": str(today.date()),
        "predicted_price": price
    })

def save_price_to_db(date, price):
    try:
        cursor.execute("""
            INSERT INTO predicted_prices (date, predicted_price)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE predicted_price = VALUES(predicted_price)
        """, (date, price))
        db.commit()
        print(f"✅ Saved predicted price for {date}: ₹{price} into MySQL.")
    except mysql.connector.Error as err:
        print(f"❌ MySQL Error: {err}")

@app.route('/future_prices', methods=['GET'])
def future_prices():
    future_prices = forecast[['ds', 'yhat']].tail(150)
    return jsonify(future_prices.to_dict(orient='records'))

@app.route('/add_price', methods=['POST'])
def add_price():
    data = request.get_json()
    date = data["date"]
    predicted_price = data["predicted_price"]
    actual_price = data.get("actual_price", 0)

    block = blockchain.create_block(date, predicted_price, actual_price)
    return jsonify({"message": "Price added to blockchain!", "block": block}), 201

@app.route("/save_future_prices", methods=["POST"])
def save_future_prices():
    try:
        # Ensure 'ds' column is in datetime format
        forecast['ds'] = pd.to_datetime(forecast['ds'])

        # Loop through forecast and save each future predicted price to MySQL
        for index, row in forecast.iterrows():
            date = row['ds'].date()  # Get just the date part
            predicted_price = round(row['yhat'], 2)

            cursor.execute("""
                INSERT INTO predicted_prices (date, predicted_price)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE predicted_price = VALUES(predicted_price)
            """, (date, predicted_price))

        db.commit()
        print("✅ All future prices saved into MySQL!")
        return jsonify({"message": "All future prices saved successfully!"}), 200

    except Exception as e:
        print("❌ Error saving future prices:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    return jsonify({"chain": blockchain.chain})

@app.route('/verify_blockchain', methods=['GET'])
def verify_blockchain():
    is_valid = blockchain.verify_chain()
    return jsonify({"valid": is_valid})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
