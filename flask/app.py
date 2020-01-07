import os
from display import Display
from flask import Flask, render_template

dh = Display()

IMAGE_FOLDER = os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

@app.route('/dab')
def show_index():
    image_filename = dh.serve_dab()
    return render_template("output_image.html", default_image = image_filename)

# @app.route('/bus')
# def show_index():
#     image_filename = dh.serve_bus()
#     return render_template("output_image.html", default_image = image_filename)

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()