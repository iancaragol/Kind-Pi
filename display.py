from datetime import datetime as dt
import time
import requests
import os

from controllers.bus import Bus
from PIL import Image, ImageFont, ImageDraw

class Display:
    def __init__(self):
        self.bus_controller = Bus([])

    def add_time(self):
        img = Image.open("dab-gray-crushed.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 72)

        now = dt.now()
        current_time = now.strftime("%H:%M")
        draw.text((5, 5), current_time, (0),font=font)
        img.convert('L')
        img.save("out.png")
        print("Saved image")

        # os.remove("out_crush.png")
        # print("Deleted old out_crush.png")

        f = os.popen("sudo pngcrush out.png out_crush.png")
        x = f.read()
        print(x)
        #optimage._pngcrush("out.png", "out_crush.png")
        print("Crushed image")	

        

def main():
    d = Display()
    # d.add_time()

    while(True):
        d.add_time()
        print("Sleeping for 59 seconds...")
        time.sleep(59.0)


if __name__ == "__main__":
    main()
