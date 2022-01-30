from datetime import datetime as dt
from PIL import Image, ImageFont, ImageDraw
from paramiko import SSHClient, AutoAddPolicy, SSHException
from scp import SCPClient
from argparse import ArgumentParser
from os import environ, getcwd
from time import sleep
import subprocess

from modules.uta.uta_bus import UtaBusController, UtaBusStop
from modules.reddit.reddit import RedditImageController
from modules.honeypot.attack import AttackHandler
from modules.openweather.weatherhandler import WeatherHandler

class Display:
    def __init__(self, verbose, kindle_addr, kindle_pw, bus_handler, reddit_image_handler, weather_handler, attack_handler, draw_image, draw_weather, draw_bus, draw_attacks, font_file):
        self.verbose = verbose

        # Add new handlers here
        self.bus_handler = bus_handler
        self.reddit_image_handler = reddit_image_handler
        self.weather_handler = weather_handler
        self.attack_handler = attack_handler

        self.kindle_addr = kindle_addr
        self.kindle_pw = kindle_pw

        self.ssh_client = None
        self.scp_client = None
        self.ssh_connect() # Connect to kindle

        # Boolean to enable/disable certain handlers
        self.draw_image = draw_image
        self.draw_weather = draw_weather
        self.draw_bus = draw_bus
        self.draw_attacks = draw_attacks

        self.font_file = font_file


    def ssh_connect(self,):
        """
        Creates an SSH session to the kindle.
        """
        print("[-] Opening ssh connection...")
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh_client.connect(hostname=self.kindle_addr,
                                port=22,
                                username="root",
                                password=self.kindle_pw)
        self.scp_client = SCPClient(self.ssh_client.get_transport())
        print("[-] Succeeded!")

    # region Time
    def add_time(self, draw, font):
        """
        Adds the current time to the top of the image
        """
        now = dt.now()
        current_time = now.strftime("%I:%M").lstrip("0").lstrip("0").replace(" 0", " ")
        draw.text((5, 5), current_time, (0),font=font)
        
        date_str = now.strftime("%a, %b %d")

        date_font = ImageFont.truetype(self.font_file, 42)
        draw.text((10, 80), date_str, (0), font=date_font)

        if self.verbose:
            print("[-] Time added: {}".format(current_time))
    #endregion

    # region Bus
    def add_bus_time(self, draw, font):
        """
        Calls bus_handler to get bus stop times.
        Parses the result and draws it on the image.
        """
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
        """
        Calls honeypot API on Azure
        Parses the result and draws it at the bottom of the image
        """
        try:
            attacks = self.attack_handler.get_data()
            geo_loc = self.attack_handler.get_geo_loc(attacks['last_ip'])
            net_stats = self.attack_handler.get_net_stats()
        except Exception as e:
            # Dirty error handling ;p
            print("[-] An error occurred while getting network and attack data.")
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
    def add_reddit_image(self, img):
        """
        Calls reddit image handler to get a picture from reddit
        Resizes the picture and adds it to the final image
        """
        self.reddit_image_handler.get_image()
        pixel = Image.open('images/pixel_art.png')
        w, h = pixel.size
        w_offset = (600 - w) // 2
        img.paste(pixel, (w_offset, 145))
    # endregion

    # region Weather
    def add_weather(self, draw):
        """
        Calls reddit image handler to get a picture from reddit
        Resizes the picture and adds it to the final image
        """
        aq = self.weather_handler.query_air_quality_api()
        wh = self.weather_handler.query_weather_api()

        # Draw temperature and Air Quality
        loc_font = ImageFont.truetype("courbd.ttf", 24)


        aq_txt = ["", "Good", "Fair", "Moderate", "Poor", "Very Poor"]

        # https://blissair.com/what-is-pm-2-5.htm
        pm2_5_health = "Healthy" # Healthy
        pm2_5 = aq['pm2_5']
        if (pm2_5 >= 35.5): pm2_5_health = "Unhealthy"
        if (pm2_5 >= 55.5): pm2_5_health = "Unhealthy (Limit excersise)"
        if (pm2_5 >= 150.5): pm2_5_health = "Very Unhealthy (Don't go outside!)"
        if (pm2_5 >= 250.5): pm2_5_health = "Hazardous (Death)"
        
        # Formatting looks weird but it works
        # The math makes sure that the spacing is correct no matter the temperature or wind speed
        line1 = "Temperature          Air Quality\n"
        line2 = f"Now: {wh['temp']}" + (" "*(12+(4-len(str(wh['temp']))))) + f"{aq_txt[aq['overall']]} ({aq['overall']})\n"
        line3 = f"Max: {wh['temp_max']}\n"
        line4 = f"Min: {wh['temp_min']}" + (" "*(12+(4-len(str(wh['temp_min']))))) + f"PM2.5: {aq['pm2_5']}\n"
        line5 = (" "*21) + f"PM10: {aq['pm10']}\n"
        line6 = f"Wind" + (" "*17) + f"CO: {aq['co']}\n"
        line7 = f"{wh['wind_speed']} mph" + (" "*(13+(4-len(str(wh['wind_speed']))))) + f"SO2: {aq['so2']}\n"
        line8 = f"\nPM2.5 levels are {pm2_5_health}"

        draw_string = line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8
        draw.text((10, 580), draw_string, (0), font=loc_font)
    # endregion

    def update_image(self):
        """
        Calls add_image functions to construct and crush image.
        Once image is crushed, it is delivered to the kindle for display.
        """
        img = Image.open("images/kindle_display_base.png")
        draw = ImageDraw.Draw(img)
        time_font = ImageFont.truetype(self.font_file, 82)
        
        # Add the image add_image code for each handler here
        if self.draw_image:
            if self.verbose:
                print("[-] Adding reddit image")
            self.add_reddit_image(img)

        if self.draw_weather:
            if self.verbose:
                print("[-] Adding weather")
            self.add_weather(draw)

        if self.draw_bus:
            if self.verbose:
                print("[-] Adding bus times")
            bus_font = ImageFont.truetype(self.font_file, 52)
            self.add_bus_time(draw, bus_font)

        if self.draw_attacks:
            if self.verbose:
                print("[-] Adding attack info")
            attack_font = ImageFont.truetype(self.font_file, 32)
            self.add_attacks(draw, attack_font)

        # Always add time
        if self.verbose:
            print("[-] Adding date time")
        self.add_time(draw, time_font)

        # Convert and crush image so it can be displayed by kindle
        img.convert('L')
        img.save("images/out_pre.png")
        if self.verbose:
            print("[-] Saved pre-crush image")


    def compress_image(self):
        """
        Compresses the image with pngcrush
        """
        cwd = getcwd()
        p = subprocess.Popen("pngcrush {}/images/out_pre.png {}/images/out.png".format(cwd, cwd).split(),
                     stdout=subprocess.PIPE)
        output, _ = p.communicate()

        if self.verbose:
            print("[-] Crushed image")
            print(output)

    def deliver_image(self, filepath):
        """
        Delivers the image to /usr
        """
        try:
            self.scp_client.put(getcwd() + filepath, '/usr')
        except Exception as e:
            print("[-] An error occured while delivering the image. This image will be skipped.")
            print(e)
            if(type(e) is SSHException):
                print("[-] Exception was an ssh exception. Reopening ssh connection!")
                self.ssh_connect()

