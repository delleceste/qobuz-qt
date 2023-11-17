# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QGraphicsPixmapItem, QGraphicsTextItem, QWidget
from PySide2.QtCore import QRectF, QRect, QPointF, QSize, QSizeF, Signal, Qt
from PySide2.QtGui import QPixmap, QPainter, QPainterPath, QFontMetrics, QFont, QPen, QColor, QBrush
from PySide2.QtWidgets import QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent
from album import Album
from imgutils import ImgUtils
from item_types import ItemTypes
from math import pi, sin, cos, sqrt, atan2
import textwrap

class RoundAlbumItem(QGraphicsEllipseItem):
    def __init__(self, pix : QPixmap, parent : QGraphicsItem = None):
        QGraphicsEllipseItem.__init__(self, parent)
        self.pix = pix
        self.setRect(pix.rect())
        self.duration = self.pos = 0
        self.setAcceptHoverEvents(True)
        self.px = None
        self.py = None
        self.pa = None # touch (mouse) point angle

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing, True)
        path = QPainterPath()
        path.addEllipse(self.pix.rect());
        painter.setClipPath(path);
        painter.drawPixmap(self.pix.rect(), self.pix)
        self.drawPos(painter, self.pix.rect())

    def drawPos(self, painter : QPainter, rect : QRect):
        c = QColor("LightGreen")
        c.setAlpha(210)
        p = QPen(c)
        p.setWidthF(18.0)
        painter.setPen(p)
        startAngle = 0
        spanAngle = -16 * (self.pos / self.duration) * 360.0 if self.duration > 0 else 0
        painter.drawArc(rect, startAngle, spanAngle)
        if self.pa is not None:
            c = QColor("DeepSkyBlue")
            p.setColor(c)
            p.setWidth(8)
            painter.setPen(p)
            painter.drawArc(rect, startAngle, self.pa * 16)

    def hoverMoveEvent(self, event : QGraphicsSceneHoverEvent):
        oldpa = self.pa
        print(f'album_play_item: hoverMove: {event}')
        p = event.pos()
        r = self.rect()
        c = r.center()
        radius = r.width() / 2.0
        a = 0
        dx = p.x() - c.x()
        dy = p.y() - c.y()
        if sqrt(dx ** 2 + dy ** 2) > 0.8 * radius:
            if dx >= 0 and dy >= 0:
                a = atan2(dy, dx)
            elif dx <  0 and dy > 0:
                a = pi/2.0 + atan2(-dx, dy)
            elif dx < 0 and dy < 0:
                a = pi + atan2(-dy, -dx)
            else: # dx > 0 and dy < 0
                a = 3 * pi / 2.0 + atan2(dx, -dy)
            self.pa = - a * 360.0 / 2.0 / pi
            print(f'{dx}, {dy}, angle {self.pa}')
        else:
            self.pa = None
        if oldpa != self.pa:
            self.update()

    def seekPos(self):
        if self.pa != None:
            return -self.pa / 360.0 if self.pa > -359 else -359
        return -1

    def hoverLeaveEvent(self, event : QGraphicsSceneHoverEvent):
        oldpa = self.pa
        self.pa = None
        if oldpa != self.pa:
            self.update()

    def type(self):
        return ItemTypes.AlbumPlay.value

