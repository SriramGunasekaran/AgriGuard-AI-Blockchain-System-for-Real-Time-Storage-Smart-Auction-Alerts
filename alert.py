from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import smtplib
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="K@v!2006",      
    database="agriguard_users" 
)
cursor = db.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_accounts (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
""")
db.commit()

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    try:
        cursor.execute("INSERT INTO user_accounts (email, password) VALUES (%s, %s)", (email, password))
        db.commit()
        print(f"Signup success for {email}")
        return jsonify({"message": "Signup successful!"})
    except mysql.connector.errors.IntegrityError:
        print(f"Signup failed: {email} already exists")
        return jsonify({"message": "Email already exists!"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not email or not password:
        return jsonify({"message": "Email and password required."}), 400

    print(f"Attempting login for {email}")
    cursor.execute("SELECT * FROM user_accounts WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()

    if not user:
        print("Login failed: invalid credentials")
        return jsonify({"message": "Invalid credentials"}), 401

    print("Login success!")
    if latitude and longitude:
        try:
            weather_api_key = "e55e416d6dd81eb9b2ae25af71edac1f"
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}&units=metric"
            )
            weather_data = response.json()

            temperature = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            print(f"Weather data — Temp: {temperature}°C, Humidity: {humidity}%")

            email_sent = False
            if temperature > 50 or humidity > 100:
                send_email(email, temperature, humidity)
                email_sent = True
                print("Weather alert email sent.")
            else:
                print("No alert needed based on weather.")

            return jsonify({
                "message": "Login successful!",
                "redirect": "/dashboard.html",
                "email_sent": email_sent,
                "temperature": temperature,
                "humidity": humidity
            })
        except Exception as e:
            print("Weather API error:", str(e))
            return jsonify({"message": "Weather API error"}), 500
    else:
        print("Login success without location")
        return jsonify({"message": "Login successful, but no location data received.", "redirect": "/dashboard.html"})

def send_email(to_email, temperature, humidity):
    sender_email = "akaviyaa03@gmail.com"
    sender_password = "buwu nwgu nmjl xsrl"  # (your Gmail App Password)

    subject = "Weather Alert!"
    body = f"🚨 Alert: High temperature ({temperature}°C) or humidity ({humidity}%) detected!"
    email_message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, email_message)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print("Error sending email:", str(e))

if __name__ == "__main__":
    app.run(debug=True)
