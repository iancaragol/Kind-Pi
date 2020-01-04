from controllers.bus import Bus

class Display:
    def __init__(self):
        self.bus_controller = Bus([])

    def serve_dab(self):
        return 'dab.jpg'

    def serve_calender(self):
        if self.bus_controller.update_image():
            return 'bus_times.jpg'
        else:
            return 'error.jpg'

