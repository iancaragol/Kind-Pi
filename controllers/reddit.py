import praw
import requests
import os
from PIL import Image

class RedditImageController:
    def get_image(self):
        reddit = praw.Reddit('Kindle', user_agent='kindle user')

        subreddit = reddit.subreddit('illustration')  

        top_posts = subreddit.top('hour')     
        for submission in top_posts:
            if not submission.stickied:
                if 'http://i.imgur.com/' in submission.url or 'i.redd.it/' in submission.url:
                    self.download_image(submission.url, 'images/' + str(submission.url).rsplit('/', 1)[1])
                    break

    def download_image(self, image_url, filename):
        response = requests.get(image_url)

        if response.status_code == 200:
            print('Downloading %s...' % (filename))

        with open(filename, 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)
        
        if filename.endswith('.gif'):
            filename = self.gif_to_png(filename)
        
        elif filename.endswith('.jpg'):
            filename = self.jpg_to_png(filename)

        self.crop_image_and_save(filename)

    def crop_image_and_save(self, filename):
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
        im.save('images/pixel_art.png')

    def gif_to_png(self, filename):
        im = Image.open(filename)
        im.seek(0)
        im.save('images/pixel_art.png')
        os.remove(filename)
        return 'images/pixel_art.png'

    def jpg_to_png(self, filename):
        im = Image.open(filename)
        im.save('images/pixel_art.png')
        os.remove(filename)
        return 'images/pixel_art.png'