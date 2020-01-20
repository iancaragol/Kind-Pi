import time
import requests
import os

from datetime import datetime as dt
from PIL import Image, ImageFont, ImageDraw
from controllers.uta_bus import UtaBusController, UtaBusStop
from controllers.reddit import RedditImageController

# python3 -m pyftpdlib -w

class Display:
    def __init__(self, verbose, bus_handler, image_handler):
        self.verbose = verbose
        self.bus_handler = bus_handler
        self.image_handler = image_handler

    def add_time(self, draw, font):
        now = dt.now()
        current_time = now.strftime("%H:%M")
        draw.text((5, 5), current_time, (0),font=font)
        
        date_str = now.strftime("%a, %b %d")

        date_font = ImageFont.truetype("Courier_New_Bold.ttf", 42)
        draw.text((10, 80), date_str, (0), font=date_font)

        if self.verbose:
            print("Time added: {}".format(current_time))

    def add_bus_time(self, draw, font):
        stops = self.bus_handler.get_all_times()
        
        for i in range(len(stops)):
            draw_txt = str(stops[i].name) + " : "
            for j in range(len(stops[i].arrival_times)):
                if j != len(stops[i].arrival_times) - 1:
                    draw_txt += str(stops[i].arrival_times[j]) + ", "
                else:
                    draw_txt += str(stops[i].arrival_times[j])

            draw.text((10, 590+(50*i)), draw_txt, (0),font=font)

    def add_pixel_art(self, img):
        self.image_handler.get_image()
        pixel = Image.open('images/pixel_art.png')
        w, h = pixel.size
        w_offset = (600 - w) // 2
        img.paste(pixel, (w_offset, 145))



    def update_image(self):
        img = Image.open("images/kindle_display_base.png")
        draw = ImageDraw.Draw(img)
        time_font = ImageFont.truetype("Courier_New_Bold.ttf", 82)
        bus_font = ImageFont.truetype("Courier_New_Bold.ttf", 52)
        
        if self.verbose:
            print("Adding pixel art")
        self.add_pixel_art(img)

        if self.verbose:
            print("Adding bus times")
        self.add_bus_time(draw, bus_font)

        # Add to image here
        if self.verbose:
            print("Adding date time")
        self.add_time(draw, time_font)

        img.convert('L')
        img.save("images/out_pre.png")
        if self.verbose:
            print("Saved pre-crush image")

        cwd = os.getcwd()
        f = os.popen("pngcrush {}/images/out_pre.png {}/images/out.png".format(cwd, cwd))
        x = f.read()

        if self.verbose:
            print("Crushed image")
            print(x)


        

def main():
    ubc = UtaBusController()
    ric = RedditImageController()

    # Add our bus stops
    ubs2 = UtaBusStop(198494, "2", "Go to engineering building", 60, "false", "2")
    ubs2.update_scheduled_stop_times(2003, 198494, 24493) # Route id, stop id, stop code
    ubs4 = UtaBusStop(126004, "4", "Go to library", 60, "false", "4")
    ubs4.update_scheduled_stop_times(79372, 126004, 18260)
    ubs455 = UtaBusStop(126004, "455", "Go to library", 60, "false", "455")
    ubs455.update_scheduled_stop_times(19906, 126004, 18260)
    ubc.add_bus_stop(ubs2)
    ubc.add_bus_stop(ubs4)
    ubc.add_bus_stop(ubs455)

    d = Display(True, ubc, ric)

    while(True):
        print("Updating image!")
        d.update_image()
        print("Image updated!")


if __name__ == "__main__":
    main()
