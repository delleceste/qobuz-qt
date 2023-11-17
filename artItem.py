# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QGraphicsPixmapItem, QGraphicsTextItem
from PySide2.QtCore import QRectF, QRect, QPointF
from PySide2.QtGui import QPixmap, QPainter, QFontMetrics, QFont, QPen, QBrush, QColor
from album import Album
from item_types import ItemTypes

class ArtItem(QGraphicsRectItem):
    def __init__(self, pix : QPixmap, text : str, font: QFont, album : Album, parent = None):
        QGraphicsRectItem.__init__(self, parent)
        margin = 10
        self.p = QGraphicsPixmapItem(pix, self)
        self.p.setPos(margin, margin)
        self.album = album
        self.id = album.id
        fm = QFontMetrics(font)
        lines = text.split('\n')
        th = fm.height() * len(lines)
        pw = pix.width();
        ph = pix.height();
        tw = 0
        short_lines = []
        for line in lines:
            llen = len(line)
            while fm.horizontalAdvance(line) > pw:
                print(f'\033[1;31mshrinking to "{line}"\033[0m')
                line = line[0:len(line) - 1]
            if(llen > len(line)):  # shrinked
                short_lines.append(line[0:len(line) - 3] + "...")
            else: # untouched
                short_lines.append(line)
        short_text = ''
        for line in short_lines:
            short_text += line + '\n' # restore lines
        self.t = QGraphicsTextItem(short_text, self)
        adetails = album.malbum
        self.t.setToolTip(text + "\n" + str(adetails))
        self.t.setPos(margin, margin + pix.height())
        self.setRect(0, 0, max(tw, pw) + 2 * margin, th + ph + 2 * margin)

    def paint(self, painter, option, widget):
        QGraphicsRectItem.paint(self, painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor(self.album.malbum["genre"]["color"]))
            pen.setWidthF(3.0)
            painter.setPen(pen)
            painter.drawRoundRect(self.boundingRect(), 2.0, 2.0)

    def type(self):
        return ItemTypes.Art.value

