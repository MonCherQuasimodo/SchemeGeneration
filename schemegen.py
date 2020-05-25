from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import send_file

from PIL import Image

from fpdf import FPDF

import traceback
import uuid

from random import choices

import os
import sys

import schemcomp

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

app = Flask(__name__)

PATHS = {
    "IMAGE_UPLOADS": os.getcwd() + "/static/img/uploads/",
    "SCHEMES": os.getcwd() + "/static/img/schemes/",
    "PALETTES": os.getcwd() + "/static/img/palettes/"
}

PDF_PATH = os.getcwd() + "/static/pdf/"

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
IMAGE_NAME = 'IMAGE_'

cur_file_name = ''


def get_filename(ext=None):
    return (cur_file_name if ext is None
            else os.path.splitext(cur_file_name)[0] + ext)


def create_sending_file():
    pdf = FPDF()
    for i in PATHS.values():
        pdf.add_page()
        pdf.image(i + get_filename(), x=0, y=0, w=210)
    pdf.output(dest="F", name=PDF_PATH + get_filename('.pdf'))


# ___________________________Web_part__________________________________ #
@app.route('/')
def main_page():
    return render_template('schemegen.html')


@app.route("/upload_image", methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files['image']
            global cur_file_name
            global ext
            cur_file_name = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
            image.save(os.path.join(PATHS["IMAGE_UPLOADS"],
                                    get_filename()))
            try:
                schemcomp.computing(get_filename(),
                                    int(request.form.get('diagonal')),
                                    request.form.get('palette').lower(),
                                    float(request.form.get('density')),
                                    request.form.get('mod'))
            except Exception as e:
                print(e, file=sys.stderr)
                traceback.print_exc()
                return redirect(url_for('error_page'))
            return redirect(request.url)
    return redirect(url_for('scheme_page'))


@app.route("/scheme_page")
def scheme_page():
    full_filename_before = "/static/img/uploads/" + get_filename()
    full_filename = "/static/img/schemes/" + get_filename()
    palette_path = "/static/img/palettes/" + get_filename()
    return render_template('schemepage.html', user_image=full_filename,
                           before=full_filename_before, palette=palette_path)


@app.route("/error_page")
def error_page():
    return render_template('errorpage.html')


@app.route("/scheme_page/download", methods=['GET', 'POST'])
def download_file():
    create_sending_file()
    return send_file(PDF_PATH + get_filename('.pdf'), as_attachment=True)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
