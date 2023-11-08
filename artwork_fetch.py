# This Python file uses the following encoding: utf-8

from threadable import Threadable
import requests
from PySide2.QtGui import QPixmap

# local
import album

class ArtworkFetch(Threadable):
    def __init__(self, album: album.Album):
        self.album = album

    def getName(self):
        return "ArtworkFetch"

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

        self.album.artwork_fetch = True

