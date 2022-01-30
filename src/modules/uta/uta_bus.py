import requests
import json
import pandas as pd
import os

from datetime import datetime
from bs4 import BeautifulSoup

class UtaBusStop:
    def __init__(self, stop_id, name, description, minutes_out, onward_calls, filter_route):
        # http://developer.rideuta.com/StopMonitoringInstructions.aspx
        # static transit: https://developers.google.com/transit/gtfs/reference?csw=1
        # http://transitfeeds.com/p/utah-transportation-authority/59
        self.stop_id = stop_id
        self.name = name
        self.description = description
        self.minutes_out = minutes_out # The number of minutes away from the stop you want to query. Any vehicle that is this many minutes or less from the stop will be returned. (e.g 30 for 30 minutes or less away)
        self.onward_calls = onward_calls #Determines whether or not the response will include the stops (known as "calls" in SIRI) each vehicle is going to make. To get calls data, use value true, otherwise use value false.
        self.filter_route = filter_route # Filters the vehicles by a a desired route. This is an optional value if the parameter is left blank all vehicles headed to the queried stop will be included. (e.g. 2 to filter for vehicles servicing route 2)
        self.estimated_times = []
        self.scheduled_times = {}
        self.arrival_times = []

    def update_scheduled_stop_times(self, gtfs_route_id, gtfs_stop_code, gtfs_stop_id):
        # 2003,,2,200 SOUTH,,3,https://www.rideuta.com/Rider-Tools/Schedules-and-Maps/2-200-South,2eb566,FFFFFF
        service_ids = [4, 3, 2] # Hardcoded for UTA

        print("[-] Parsing gtfs files...")

        for s_id in service_ids:
            trip_df = pd.read_csv(os.getcwd() + "/controllers/gtfs/trips.txt")
            trips = trip_df.loc[trip_df['route_id'] == gtfs_route_id]
            trips = trips.loc[trips['service_id'] == s_id]

            stop_times_df = pd.read_csv(os.getcwd() + "/controllers/gtfs/stop_times.txt")
            stops = stop_times_df.loc[stop_times_df['stop_id'] == gtfs_stop_id]

            times = stops.loc[stops['trip_id'].isin(trips['trip_id'])]

            # times.drop_duplicates(keep=False,inplace=True)

            str_times = times['arrival_time'].values.tolist()

            self.scheduled_times[s_id] = str_times

        print("[-] Complete!")

class UtaBusController:
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
            arrive_time = int(t.text)//60
            
            if arrive_time < 0:
                arrive_time = 0

            estimated_times.append(arrive_time)

        return estimated_times

    def update_estimated_times(self, bus_stop):
        try: #UTA API is iconsistent
            content = self.make_request(bus_stop)
            times = self.parse_response_content(content)
            bus_stop.estimated_times = times


        except:
            bus_stop.estimated_times = []

        print("[-] Stop: " + str(bus_stop.stop_id) + " , times: " + str(times))

        return bus_stop

    def update_scheduled_times(self, bus_stop):
        FMT = "%H:%M:%S"
        now = datetime.now()
        now = datetime.strptime(now.strftime(FMT), FMT)
        time_differences = []

        calendar_id = datetime.today().weekday()
        service_id = 4
        if calendar_id == 5: # Saturday
            service_id = 2
        
        if calendar_id == 6: # Sunday
            service_id = 3

        for t in bus_stop.scheduled_times[service_id]:
            time = t.strip().replace(' ', '')

            if time.startswith('24'): # Extra case to 24:26:57 format from GTFS
                temp_time = list(time)
                temp_time[0] = '0'
                temp_time[1] = '0'
                time = "".join(temp_time)

            arrive = datetime.strptime(time, FMT)
            t_delta = now - arrive
            t_delta = int(t_delta.total_seconds() // 60)
            if t_delta >= 0 and t_delta <= bus_stop.minutes_out:
                time_differences.append(t_delta)

        time_differences.sort()
        bus_stop.arrival_times = time_differences

        return bus_stop

    def get_all_times(self):
        stops = []
        for bs in self.bus_stops.values():
            # Estimated times
            # temp_bs = self.update_estimated_times(bs)
            temp_bs = self.update_scheduled_times(bs)

            temp_est_times = temp_bs.estimated_times

            # Add parenthesis so we can tell if the time is from the API
            formatted_est_times = []
            for t in temp_est_times:
                formatted_est_times.append('('+str(t)+')')

            temp_bs.estimated_times = formatted_est_times
            self.bus_stops[temp_bs.name] = temp_bs
            stops.append(temp_bs)

        return stops

    def add_bus_stop(self, bus_stop):
        self.bus_stops[bus_stop.name] = bus_stop



    