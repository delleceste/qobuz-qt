# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide2.QtCore import QRect, QRectF, Signal, Slot, Qt, QDateTime
import math

# local
from album import Album
from artItem import ArtItem
from item_types import ItemTypes
import json

class ListScene(QGraphicsScene):
    albumSelectionChanged = Signal(Album)

    def __init__(self, parent):
        QGraphicsScene.__init__(self, parent)
        self.x = self.y = self.maxw = 0
        self.column_idx = 0
        self.grid_size = 4
        self.selectionChanged.connect(self.emit_albumSelectionChanged)
        self.selectedAlbum : Album = None

    def _caption(self, album: dict):
        artist = album['artist']['name']
        title = album['title']
        d = album['release_date_original']
        released = d[0:d.index('-')]
        return artist + ' - ' + released + '\n' + title

    def getItem(self, id):
        items = self.getArtItems()
        for i in items:
            if i.id == id:
                return i
        return None

    def getArtItems(self):
        ai = []
        for item in self.items(Qt.AscendingOrder):
            if item.type() == ItemTypes.Art.value:
                ai.append(item)
        return ai

    def prepareNewArtwork(self, albums: list):
        newids = []
        for a in albums:
            newids.append(a.id)
        rem = [] # items to remove
        print(f'prepareNewArtwork: current items count {len(self.getArtItems())}')
        for i in self.getArtItems():
            if i.id not in newids:
                rem.append(i)
        for i in rem:
            print(f'prepareNewArtwork \033[1;35m removing no more album {i.album.title}: {i.album.id}\033[0m')
            self.removeItem(i)

        self.grid_size = 4 # math.sqrt(len(albums))
        # self.grid_size = 8 if self.grid_size > 8 else self.grid_size
        self._layout()
        self.maxw = self.column_idx = 0
        self.x = self.y = 10

    def addArtwork(self, albums: list):
        albums.sort(key=lambda a: QDateTime.fromString(a.malbum['release_date_original'], 'yyyy-MM-dd').toSecsSinceEpoch())
        r = self.sceneRect()
        for album in albums:
            img = album.spix
            text = self._caption(album.malbum)
            art_item = self.getItem(album.id)
            if art_item is None:
                art_item = ArtItem(img, text, self.font(), album)
                art_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.addItem(art_item)

            size = art_item.rect().size()
            art_item.setPos(self.x, self.y);
            print(f'scene rect {self.sceneRect()} item siz {size} pos {art_item.pos()}')
            print(f'{album.title} {album.released} @ \033[1;36m{self.x}, {self.y}\033[0m')
            self.x = self.x + 1.1 * size.width()
            if self.maxw < self.x:
                self.maxw = self.x
            self.column_idx += 1
            if self.column_idx >= self.grid_size:
                self.column_idx = 0
                self.x = 10.0
                self.y = self.y + 1.1 * size.height()
                r.setHeight(self.y)
        r.setWidth(self.maxw)
        self.setSceneRect(r)

    def _layout(self):
        x = 10.0
        y = 10.0
        column_idx = 0
        maxw = 0
        ssize = self.sceneRect().size()
        r = self.sceneRect()
        arti = self.getArtItems()
        for i in arti:
            size = i.rect().size()
            i.setPos(x, y);
            print(f'list_scene._layout: scene size {ssize} item siz {size} pos {i.pos()}')
            x = x + 1.1 * size.width()
            if maxw < x:
                maxw = x
            column_idx += 1
            if column_idx >= self.grid_size:
                column_idx = 0
                x = 10.0
                y = y + 1.1 * size.height()
                r.setHeight(y)
            else:
                r.setHeight(y + 1.1 * size.height())
        if len(arti) > 0:
            r.setWidth(maxw);
            print(f'\033[1;33m_layout scene size changed from {ssize} to {r.size()}\033[0m')
            #self.setSceneRect(r)

    @Slot()
    def emit_albumSelectionChanged(self):
        s = self.selectedItems()
        if len (s) == 1:
            a = s[0].album
            self.selectedAlbum = a
            self.albumSelectionChanged.emit(a)