class TrackItem(QGraphicsTextItem):
    def __init__(self, track : dict, font : QFont, parent : QGraphicsItem = None):
        QGraphicsTextItem.__init__(self, str(), parent)
        self.connector = None
        self.setFont(font)
        self.setPlainText(self.makeText(track))
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True);
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.track_id = str(track['id']) # use str
        self.bgpix = None
        self.bgrect = None
        self.imgu = ImgUtils()
        # self.size is set after setPlainText

    def setText(self, text : str):
        # adjusts self.size
        self.setPlainText(self.makeText(text))

    def paint(self, painter, option, widget):
        if self.bgrect is None:
            self._graphics_prepare()

        painter.drawPixmap(option.rect, self.bgpix, self.bgpix.rect())
        brushc = QColor("gray") if self.defaultTextColor().lightness() > 155 else QColor("white") if not self.isSelected() else QColor("palegreen")
        brushc.setAlpha(90 if not self.isSelected() else 200)

        color = QColor("green") if self.isSelected() else QColor("lightblue")
        painter.setPen(color.darker())
       # color.setAlpha(190)
        painter.setBrush(brushc)
        r = QRectF(QPointF(0,0), option.rect.size())
        painter.drawRoundedRect(r, 2.0, 2.0)
        QGraphicsTextItem.paint(self, painter, option, widget)

        if self.isSelected():
            painter.setBrush(QBrush())
            p = QPen("white")
            p.setWidthF(4.5)
            painter.setPen(p)
            painter.drawRoundedRect(r, 3.0, 3.0)
            p.setColor(QColor("MediumSeaGreen"))
            p.setWidthF(0)
            painter.setPen(p)
            painter.drawRoundedRect(r, 3.0, 3.0)

    def setConnector(self, path):
        self.connector = path

    def pathFrom(self, _from : QPointF):
        mycenter = QRectF(self.pos(), self.size).center()
        path = QPainterPath(_from) # start: center of the scene
        c1 = (mycenter + _from)*.5*.9
        c1.setY(c1.y() * 1.2);
        c2 = (mycenter + _from)*.5*.9;
        c2.setY(c2.y() * 1.2);
        path.cubicTo(c1, c2, mycenter)
        return path

    def makeText(self, t : dict):
        font = self.font()
        n = t['track_number']
        tit = t['title']
        tit = textwrap.fill(tit, 20, max_lines = 3)
        sec = int(t['duration'])
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        if h > 0:
            duration = "{0:02d}:{1:02d}:{2:02d}".format(h, m, s)
        else:
            duration = "{0:02d}:{1:02d}".format(m, s)

        s = f'{n}. {tit} [{duration}]'

        # calculate size needed
        fm = QFontMetrics(font)
        x = 0
        y = 0
        a = 0
        for line in s.split('\n'):
            a = fm.horizontalAdvance(line)
            if a > x:
                x = a
            y += fm.height()
        self.size = QSizeF(x, y)
        return s

    def itemChange(self, change : QGraphicsItem.GraphicsItemChange, value ):
        if (change == QGraphicsItem.ItemPositionChange and self.connector != None):
            # value is the new position.
            path : QPainterPath = self.connector.path()
            self.connector.setPath(self.pathFrom(path.pointAtPercent(0)))
            self.scene().update()
            self._graphics_prepare()

        elif(change == QGraphicsItem.ItemSelectedChange):
            pass

        return QGraphicsItem.itemChange(self, change, value);

    def _graphics_prepare(self):
        self.bgrect = self.mapRectToItem(self.scene().background_it, self.boundingRect()).toRect()
        qi = self.scene().backgroundPixmap().copy(self.bgrect).toImage() # scene() : DetailScene
        fgcolor = self.imgu.bestFgColor(qi)
        self.imgu.adjustBackground(qi, fgcolor) # make sure text is well readable
        self.bgpix = QPixmap.fromImage(qi)
        self.setDefaultTextColor(QColor(fgcolor))


