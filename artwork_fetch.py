# This Python file uses the following encoding: utf-8

from threadable import Threadable, QobuzQtThread
import requests
from album import Album
from PySide2.QtGui import QPixmap
from PySide2.QtCore import  Slot, Signal, QObject

# local
import album

class ArtworkFetch(Threadable):
    fetch_complete = Signal(object)

    def __init__(self, album: album.Album, parent : QObject = None):
        Threadable.__init__(self, parent)
        self.album = album

    def getName(self):
        return "ArtworkFetch"

    @Slot()
    def on_finished(self, threadable : Threadable):
        self.album.artwork_fetch = True
        self.fetch_complete.emit(self)

    def fetch(self):
        th = QobuzQtThread(self, self)
        th.finished.connect(self.on_finished)
        th.start()

    def run(self):
        # album.Album.malbum -> minim.qobuz.Album
        urlsmall = self.album.malbum['image']['small']
        urllarge = self.album.malbum['image']['large']
        urlthumb = self.album.malbum['image']['thumbnail']
        img = requests.get(urlsmall)
        if img.status_code == 200:
            self.album.spix = QPixmap()
            self.album.spix.loadFromData(img.content)
        else:
            print(f'img download error: {img.reason}')

        img = requests.get(urllarge)
        if img.status_code == 200:
            self.album.lpix = QPixmap()
            self.album.lpix.loadFromData(img.content)
        else:
            print(f'img download error: {img.reason}')

        img = requests.get(urlthumb)
        if img.status_code == 200:
            self.album.thpix = QPixmap()
            self.album.thpix.loadFromData(img.content)
        else:
            print(f'img download error: {img.reason}')


