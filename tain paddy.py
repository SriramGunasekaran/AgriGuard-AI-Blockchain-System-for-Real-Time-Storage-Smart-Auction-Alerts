import pandas as pd
from prophet import Prophet
from flask import Flask, jsonify
file_path = r"C:\Users\kaviy\Downloads\thanjavur.csv"  
df = pd.read_csv(file_path, skiprows=1)
df.columns = df.columns.str.strip()
df['ds'] = pd.to_datetime(df['ds'], format="%d-%b-%y", errors='coerce')
df['y'] = pd.to_numeric(df['y'], errors='coerce')
df = df.dropna(subset=['ds', 'y'])
df = df.groupby('ds', as_index=False)['y'].mean()
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=70, freq='D')
forecast = model.predict(future)
app = Flask(__name__)

@app.route('/today_price', methods=['GET'])
def today_price():
    today = pd.Timestamp.today().normalize()  # Current date with time set to 00:00:00
    
    # Fetch today's real price from the original dataset (the one you used to train the model)
    real_price = df.loc[df['ds'] == today, 'y']
    
    if not real_price.empty:
        return jsonify({"date": str(today.date()), "real_price": round(real_price.values[0], 2)})
    else:
        return jsonify({"error": "No real price available for today"}), 404


@app.route('/future_prices', methods=['GET'])
def future_prices():
    return jsonify(forecast[['ds', 'yhat']].to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

