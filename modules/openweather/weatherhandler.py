import requests
import os
from datetime import datetime as dt
from PIL import Image

class WeatherHandler:
    # https://api.nasa.gov/
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.api_key = ""
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, "apikey.txt")) as ak:
            self.api_key = ak.readline()
        self.air_quality_uri = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}"
        self.weather_uri =  "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=imperial"

    def query_air_quality_api(self):
        # https://openweathermap.org/api/air-pollution
        response = requests.get(self.air_quality_uri.format(self.lat, self.lon, self.api_key))
        data = response.json()["list"][0]
        aq = {
            "overall" : data["main"]["aqi"],
            "co" : data["components"]["co"],
            "no" : data["components"]["no"],
            "no2" : data["components"]["no2"],
            "o3" : data["components"]["o3"],
            "so2" : data["components"]["so2"],
            "pm2_5" : data["components"]["pm2_5"],
            "pm10" : data["components"]["pm10"],
            "nh3" : data["components"]["nh3"],
        }

        return aq

    
    def query_weather_api(self):
        # https://openweathermap.org/api/air-pollution
        response = requests.get(self.weather_uri.format(self.lat, self.lon, self.api_key))
        data = response.json()
        we = {
            "temp" : data["main"]["temp"],
            "temp_max" : data["main"]["temp_max"],
            "temp_min" : data["main"]["temp_min"],
            "wind_speed" : data["wind"]["speed"],
            "description" : data["weather"][0]["main"],
        }

        return we

# Use this for debugging
if __name__ == "__main__":
    wh = WeatherHandler(lat = "40.4849769", lon = "-106.8317158")
    wh.query_air_quality_api()
    wh.query_weather_api()
