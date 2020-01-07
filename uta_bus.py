import requests
import datetime
import json

from bs4 import BeautifulSoup

class UtaBusStop:
    def __init__(self, stop_id, name, description, minutes_out, onward_calls, filter_route):
        # http://developer.rideuta.com/StopMonitoringInstructions.aspx
        self.stop_id = stop_id
        self.name = name
        self.description = description
        self.minutes_out = minutes_out # The number of minutes away from the stop you want to query. Any vehicle that is this many minutes or less from the stop will be returned. (e.g 30 for 30 minutes or less away)
        self.onward_calls = onward_calls #Determines whether or not the response will include the stops (known as "calls" in SIRI) each vehicle is going to make. To get calls data, use value true, otherwise use value false.
        self.filter_route = filter_route # Filters the vehicles by a a desired route. This is an optional value if the parameter is left blank all vehicles headed to the queried stop will be included. (e.g. 2 to filter for vehicles servicing route 2)
        self.estimated_times = []

class UtaBusHandler:
    def __init__(self):
        self.bus_stops = {}
        self.token = 'UUBGOBXBKB3'
        self.url = "http://api.rideuta.com/SIRI/SIRI.svc/StopMonitor?stopid={}&minutesout={}&onwardcalls={}&filterroute={}&usertoken={}"

    def make_request(self, bus_stop):
        request_url = self.url.format(bus_stop.stop_id, bus_stop.minutes_out, bus_stop.onward_calls, bus_stop.filter_route, self.token)
        response = requests.get(request_url)

        return response.content
    
    def parse_response_content(self, content):
        soup = BeautifulSoup(content, "html.parser")

        estimated_times = []
        for t in soup.findAll("estimateddeparturetime"):
            estimated_times.append(int(t.text)//60)

        return estimated_times

    def get_estimated_times(self, bus_stop):
        content = self.make_request(bus_stop)
        times = self.parse_response_content(content)

        bus_stop.estimated_times = times

        return bus_stop

    def get_all_estimated_times(self):
        stops = []
        for bs in self.bus_stops.values():
            temp_bs = self.get_estimated_times(bs)
            self.bus_stops[temp_bs.stop_id] = temp_bs
            stops.append(temp_bs)

        return stops

    def add_bus_stop(self, bus_stop):
        self.bus_stops[bus_stop.stop_id] = bus_stop

    