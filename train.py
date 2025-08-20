import pandas as pd
from prophet import Prophet
import pickle
file_path = r"C:\Users\kaviy\Downloads\thanjavur.csv"
df = pd.read_csv(file_path, skiprows=1)
df.columns = df.columns.str.strip()
df['ds'] = pd.to_datetime(df['ds'], format="%d-%b-%y", errors='coerce')
df['y'] = pd.to_numeric(df['y'], errors='coerce')
df = df.dropna(subset=['ds', 'y'])
df = df.groupby('ds', as_index=False)['y'].mean()
model = Prophet()
model.fit(df)
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
print("✅ Model saved as 'model.pkl'")
future = model.make_future_dataframe(periods=70, freq='D')
forecast = model.predict(future)
forecast.to_csv("forecast.csv", index=False)
print("✅ Forecast saved as 'forecast.csv'")
