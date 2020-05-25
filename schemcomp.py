from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageFont

from random import choices

import matplotlib.pyplot as plt
import matplotlib.ticker as plticker

import numpy as np
import os

import math

DPI = 200
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
MIN_PIXELS_PER_CELL = 16

IMAGE_UPLOADS = os.getcwd() + "/static/img/uploads/"
SCHEMES = os.getcwd() + "/static/img/schemes/"
PALETTES = os.getcwd() + "/static/img/palettes/"


def pixel_per_cell(image_size, size, density):
    return max(1, int((np.hypot(image_size[0], image_size[1])) /
                      (size * density)))


def distance(pixel, basic_colour):
    return np.linalg.norm(np.array(pixel) - np.array(basic_colour))


def handle_pixel(pixel, palette="standard"):
    distances = [(distance(pixel, basic_colour), basic_colour)
                 for basic_colour in CONST_PALETTE[palette]]
    distances.sort()
    probably_colour = [dist[1] for dist in distances
                       if abs(distances[0][0] - dist[0]) < CONST_EPSILON]
    return choices(probably_colour)[0]


def high_quality_mod(source_image, palette):
    pixels = source_image.load()
    for i in range(source_image.size[0]):
        for j in range(source_image.size[1]):
            pixels[i, j] = handle_pixel(pixels[i, j], palette)
    return source_image


def fast_mod(source_image, palette):
    palette = np.array(CONST_PALETTE[palette], dtype=np.uint8)
    numpy_im = np.array(source_image)
    image = numpy_im[:, :, :, np.newaxis]
    reshaped_palette = palette.T.reshape(1, 1, 3, -1)
    distance = np.linalg.norm(image - reshaped_palette, axis=2)
    indexes = np.argmin(distance, axis=2)
    numpy_im = palette[indexes]
    return Image.fromarray(numpy_im)


def add_grid(source_image, pixel_per_cell_value, fig):
    fig.set_figwidth(float(source_image.size[0])/DPI)
    fig.set_figheight(float(source_image.size[1])/DPI)
    fig.set_dpi(DPI)

    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax = fig.add_subplot(111)
    loc = plticker.MultipleLocator(base=pixel_per_cell_value)
    ax.xaxis.set_major_locator(loc)
    ax.yaxis.set_major_locator(loc)
    ax.grid(which='major', axis='both', linestyle='-', )
    ax.imshow(source_image)


def input_image(filename):
    return Image.open(IMAGE_UPLOADS + filename)


def output_image(fig, filename):
    fig.savefig(SCHEMES + filename, dpi=DPI)


def computing(filename, size=30, palette='standard',
              density=5.1, mod='High-quality', fig=plt.figure()):
    # Ввод
    source_image = input_image(filename)

    # Считаем, сколько пикселей будет в одной клеточке.
    pixel_per_cell_value = pixel_per_cell(source_image.size, size, density)
    if pixel_per_cell_value != MIN_PIXELS_PER_CELL:
        coef = math.ceil(MIN_PIXELS_PER_CELL / pixel_per_cell_value)
        source_image = source_image.resize((source_image.size[0] * coef,
                                            source_image.size[1] * coef))
        pixel_per_cell_value = pixel_per_cell(source_image.size,
                                              size, density)

    width, height = source_image.size
    # Уменьшаем картинку до размера количества клеточек.
    width_cell = width // pixel_per_cell_value
    height_cell = height // pixel_per_cell_value
    source_image = source_image.resize((width_cell, height_cell))

    # Приводим цвета маленькой картинки к палитре
    if mod == 'High-quality':
        source_image = high_quality_mod(source_image, palette)
    else:
        source_image = fast_mod(source_image, palette)

    # Возвращаем исходный размер картинкe
    source_image = source_image.resize((width_cell * pixel_per_cell_value,
                                        height_cell * pixel_per_cell_value))
    # Рисуем клеточки
    add_grid(source_image, pixel_per_cell_value, fig)

    # Вывод
    output_image(fig, filename)
    fig.clear()

    # Таблица цветов
    # Для каждого файла своя, так как некоторые цвета могут не
    # использоваться, но это пока не проверяется
    create_color_table(filename, palette='standard')


def get_cell_color(color):
    cell = Image.new(mode='RGB', size=(40, 30), color=color)
    return ImageOps.expand(cell, border=2, fill='black')


def create_color_table(filename, palette='standard'):
    table = Image.new(mode='RGB',
                      size=(400, (len(CONST_PALETTE[palette]) + 1) * 40),
                      color='white')
    table = ImageOps.expand(table, border=3, fill='black')
    draw = ImageDraw.Draw(table)
    for i in range(len(CONST_PALETTE[palette])):
        cell = get_cell_color(CONST_PALETTE[palette][i])
        table.paste(cell, (30, 20 + i * 40))
        font = ImageFont.truetype("arial.ttf", 15)
        draw.text((80, 30 + i * 40),
                  '#Number in company palette  ' +
                  str(CONST_PALETTE[palette][i]), (0, 0, 0), font)
    table.save(PALETTES + filename)

'''
if __name__ == "__main__":
'''
