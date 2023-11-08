# This Python file uses the following encoding: utf-8
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QGraphicsItem, QGraphicsPixmapItem, QTreeWidgetItem
from PySide2.QtCore import QObject, Slot, Signal, QThread, QRect, QPoint, QPointF, QDateTime, Qt
import sys
from enum import Enum
from qobuzw import QobuzW
from qobuzw import CurrentView

# local imports
from album import Album
from artwork_fetch import ArtworkFetch
from threadable import Threadable, QobuzQtThread
from search import Search, SearchResult, AlbumFetch
from login import Login
from tracks_view import TracksView, UserRoles
from player import Player

from minim import qobuz as qo

class QoFormat(Enum):
    MP3 = 5
    CD = 6
    HiRes96 = 7
    HiRes192 = 27

class QobuzQt(QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        email = "delleceste@gmail.com"
        login = Login(email, "Nautilus803")
        th = QobuzQtThread(self, login)
        th.finished.connect(self.on_login)
        th.start()

        self.session = None
        self.win = QobuzW()
        self.win.show()
        msg = f'logging in as {email}...'
        self.win.statusBar().showMessage(msg)

        self.player = Player(self)

        # connections
        self.win.ui.pbSearch.setDisabled(True)
        self.win.ui.pbSearch.clicked.connect(self.search)
        self.win.scene.albumSelectionChanged.connect(self.albumSelectionChanged)
        self.win.ui.pbBack.clicked.connect(self.showListView)
        self.win.ui.tw.itemSelectionChanged.connect(self.trackSelectionChanged)
        self.win.ui.tw.itemDoubleClicked.connect(self.trackDoubleClicked)
        self.win.ui.pbPlay.clicked.connect(self.play)
        self.win.ui.pbStop.clicked.connect(self.stop)
        self.win.ui.pbClear.clicked.connect(self.clear)
        self.player.track_changed.connect(self.on_track_changed)

        # init visibility / UI
        self.win.ui.pbBack.setVisible(False)

        # albums Album in album.py minim.Album + extensions (pixmaps)
        self.albums = []

        # TracksView helper class
        self.tracks_view = TracksView()

        # search: will be initialized after login with a valid session
        self.search = None

        # for testing
        self.win.ui.leSearch.setText("The dark side of the moon")


    @Slot(Threadable)
    def on_login(self, login):
        msg = f'logged in as {login.name}'
        self.win.statusBar().showMessage(msg)
        if login.session != None:
            self.session = login.session
            self.search = Search(self.session)
            self.win.ui.pbSearch.setEnabled(True)

    @Slot()
    def search(self):
        self.search.setKeyword(self.win.ui.leSearch.text())
        th = QobuzQtThread(self, self.search)
        th.finished.connect(self.on_search_results)
        th.start()

    @Slot()
    def on_search_results(self, search: Search):
        self.win.ui.stackW.setCurrentIndex(0)
        self.win.scene.prepareNewArtwork(len(search.results))
        if search.result_type == SearchResult.Album:
            self.albums = []
            search.results.sort(key=lambda x: QDateTime.fromString(x['release_date_original'], 'yyyy-MM-dd').toSecsSinceEpoch())
            for album in search.results:
                myal = Album(album) # album is minim.qobuz.Album
                self.albums.append(myal)
                th = QobuzQtThread(self, ArtworkFetch(myal))
                th.finished.connect(self.on_img_ready)
                th.start()

    @Slot(Threadable)
    def on_img_ready(self, artwork_fetch: ArtworkFetch):
        for a in self.albums:
            if not a.artwork_fetch: # not all albums with artwork yet
                return

        for album in self.albums:
            self.win.scene.addArtwork(album)

    @Slot(Threadable)
    def on_album_fetched(self, album_f : AlbumFetch):
        tracks = album_f.tracks
        self.tracks_view.set(self.win.ui.tw, tracks, album_f.id)
        ids = self.tracks_view.getIds(self.win.ui.tw)
        self.player.enqueue(self.session, ids, QoFormat.HiRes192.value)

    @Slot(Album)
    def albumSelectionChanged(self, album):
        print(f'albumSelectionChanged: {album}')
        self._toggleScene(CurrentView.Detail)
        self.win.scene2.prepareNewArtwork(1)
        self.win.scene2.set(album)
        self._get_album(album.malbum['id'])

    @Slot()
    def trackSelectionChanged(self):
        items = self.win.ui.tw.selectedItems()
        for i in items:
            data = i.data(0, UserRoles.Metadata.value)
            print(f'selected \033[1;36m{data}\033[0m')
            print(f'selected: album id \033[0;36m{i.data(0, UserRoles.AlbumId.value)}\033[0m')

    def error(self, origin, reason):
        print(f'error: {origin}: \033[1;31m{reason}\033[0m')
        
    def _toggleScene(self, cur_view: CurrentView) :
        self.win.ui.stackW.setCurrentIndex(cur_view.value)
        self.win.ui.pbBack.setVisible(cur_view == CurrentView.Detail)

    def _get_album(self, id):
        th = QobuzQtThread(self, AlbumFetch(self.session, id))
        th.finished.connect(self.on_album_fetched)
        th.start()

    @Slot()
    def showListView(self):
        self._toggleScene(CurrentView.List)

    @Slot()
    def play(self):
        # track information stored in each item UserRole
        self.player.play()

    @Slot()
    def stop(self):
        self.tracks_view.deselect()
        self.player.stop()

    @Slot()
    def clear(self):
        self.player.stop()
        self.player.clear()
        self.tracks_view.clear(self.win.ui.tw)
        self.showListView()

    @Slot(QTreeWidgetItem, int)
    def trackDoubleClicked(self, it, col):
        self.player.play(self.tracks_view.index(self.win.ui.tw, it));

    @Slot(int)
    def on_track_changed(self, idx):
        self.tracks_view.select(self.win.ui.tw, idx)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qoqt = QobuzQt()
    sys.exit(app.exec_())
