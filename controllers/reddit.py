import praw
import requests
import os
from PIL import Image

class RedditImageController:
    def get_image(self):
        reddit = praw.Reddit('Kindle', user_agent='kindle user')

        subreddit = reddit.subreddit('pixelart')  

        top_posts = subreddit.top('day')     
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
            self.gif_to_png(filename)
        
        if filename.endswith('.jpg'):
            self.jpg_to_png(filename)

    def gif_to_png(self, filename):
        im = Image.open(filename)
        im.seek(0)
        im.save('images/pixel_art.png')
        os.remove(filename)

    def jpg_to_png(self, filename):
        im = Image.open(filename)
        im.save('images/pixel_art.png')
        os.remove(filename)