class AlbumPlayItem(QGraphicsRectItem):
    def __init__(self, pix : QPixmap, text : str, font: QFont, album : Album, sceneRect : QRectF, parent = None):
        QGraphicsRectItem.__init__(self, parent)
        sr = sceneRect;
        self.setRect(sr.adjusted(sr.width() * 0.04, sr.height() * 0.04, -sr.width() * 0.04, -sr.height() * 0.04))
        print(f'album play item rect {self.rect()} has tracks {len(album.tracks)}')
        self.p = RoundAlbumItem(pix, self)
        r = self.rect()
        c = r.center()
        self.p.setPos(c.x() - pix.width()/2.0, c.y() - pix.height() / 2.0)
        self.album = album
        self.track_items = []
        fm = QFontMetrics(font)
        lines = text.split('\n')
        th = fm.height() * len(lines)
        # pw = pix.width();
        pw = self.rect().width()
        ph = self.rect().height()
        # ph = pix.height();
        # tw = 0
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

        tcnt = len(album.tracks)
        alpha = 2 * pi / (tcnt );
        a0 = 0
        pr = self.p.rect() # pixmap rect
        radius = min(pr.width(), pr.height()) * 1.3
        x = c.x()
        y = c.y()
        i = 0
        prevr = None
        trackfont = font
        #trackfont.setPointSizeF(font.pointSizeF() - 1.2)
        trackfont.setBold(True)
        for t in album.tracks:
            a = a0 + i * alpha
            ti = TrackItem(t, trackfont, self)
            self.track_items.append(ti)
            size = ti.size
            tr = QRectF(QPointF(0,0), size)
            xoff = tr.width() / 2.0
            yoff = tr.height() / 2.0
            pos = QPointF(x + radius * sin(a) - xoff, y - radius * cos(a) - yoff)
            # colliding items?
            xr = 1.0
            size *= 1.2
            thisr = QRectF(pos, size)
            if i == 0:
                rect0 = QRectF(thisr)
            if prevr is not None:
                print('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv')
                print(f'\033[1;32m this rect {ti.toPlainText()} {thisr}  prev rect {self.track_items[len(self.track_items) - 2].toPlainText()} {prevr} \033[0m')
            while prevr is not None and prevr.intersects(thisr):
                print(f'\033[1;31mcollision: {ti.toPlainText()} {thisr} collides with {self.track_items[len(self.track_items) - 2].toPlainText()} {prevr} \033[0m')
                xr *= 1.1
                thisr.moveTopLeft(QPointF(x + radius * xr * sin(a) - xoff, y - radius * xr * cos(a) - yoff))
                if not r.contains(thisr): # go back to fit in the scene
                    print(f'\033[1;31m MUST REVERT BACK CUZ {thisr} OUT OF SCENE!!!!!!!!\033[0m')
                    thisr.moveTopLeft(QPointF(x + radius / 1.1 * sin(a) - xoff, y - radius / 1.1 * cos(a) - yoff))
                    break

            while len(self.track_items) == len(album.tracks) and rect0.intersects(thisr):
                xr *= 1.1
                thisr.moveTopLeft(QPointF(x + radius * xr * sin(a) - xoff, y - radius * xr * cos(a) - yoff))
                print(f'\033[0;35mcollision: {ti.toPlainText()} {thisr} collides with FIRST rect {self.track_items[len(self.track_items) - 1].toPlainText()} {rect0} \033[0m')
                if not r.contains(thisr): # step back
                    print(f'\033[0;35m MUST REVERT BACK CUZ {thisr} OUT OF SCENE!!!!!!!!\033[0m')
                    thisr.moveTopLeft(QPointF(x + radius / 1.1 * sin(a) - xoff, y - radius / 1.1 * cos(a) - yoff))
                    break
            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            ti.setPos(thisr.topLeft())

            # connect center to track item center
            path_i = QGraphicsPathItem(self)
            path_i.setZValue(-10)
            path_i.setPen(QPen("gray"))
            ti.setConnector(path_i) # associate the path_i connector to the track item
            path_i.setPath(ti.pathFrom(c))
            prevr = QRectF(thisr)
            i += 1



        self.t.setToolTip(text + "\n" + str(adetails))
        self.t.setPos(self.p.x(), self.p.y() + pix.height())

    def paint(self, painter, option, widget):
        painter.setPen(QPen("lightblue"))
        painter.drawRoundedRect(self.boundingRect(), 2.0, 2.0)


    def selectTrack(self, trackid):
        print(f'selecting track {trackid} type {type(trackid)}')
        for t in self.track_items:
            t.setSelected(True if t.track_id == trackid else False)

    def deselect(self):
        for t in self.track_items:
            t.setSelected(False)

    def setTrackDuration(self, du):
        self.p.duration = du
        self.p.update()

    def setTrackPos(self, pos):
        self.p.pos = pos
        self.p.update()








