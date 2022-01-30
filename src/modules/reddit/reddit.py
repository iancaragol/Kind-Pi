import praw
import requests
import os
from PIL import Image

class RedditImageController:
    def __init__(self):
        self.last_image_url = ""
        self.image_changed = True
        self.subreddit = os.environ.get("IMG_SUBREDDIT")
        self.image_filepath = "images/reddit_image.png"

    def get_image(self):
        try:
            print(f"[-] Getting images from /r/{self.subreddit}", flush=True)
            reddit = praw.Reddit('KindPi', user_agent='kindle user')
            subreddit = reddit.subreddit(self.subreddit)  

            top_posts = subreddit.top('day')     
            for submission in top_posts:
                if not submission.stickied:
                    if 'http://i.imgur.com/' in submission.url or 'i.redd.it/' in submission.url:
                        self.download_image(submission.url, 'images/' + str(submission.url).rsplit('/', 1)[1])
                        break
        except Exception as e:
            print("[-] An exception occurred while getting images...", flush=True)
            print(e)

    def download_image(self, image_url, temp_img):
        print(f"[-] Image URL: {image_url}")
        print(f"[-] LAST Image URL: {self.last_image_url}")
        if image_url == self.last_image_url:
            print("[-] Skipping download because image has not changed...", flush=True)
            return

        try:
            print("[-] Downloading image from reddit...", flush=True)
            response = requests.get(image_url)

            if response.status_code == 200:
                print('Downloading %s...' % (temp_img))

            with open(temp_img, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)
            
            if temp_img.endswith('.gif'):
                temp_img = self.gif_to_png(temp_img)
            
            elif temp_img.endswith('.jpg'):
                temp_img = self.jpg_to_png(temp_img)
                
            self.crop_image_and_save(temp_img)
            self.last_image_url = image_url
            
        except Exception as e:
            print("[-] An exception occurred while downloading...", flush=True)
            print(e)

    def crop_image_and_save(self, filename):
        print(f"[-] Cropping temporary image: {filename}", flush=True)
        basewidth = 550
        im = Image.open(filename)
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
        print(f"[-] Saving cropped image to {self.image_filepath}", flush=True)
        im.save(self.image_filepath)

        print(f"[-] Deleting temporary image file to save space: {filename}", flush=True)
        os.remove(filename)

    def gif_to_png(self, filename):
        im = Image.open(filename)
        im.seek(0)
        im.save(f"{filename}.png")
        os.remove(filename)
        return f"{filename}.png"

    def jpg_to_png(self, filename):
        im = Image.open(filename)
        im.save(f"{filename}.png")
        os.remove(filename)
        return f"{filename}.png"