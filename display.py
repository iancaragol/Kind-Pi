from datetime import datetime as dt
from PIL import Image, ImageFont, ImageDraw
from paramiko import SSHClient, AutoAddPolicy, SSHException
from scp import SCPClient
from argparse import ArgumentParser
from os import getcwd, popen
from time import sleep

from modules.uta.uta_bus import UtaBusController, UtaBusStop
from modules.reddit.reddit import RedditImageController
from modules.honeypot.attack import AttackHandler

class Display:
    def __init__(self, verbose, kindle_addr, kindle_pw, bus_handler, image_handler, attack_handler, draw_image, draw_bus, draw_attacks, font_file):
        self.verbose = verbose
        self.bus_handler = bus_handler
        self.image_handler = image_handler
        self.attack_handler = attack_handler

        self.kindle_addr = kindle_addr
        self.kindle_pw = kindle_pw

        self.ssh_client = None
        self.scp_client = None
        self.ssh_connect() # Connect to kindle

        self.draw_image = draw_image
        self.draw_bus = draw_bus
        self.draw_attacks = draw_attacks

        self.font_file = font_file


    def ssh_connect(self,):
        print("Opening ssh connection...")
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh_client.connect(hostname=self.kindle_addr,
                                port=22,
                                username="root",
                                password=self.kindle_pw)
        self.scp_client = SCPClient(self.ssh_client.get_transport())
        print("Succeeded!")

    # region Time
    def add_time(self, draw, font):
        now = dt.now()
        current_time = now.strftime("%H:%M")
        draw.text((5, 5), current_time, (0),font=font)
        
        date_str = now.strftime("%a, %b %d")

        date_font = ImageFont.truetype(self.font_file, 42)
        draw.text((10, 80), date_str, (0), font=date_font)

        if self.verbose:
            print("Time added: {}".format(current_time))
    #endregion

    # region Bus
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
    #endregion

    # region Honeypot
    def add_attacks(self, draw, font):
        try:
            attacks = self.attack_handler.get_data()
            geo_loc = self.attack_handler.get_geo_loc(attacks['last_ip'])
            net_stats = self.attack_handler.get_net_stats()
        except Exception as e:
            # Dirty error handling ;p
            print("An error occurred while getting network and attack data.")
            print(e)

            template = "Exception: {0}"
            message = template.format(type(e).__name__)

            error_font = ImageFont.truetype("Courier_New_Bold.ttf", 24)
            draw.text((10, 580), message, (0), font=error_font)
            return
            

        draw_txt = attacks['last_ip']

        if geo_loc != None:
            if geo_loc['city'] != None:
                draw_txt += f": {geo_loc['city']}"
            if geo_loc['country_code'] != None:
                if len(geo_loc['country_name']) > 12:
                    draw_txt += f", {geo_loc['country_code']}"
                else:
                    draw_txt += f", {geo_loc['country_name']}"

        loc_font = ImageFont.truetype("Courier_New_Bold.ttf", 24)
        draw.text((10, 580), draw_txt, (0), font=loc_font)

        sorted_users = sorted(attacks['users'].items(), key=lambda x:x[1], reverse=True)
        user_font = ImageFont.truetype("Courier_New_Bold.ttf", 24)
        draw_txt = f"{attacks['last_user']}*"
        draw.text((10, 610), draw_txt, (0), font=user_font)

        for i in range(0, len(sorted_users)):
            if i > 6:
                break
            draw_txt = f"{sorted_users[i][0]}: {sorted_users[i][1]}"
            draw.text((10, 640+(30*i)), draw_txt, (0), font=user_font)
        
        # Draw network stats
        draw_txt = "rx_d: " + net_stats['rx_d']
        draw.text((310, 610+(30*0)), draw_txt, (0), font=user_font)
        draw_txt = "tx_d: " + net_stats['tx_d']
        draw.text((310, 610+(30*1)), draw_txt, (0), font=user_font)
        # Leave a space
        draw_txt = "rx_m: " + net_stats['rx_m']
        draw.text((310, 610+(30*3)), draw_txt, (0), font=user_font)
        draw_txt = "tx_m: " + net_stats['tx_m']
        draw.text((310, 610+(30*4)), draw_txt, (0), font=user_font)
    # endregion

    # region Reddit
    def add_pixel_art(self, img):
        self.image_handler.get_image()
        pixel = Image.open('images/pixel_art.png')
        w, h = pixel.size
        w_offset = (600 - w) // 2
        img.paste(pixel, (w_offset, 145))
    # endregion

    def update_image(self):
        img = Image.open("images/kindle_display_base.png")
        draw = ImageDraw.Draw(img)
        time_font = ImageFont.truetype(self.font_file, 82)
        bus_font = ImageFont.truetype(self.font_file, 52)
        attack_font = ImageFont.truetype(self.font_file, 32)
        
        if self.draw_image:
            if self.verbose:
                print("Adding pixel art")
            self.add_pixel_art(img)

        if self.draw_bus:
            if self.verbose:
                print("Adding bus times")
            self.add_bus_time(draw, bus_font)

        if self.draw_attacks:
            if self.verbose:
                print("Adding attack info")
            self.add_attacks(draw, attack_font)

        # Add to image here
        if self.verbose:
            print("Adding date time")
        self.add_time(draw, time_font)

        img.convert('L')
        img.save("images/out_pre.png")
        if self.verbose:
            print("Saved pre-crush image")

        cwd = getcwd()
        f = popen("pngcrush {}/images/out_pre.png {}/images/out.png".format(cwd, cwd))
        x = f.read()

        if self.verbose:
            print("Crushed image")
            print(x)
        print("Delivering image to kindle...")
        self.deliver_image("/images/out.png")
        print("Image delivered!")

    def deliver_image(self, filepath):
        try:
            self.scp_client.put(getcwd() + filepath, '/usr')
        except Exception as e:
            print("An error occured while delivering the image. This image will be skipped.")
            print(e)
            if(type(e) is SSHException):
                print("Exception was an ssh exception. Reopening ssh connection!")
                self.ssh_connect()

def main():
    parser = ArgumentParser()
    parser.add_argument('--ip', required=True) # IP of VM
    parser.add_argument('--port', required=True) # Port of flask app
    parser.add_argument('--kip', required=True) # Kindle IP
    parser.add_argument('--pw', required=True) # Kindle root PW

    args = parser.parse_args()

    ric = RedditImageController()
    ath = AttackHandler("http://" + args.ip + ":" + args.port)

    kindle_addr = args.kip
    kindle_pw = args.pw

    d = Display(True, kindle_addr, kindle_pw, None, ric, ath, True, None, False, "courbd.ttf")

    while(True):
        print("Updating image!")
        d.update_image()
        print("Image updated!")

        if(not d.draw_bus): # If we done have to draw the bus then there is some extra time between image updates
            print("Sleeping for 3 seconds...")
            sleep(3)


if __name__ == "__main__":
    main()
