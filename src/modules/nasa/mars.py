import requests
import os
from datetime import datetime as dt
from PIL import Image

class MarsRover:
    # https://api.nasa.gov/
    def __init__(self, rover, img_filename):
        self.api_key = ""
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, "apikey.txt")) as ak:
            self.api_key = ak.readline()
        self.rover = rover
        self.photos_uri = "https://api.nasa.gov/mars-photos/api/v1/rovers/{}/photos?sol={}&api_key={}"
        self.manifest_uri = "https://api.nasa.gov/mars-photos/api/v1/manifests/{}/?api_key={}"
        self.img_filename = img_filename

    def query_api(self):
        manifest = self.get_mission_mainifest()
        sol = 0 # Default to first day of mission

        if (manifest):
            sol = int(manifest["photo_manifest"]["max_sol"])

        response = requests.get(self.photos_uri.format(self.rover, sol, self.api_key))
        img_url = response.json()["photos"][0]["img_src"]
        self.download_image(img_url)

    def download_image(self, image_url):
        try:
            print("[-] Downloading image from Nasa...")
            response = requests.get(image_url)

            if response.status_code == 200:
                print('Downloading %s...' % (self.img_filename))

            with open(self.img_filename, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)

            self.crop_image_and_save()
            
        except Exception as e:
            print("[-] An exception occurred while downloading...")
            print(e)

    def crop_image_and_save(self):
        basewidth = 550
        im = Image.open(self.img_filename)
        wpercent = (basewidth/float(im.size[0]))
        hsize = int((float(im.size[1])*float(wpercent)))
        im = im.resize((basewidth,hsize), Image.ANTIALIAS)

        w, h = im.size
        h_const = 400
        w_const = 575
        h_offset = 0
        w_offset = 0

        if h >= h_const:
            h_offset = (h - h_const)//2
        
        if w >= w_const:
            w_offset = (w - w_const)//2

        im = im.crop((w_offset, h_offset, w-w_offset, h-h_offset))
        im.save(self.img_filename)

    def get_mission_mainifest(self):
        response = requests.get(self.manifest_uri.format(self.rover, self.api_key))

        if (response.status_code == 200):
            print(f"Got manifest for {self.rover}")
            return response.json()
        else:
            print(f"Got status code: {response.status_code} from {self.manifest_uri.format(self.rover)}")
            print("[-] Returning none.")
            return None



if __name__ == "__main__":
    mr = MarsRover("Curiosity", "images/curiosity.jpg")
    mr.query_api()