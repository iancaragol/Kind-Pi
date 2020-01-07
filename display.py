import time
import requests
import os

from datetime import datetime as dt
from controllers.bus import Bus
from PIL import Image, ImageFont, ImageDraw
from uta_bus import UtaBusHandler, UtaBusStop

class Display:
    def __init__(self, verbose, bus_handler):
        self.verbose = verbose
        self.bus_handler = bus_handler

    def add_time(self, draw, font):
        now = dt.now()
        current_time = now.strftime("%H:%M")
        draw.text((5, 5), current_time, (0),font=font)

        if self.verbose:
            print("Time added: {}".format(current_time))

    def add_bus_time(self, draw, font):
        stops = self.bus_handler.get_all_estimated_times()
        
        for i in range(len(stops)):
            draw_txt = str(stops[i].name) + " : "
            for j in range(len(stops[i].estimated_times)):
                if j != len(stops[i].estimated_times) - 1:
                    draw_txt += str(stops[i].estimated_times[j]) + ", "
                else:
                    draw_txt += str(stops[i].estimated_times[j])

            draw.text((10, 610+(50*i)), draw_txt, (0),font=font)

  
    def update_image(self):
        img = Image.open("images/base_image.png")
        draw = ImageDraw.Draw(img)
        time_font = ImageFont.truetype("arial.ttf", 72)
        bus_font = ImageFont.truetype("arial.ttf", 52)
        

        # Add to image here
        self.add_time(draw, time_font)
        self.add_bus_time(draw, bus_font)

        img.convert('L')
        img.save("images/out_pre.png")
        if self.verbose:
            print("Saved image")

        time.sleep(5.0)

        cwd = os.getcwd()
        f = os.popen("pngcrush {}/images/out_pre.png {}/images/out.png".format(cwd, cwd))
        x = f.read()
        
        if self.verbose:
            print(x)

        

def main():
    # Add our bus stops
    ubh = UtaBusHandler()
    ubs2 = UtaBusStop(198494, "2", "Go to engineering building", 120, "false", "2")
    ubs4 = UtaBusStop(126004, "4/455", "Go to library", 120, "false", "")

    ubh.add_bus_stop(ubs2)
    ubh.add_bus_stop(ubs4)

    d = Display(True, ubh)

    while(True):
        d.update_image()
        print("Sleeping for 53 seconds...")
        time.sleep(53.0)


if __name__ == "__main__":
    main()
