from datetime import datetime as dt
import time
import optimage
import requests

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
        img.save("dab-gray-crushed-edit.png")

        img = Image.open('dab-gray-crushed-edit.png').convert('LA')
        img.save('out.png')

def main():
    d = Display()

    while(True):
        time.sleep(60.0)
        d.add_time()


if __name__ == "__main__":
    main()