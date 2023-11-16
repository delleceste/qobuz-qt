# This Python file uses the following encoding: utf-8
from PySide2.QtGui import QPixmap, QImage, QColor
from PIL import Image, ImageQt, ImageFilter
from PySide2.QtCore import  QRect
import io

class ImgUtils:
    def __init__(self):
        pass

    def bestFgColor(self, pixmap : QPixmap, rect : QRect):
        """return the best foreground color according to the pixmap color"""
        # Convert the image to a QPixmap
        image = pixmap.toImage()

        r = 0.0
        g = 0.0
        b = 0.0
        pcnt = float(rect.width() * rect.height())
        for i in range(rect.left(), rect.right()):
            for j in range(rect.top(), rect.bottom()):
                rgb = image.pixelColor(i, j)
                r += rgb.redF()
                g += rgb.greenF()
                b += rgb.blueF()

        # Get the average color of the image
        print(f'r is {r} divided by pcnt {pcnt} makes {r / pcnt} rect {rect.width()} x {rect.height()}')
        r /= pcnt
        g /= pcnt
        b /= pcnt

        # Calculate relative luminance (perceived brightness)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        print(f'on rect {rect} luminance is {luminance} avgc {r},{g},{b}')
        # Choose black or white based on luminance
        return "black" if luminance > 0.2 else "white"

