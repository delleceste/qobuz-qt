# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide2.QtCore import QRect, QRectF, Signal, Slot
import math

# local
from album import Album
from artItem import ArtItem
import json

class ListScene(QGraphicsScene):
    albumSelectionChanged = Signal(Album)

    def __init__(self, parent):
        QGraphicsScene.__init__(self, parent)
        self.x = self.y = 0
        self.cnt = 0
        self.selectionChanged.connect(self.emit_albumSelectionChanged)
        self.selectedAlbum : Album = None

    def prepareNewArtwork(self, cnt: int):
        self.cnt = cnt;
        self.x = 10.0
        self.y = 10.0
        self.maxw = 0
        self.rows = math.sqrt(self.cnt) if self.cnt > 0 else 10
        self.cnt = 0
        self.clear()

    def _caption(self, album: dict):
        print(f'_caption: \033[1;33m{album}\033[0m')
        artist = album['artist']['name']
        title = album['title']
        d = album['release_date_original']
        released = d[0:d.index('-')]
        return artist + ' - ' + released + '\n' + title

    def addArtwork(self, album: Album):
        img = album.spix
        ssize = self.sceneRect().size()
        r = self.sceneRect()
        text = self._caption(album.malbum)
        art_item = ArtItem(img, text, self.font(), album)
       # art_item.setFlag(QGraphicsItem.ItemIsMovable, True)
        art_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        size = art_item.boundingRect().size()
        art_item.setPos(self.x, self.y);
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
            r.setHeight(self.y)
        else:
            r.setHeight(self.y + 1.1 * size.height())

        r.setWidth(self.maxw);
        self.setSceneRect(r)

    @Slot()
    def emit_albumSelectionChanged(self):
        s = self.selectedItems()
        if len (s) == 1:
            a = s[0].album
            self.selectedAlbum = a
            self.albumSelectionChanged.emit(a)
