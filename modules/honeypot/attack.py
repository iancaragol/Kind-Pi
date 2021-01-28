import requests
import urllib.request
import json

class AttackHandler:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_data(self):
        r = requests.get(url=self.endpoint + "/attacks")
        data = r.json()

        return data

    def get_net_stats(self):
        r = requests.get(url=self.endpoint + "/traffic")
        data = r.json()

        return data

    def get_geo_loc(self, ip):
        try:
            with urllib.request.urlopen(f"https://geolocation-db.com/jsonp/{ip}") as url:
                data = url.read().decode()
                data = data.split("(")[1].strip(")")
                data_j = json.loads(data)
                return data_j
        except Exception as e:
            print(e)
            return None