# This Python file uses the following encoding: utf-8
from PySide2.QtGui import QPixmap, QImage
from PIL import Image, ImageQt, ImageFilter
from PySide2.QtCore import QBuffer
import io

class ImgUtils:
    def __init__(self):
        pass

    def blurred(self, pixmap : QPixmap):
        img = pixmap.toImage()
        pilim = ImageQt.fromqimage(img)
        blurd = pilim.filter(ImageFilter.GaussianBlur(radius=5))
        return ImageQt.ImageQt(blurd)

