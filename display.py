import time
import requests
import os

from datetime import datetime as dt
from controllers.bus import Bus
from PIL import Image, ImageFont, ImageDraw

class Display:
    def __init__(self, verbose):
        self.bus_controller = Bus([])
        self.verbose = verbose

    def add_time(self, draw, font):
        now = dt.now()
        current_time = now.strftime("%H:%M")
        draw.text((5, 5), current_time, (0),font=font)

        if self.verbose:
            print("Time added: {}".format(current_time))

    def add_bus(self, draw, font):
        return 
  
    def update_image(self):
        img = Image.open("base_image.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 72)

        # Add to image here
        self.add_time(draw, font)

        img.convert('L')
        img.save("out_pre.png")
        if self.verbose:
            print("Saved image")

        cwd = os.getcwd()
        f = os.popen("pngcrush {}/out_pre.png {}/out.png".format(cwd, cwd))
        x = f.read()
        
        if self.verbose:
            print(x)

        

def main():
    d = Display(True)
    # d.add_time()

    while(True):
        d.update_image()
        print("Sleeping for 59 seconds...")
        time.sleep(59.0)


if __name__ == "__main__":
    main()
