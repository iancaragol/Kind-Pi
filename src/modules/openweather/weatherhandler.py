import requests
from os import environ
from datetime import datetime

class WeatherHandler:
    # https://api.nasa.gov/
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.api_key = environ.get("OPENWEATHER_API_KEY")
        self.air_quality_uri = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}"
        self.weather_uri =  "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=imperial"

    def query_air_quality_api(self):
        # https://openweathermap.org/api/air-pollution
        headers = {
            'Content-type': 'application/json',
        }

        request_uri = self.air_quality_uri.format(self.lat, self.lon, self.api_key)
        aq = {
                "overall" : "Default",
                "co" : 0,
                "no" : 0,
                "no2" : 0,
                "o3" : 0,
                "so2" : 0,
                "pm2_5" : 0,
                "pm10" : 0,
                "nh3" : 0,
        }

        try:
            response = requests.get(request_uri, headers=headers)
            #print(request_uri)
            #print(response)
            data = response.json()["list"][0]
            aq["overall"] = data["main"]["aqi"]
            aq["co"] = data["components"]["co"]
            aq["no"] = data["components"]["no"]
            aq["no2"] = data["components"]["no2"]
            aq["o3"] = data["components"]["o3"]
            aq["so2"] = data["components"]["so2"]
            aq["pm2_5"] = data["components"]["pm2_5"]
            aq["pm10"] = data["components"]["pm10"]
            aq["nh3"] = data["components"]["nh3"]

        except Exception as e:
            print("[-] An exception occurred in query_air_quality_api")
            print("[-] Returning default values.")
            print(e)

        return aq

    
    def query_weather_api(self):
        # https://openweathermap.org/api/air-pollution
        headers = {
            'Content-type': 'application/json',
        }

        request_uri = self.weather_uri.format(self.lat, self.lon, self.api_key)
        we = {
            "temp" : 0,
            "temp_max" : 0,
            "temp_min" : 0,
            "wind_speed" : 0,
            "description" : 0
        }

        try:
            response = requests.get(request_uri, headers=headers)
            #print(request_uri)
            #print(response)

            data = response.json()
            we["temp"] = round(data["main"]["temp"], 2)
            we["temp_max"] = round(data["main"]["temp_max"], 2)
            we["temp_min"] = round(data["main"]["temp_min"], 2)
            we["wind_speed"] = round(data["wind"]["speed"], 2)
            we["description"] = data["weather"][0]["main"]
                    
        except Exception as e:
            print("[-] An exception occurred in query_air_quality_api")
            print("[-] Returning default values.")
            print(e)

        return we

# Use this for debugging
if __name__ == "__main__":
    wh = WeatherHandler(lat = "40.4849769", lon = "-106.8317158")
    wh.query_air_quality_api()
    wh.query_weather_api()
