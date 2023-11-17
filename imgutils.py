# This Python file uses the following encoding: utf-8
from PySide2.QtGui import QPixmap, QImage, QColor
from PIL import Image, ImageQt, ImageFilter
from PySide2.QtCore import  QRect, QPoint
import io

class ImgUtils:
    def __init__(self):
        pass

    def bestFgColor(self, image : QImage):
        """return the best foreground color according to the pixmap color"""
        # Convert the image to a QPixmap
        r = 0.0
        g = 0.0
        b = 0.0
        pcnt = float(image.width() * image.height())
        for i in range(0, image.width()):
            for j in range(0, image.height()):
                rgb = image.pixelColor(i, j)
                r += rgb.redF()
                g += rgb.greenF()
                b += rgb.blueF()

        # Get the average color of the image
        r /= pcnt
        g /= pcnt
        b /= pcnt
        # Calculate relative luminance (perceived brightness)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
#        print(f'ImgUtils.bestFgColor: luminance is {luminance}')
        # Choose black or white based on luminance
        if luminance < 0.35:
            return "white"
        return "black"
#        elif luminance < 0.5:
#            return "lightgray" # "DimGray"
#        elif luminance < 0.75:
#            return "DimGray" # "DarkSlateGray"
#        else:
#            return "black"

    def adjustBackground(self, qi : QImage, fgcolor : str):
        return qi

        c = QColor(fgcolor)
        li = c.lightness()  # black: 0 white: 255
        darkened = 0
        lightened = 0

        for i in range(0, qi.width()):
            for j in range(0, qi.height()):
                pixc = qi.pixelColor(i, j)
                if pixc.lightness() > 155:
                    darkened += 1
                    pixc = pixc.darker(100 + pixc.lightness() - 155)
                else:
                    lightened += 1
                    pixc = pixc.lighter(200 - pixc.lightness())
                qi.setPixelColor(QPoint(i, j), pixc)

        #print(f'adjustBackground: fgcolor lightness: {li}: bg lightened {lightened} pixels darkened {darkened} over total {qi.width() * qi.height()}')

