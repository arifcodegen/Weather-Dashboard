from flask import Flask, render_template, request
import requests
from datetime import datetime  # Import datetime to get the current date and time

# app = Flask(__name__)
app = Flask(__name__)
# Your OpenWeatherMap API key
api_key = 'd38ebe8bc4fa6d4bbbdb7cf6256c6541'  # Replace with your actual OpenWeatherMap API key


def get_coordinates(city_name, api_key):
    """Fetch latitude and longitude for a given city name."""
    # Create the API URL with the city name
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"

    # Send a request to the OpenWeatherMap API
    response = requests.get(url)
    data = response.json()  # Parse the response JSON

    # Check if the request was successful
    if response.status_code == 200:
        # Extract latitude and longitude
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        return lat, lon
    else:
        print(f"Error fetching coordinates: {data['message']}")
        return None, None


def get_current_location():
    response = requests.get('https://ipinfo.io/json')
    data = response.json()
    return data


def get_weather(lat, lon):
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    response = requests.get(weather_url)
    weather_data = response.json()
    return weather_data


def get_forecast(lat, lon):
    forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    response = requests.get(forecast_url)
    forecast_data = response.json()
    return forecast_data


@app.route('/')
def index():
    # Get the current location data
    location_data = get_current_location()
    lat, lon = location_data['loc'].split(',')

    # Get the current weather data
    current_weather_data = get_weather(lat, lon)
    current_location = {
        "city": location_data['city'],
        "region": location_data.get('region', 'N/A'),
        "latitude": lat,  # Include latitude in the data passed to the template
        "longitude": lon,  # Include longitude in the data passed to the template
        "temperature": current_weather_data['main']['temp'],
        "weather": current_weather_data['weather'][0]['description'],
        "humidity": current_weather_data['main']['humidity'],
        "wind_speed": current_weather_data['wind']['speed']
    }

    # Get the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the date and time

    # Get the 5-day forecast for the current location
    forecast_data = get_forecast(lat, lon)
    daily_forecast = {}

    for entry in forecast_data['list']:
        date_time = entry['dt_txt']
        date = date_time.split(' ')[0]

        if date not in daily_forecast:
            daily_forecast[date] = {
                'temperature': entry['main']['temp'],
                'humidity': entry['main']['humidity'],
                'wind_speed': entry['wind']['speed'],
                'weather': entry['weather'][0]['description'],
            }

    return render_template('index.html', current_location=current_location,
                           daily_forecast=daily_forecast, current_datetime=current_datetime)


@app.route('/weather', methods=['POST'])
def weather():
    city_name = request.form.get('city_name')

    # Use the get_coordinates function to fetch latitude and longitude for the entered city
    lat, lon = get_coordinates(city_name, api_key)

    # Check if valid coordinates were returned
    if lat is not None and lon is not None:
        weather_data = get_weather(lat, lon)

        # Get the 5-day forecast for the selected city
        city_forecast_data = get_forecast(lat, lon)
        city_daily_forecast = {}
        for entry in city_forecast_data['list']:
            date_time = entry['dt_txt']
            date = date_time.split(' ')[0]

            if date not in city_daily_forecast:
                city_daily_forecast[date] = {
                    'temperature': entry['main']['temp'],
                    'humidity': entry['main']['humidity'],
                    'wind_speed': entry['wind']['speed'],
                    'weather': entry['weather'][0]['description'],
                }

        return render_template('weather.html', weather_data=weather_data, city_name=city_name,
                               city_daily_forecast=city_daily_forecast, latitude=lat, longitude=lon)

    else:
        error = "City not found. Please check the city name."
        return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
