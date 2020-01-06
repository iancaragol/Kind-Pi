from onebusaway import BusHandler, Bus
import time
import optimage
from PIL import Image, ImageFont, ImageDraw


def add_time(bus_dict_input):
        img = Image.open("dab.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 52)

        arrival_time = 'Next Bus: ' + str(bus_dict_input[0].arrival) + ' minutes'
        draw.text((50, 50), arrival_time, (0), font=font)
        img.convert('L')
        img.save("out.png")


def main():
    bh = BusHandler()
    bus_dict_out = bh.update_buses()
    print(bus_dict_out[0].arrival)
    add_time(bus_dict_out)

if __name__ == "__main__":
    main()