def main():
    VERBOSE = environ.get("VERBOSE")
    KINDLE_IP = environ.get("KINDLE_IP")
    KINDLE_PW = environ.get("KINDLE_PW")
    WEATHER_LAT = environ.get("WEATHER_LAT")
    WEATHER_LON = environ.get("WEATHER_LON")

    ric = RedditImageController()
    wh = WeatherHandler(lat = WEATHER_LAT, lon = WEATHER_LON) # Cords for Steamboat Springs, CO
    # ath = AttackHandler("http://" + args.ip + ":" + args.port)

    font_file = "courbd.ttf"

    d= Display(verbose=VERBOSE,
               kindle_addr=KINDLE_IP,
               kindle_pw=KINDLE_PW,
               bus_handler=None,
               reddit_image_handler=ric,
               weather_handler=wh,
               attack_handler=None,
               draw_image=True,
               draw_weather=True,
               draw_bus=False,
               draw_attacks=False,
               font_file=font_file)

    while(True):
        print("[-] Starting image update process...")

        d.update_image()
        print("[-] Image updated!")

        d.compress_image()
        print("[-] Image compressed!")
        
        print("[-] Delivering image to kindle...")
        d.deliver_image("/images/out.png")
        print("[-] Image delivered!")

        print("[!] Sleeping....")
        sleep(10)


if __name__ == "__main__":
    main()
