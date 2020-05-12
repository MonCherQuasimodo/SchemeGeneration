from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request

from PIL import Image

from random import choices

import numpy

import os
import sys

app = Flask(__name__)


app.config["IMAGE_UPLOADS"] = os.getcwd() + "/static/img/uploads/"
app.config["SCHEMES"] = os.getcwd() + "/static/img/schemes/"
last_file = ""


# ___________________________Web_part__________________________________ #
@app.route('/')
def hello_world():
    return render_template('schemegen.html')


@app.route("/upload_image", methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files['image']
            global last_file
            last_file = image.filename
            image.save(os.path.join(app.config["IMAGE_UPLOADS"],
                                    image.filename))
            convert_image(image.filename)
            return redirect(request.url)

    return redirect(url_for('scheme_page'))


@app.route("/scheme_page")
def scheme_page():
    full_filename_before = "/static/img/uploads/" + last_file
    full_filename = "/static/img/schemes/" + last_file
    return render_template('schemepage.html', user_image=full_filename,
                           before=full_filename_before)

# ___________________________Computing_part____________________________ #
CONST_EPSILON = 20.0
CONST_PALETTE = {"standard": [(0, 0, 0),
                              (128, 128, 128),
                              (192, 192, 192),
                              (255, 255, 255),
                              (128, 0, 0),
                              (255, 0, 0),
                              (128, 128, 0),
                              (255, 255, 0),
                              (0, 128, 0),
                              (0, 255, 0),
                              (0, 128, 128),
                              (0, 255, 255),
                              (0, 0, 128),
                              (0, 0, 255),
                              (128, 0, 128),
                              (255, 0, 255)]}


def distance(pixel, basic_colour):
    return numpy.linalg.norm(numpy.array(pixel) - numpy.array(basic_colour))


def handle_pixel(pixel, palette="standard"):
    distances = [(distance(pixel, basic_colour), basic_colour)
                 for basic_colour in CONST_PALETTE[palette]]
    distances.sort()
    probably_colour = [dist[1] for dist in distances
                       if abs(distances[0][0] - dist[0]) < CONST_EPSILON]
    return choices(probably_colour)[0]


def convert_image(filename):
    source_image = Image.open(app.config["IMAGE_UPLOADS"] + filename)

    numpy_im = numpy.array(source_image)
    width, height, depth = numpy_im.shape

    for i in range(width):
        for c in range(height):
            numpy_im[i][c] = handle_pixel(numpy_im[i][c])

    new_image = Image.fromarray(numpy_im)
    new_image.save(os.path.join(app.config["SCHEMES"], filename))

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
