# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem
from PySide2.QtWidgets import QGraphicsBlurEffect, QGraphicsEffect
from PySide2.QtCore import QRect, QRectF, Signal, Slot, Qt
from PySide2.QtGui import QPixmap, QPainter
import math

# local
from album import Album
from artItem import ArtItem
from album_play_item import AlbumPlayItem
from imgutils import ImgUtils

class BackgroundBlurEffect(QGraphicsBlurEffect):
    def __init__(self, parent):
        QGraphicsBlurEffect.__init__(self, parent)
        self.setBlurRadius(15.0)
        self.setBlurHints(QGraphicsBlurEffect.AnimationHint)

    def draw(self, painter):
        # QPixmap pix = self.sourcePixmap(Qt.LogicalCoordinates)
        QGraphicsBlurEffect.draw(self, painter)

class DetailScene(QGraphicsScene):

    def __init__(self, parent):
        QGraphicsScene.__init__(self, parent)
        self.x = self.y = 0
        self.cnt = 0
        self.id = -1
        self.background = None

    def prepareNewArtwork(self, cnt: int):
        self.cnt = cnt;
        self.x = 10.0
        self.y = 10.0
        self.maxw = 0
        self.rows = math.sqrt(self.cnt) if self.cnt > 0 else 10
        self.cnt = 0
        self.clear()

    def _caption(self, album: dict):
        artist = album['artist']['name']
        title = album['title']
        return artist + '\n' + title

    def set(self, album: Album):
        if album.id != self.id:
            self.id = album.malbum['id']
            bgpix : QPixmap = album.lpix

            img = album.spix
            ssize = self.sceneRect().size()
            r = self.sceneRect()
            text = self._caption(album.malbum)
            art_item = AlbumPlayItem(img, text, self.font(), album, self.sceneRect())
           # art_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            art_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            size = art_item.rect().size()
            art_item.setPos(self.x, self.y);

            self.background_it = QGraphicsPixmapItem(bgpix.scaledToHeight(size.height()))
            self.addItem(self.background_it)
            self.background_it.setPos(art_item.pos())
            self.background_it.setGraphicsEffect(BackgroundBlurEffect(self))


            self.addItem(art_item)

            print(f'scene size {ssize} item siz {size} pos {art_item.pos()}')
            self.x = self.x + 1.1 * size.width()
            if self.maxw < self.x:
                self.maxw = self.x
            self.cnt += 1
            if self.cnt >= self.rows:
                self.cnt = 0
                self.x = 10.0
                self.y = self.y + 1.1 * size.height()
            r.setWidth(self.maxw);
            r.setHeight(self.y)
            self.setSceneRect(r)

    def selectTrack(self, trackid):
        items = self.items()
        for i in items:
            if isinstance(i, AlbumPlayItem):
                i.selectTrack(trackid)

#    def drawBackground(self, painter, rect):
#        QGraphicsScene.drawBackground(self, painter, rect)
#        if self.background is not None:
#            imgu = ImgUtils()
#            painter.drawPixmap(self.sceneRect(), self.background, self.background.rect())

    def backgroundPixmap(self):
        return self.background_it.pixmap()
