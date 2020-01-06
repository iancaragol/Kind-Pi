import requests
import json
import datetime

class Bus:
  def __init__(self, bus_id, predicted, arrival):
    self.bus_id = bus_id
    self.predicted = predicted
    self.arrival = arrival

class BusHandler:

    def __init__(self):
        self.bus_dict = {}

    def http_call(self):
        url = 'http://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/1_18270.json?key=TEST'
        response = requests.get(url)
        data = response.json()
        num_of_buses = len(data['data']['entry']['arrivalsAndDepartures'])
        data = data['data']['entry']['arrivalsAndDepartures']

        return data, num_of_buses

    def parse_json(self, input_data, counter):
        time_type = str(input_data[counter]['predicted'])

        if time_type == 'False':
            time_type = False
            arrival = input_data[counter]['scheduledArrivalTime']
        else:
            time_type = True
            arrival = input_data[counter]['predictedArrivalTime']

        return time_type, arrival

    def time_away(self, input_variable, current_time):
        minutes_away = input_variable - current_time
        minutes_away = round(minutes_away.total_seconds() / 60)

        return minutes_away
    
    def update_buses(self):
        current_time = datetime.datetime.now()
        data, num_of_buses = self.http_call()
        
        for i in range(num_of_buses):
            time_type, arrival = self.parse_json(data, i)
            arrival = datetime.datetime.fromtimestamp(arrival/1000)
            arrival = self.time_away(arrival, current_time)
            if arrival <= 0:
                arrival = 0
            temp_bus = Bus(i, time_type, arrival)
            self.bus_dict[i] = temp_bus

            #print('OneBusAway - Predicted:', self.bus_dict[i].predicted, '| Arrival:', str(self.bus_dict[i].arrival) + ' minutes')

            return self.bus_dict
        
if __name__ == "__main__":
    bh = BusHandler()
    bus_dict_out = bh.update_buses()

