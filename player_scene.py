# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem, QGraphicsSceneMouseEvent
from PySide2.QtWidgets import QGraphicsBlurEffect, QGraphicsEffect
from PySide2.QtCore import QRect, QRectF, Signal, Slot, Qt, QPointF
from PySide2.QtGui import QPixmap, QPainter, QTransform
import math

# local
from album import Album
from artItem import ArtItem
from album_play_item import AlbumPlayItem, TrackItem
from imgutils import ImgUtils
from item_types import ItemTypes

class BackgroundBlurEffect(QGraphicsBlurEffect):
    def __init__(self, parent):
        QGraphicsBlurEffect.__init__(self, parent)
        self.setBlurRadius(15.0)
        self.setBlurHints(QGraphicsBlurEffect.AnimationHint)

    def draw(self, painter):
        # QPixmap pix = self.sourcePixmap(Qt.LogicalCoordinates)
        QGraphicsBlurEffect.draw(self, painter)

class PlayerScene(QGraphicsScene):
    trackDoubleClicked = Signal(str)
    seekToPos = Signal(float)

    def __init__(self, parent):
        QGraphicsScene.__init__(self, parent)
        self.x = self.y = 0
        self.cnt = 0
        self.id = -1
        self.background = None
        self.play_item = None

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
            self.prepareNewArtwork(1)
            self.id = album.malbum['id']
            bgpix : QPixmap = album.lpix

            img = album.spix
            ssize = self.sceneRect().size()
            r = self.sceneRect()
            text = self._caption(album.malbum)
            self.play_item = AlbumPlayItem(img, text, self.font(), album, self.sceneRect())
           # art_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.play_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            size = self.play_item.rect().size()
            self.play_item.setPos(self.x, self.y);

            self.background_it = QGraphicsPixmapItem(bgpix.scaledToHeight(size.height()))
            self.addItem(self.background_it)
            self.background_it.setPos(self.play_item.pos())
            self.background_it.setGraphicsEffect(BackgroundBlurEffect(self))
            self.addItem(self.play_item)

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

    def stop(self):
        items = self.items()
        for i in items:
            if isinstance(i, AlbumPlayItem):
                i.deselect()

    def setPlayerDuration(self, du):
        self.play_item.setTrackDuration(du)

    def setPlayerPos(self, p):
        self.play_item.setTrackPos(p)


    def backgroundPixmap(self):
        return self.background_it.pixmap()

    def mouseDoubleClickEvent(self, event : QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            i = self.itemAt(event.scenePos(), QTransform())
            if isinstance(i, TrackItem):
                self.trackDoubleClicked.emit(str(i.track_id))
        QGraphicsScene.mouseDoubleClickEvent(self, event)

    def mousePressEvent(self, event : QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self._handleSeek(event.scenePos())
        QGraphicsScene.mousePressEvent(self, event)

    def mouseMoveEvent(self, event : QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton and event.buttonDownScenePos(event.button()).isValid():
            self._handleSeek(event.scenePos())
        QGraphicsScene.mouseMoveEvent(self, event)

    def _handleSeek(self, scenep):
        i = self.itemAt(scenep, QTransform())
        if i.type() == ItemTypes.AlbumPlay.value:
            seekp = i.seekPos()
            if seekp >= 0:
                self.seekToPos.emit(seekp)

