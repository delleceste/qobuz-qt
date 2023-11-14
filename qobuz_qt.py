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
from textview import TextView

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

        # Player
        self.player = Player(self)

        # Text View helper
        self.textview = TextView(self)

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
        self.win.ui.pbAdd.clicked.connect(self.add)
        self.player.track_index_changed.connect(self.on_track_index_changed)

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

        # more UI setup
        self.win.ui.wRight.setVisible(False)
        self.win.ui.w_list.setVisible(False)
        self.win.ui.pbAdd.setVisible(False)
        self.win.ui.wRight.setVisible(False)


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
        self.win.statusBar().showMessage(f'searching {self.win.ui.leSearch.text()}')
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

        self.win.statusBar().showMessage(f'found {len(self.albums)} albums matching {self.win.ui.leSearch.text()}')


    @Slot(Threadable)
    def on_album_fetched(self, album_f : AlbumFetch):
        if album_f.id == self.win.scene.selectedAlbum.id:
            tracks = album_f.tracks
            self.win.scene.selectedAlbum.setTracks(album_f.getTracks())
            self.textview.setTracks(self.win.ui.te)

    @Slot(Album)
    def albumSelectionChanged(self, album : Album):
        print(f'albumSelectionChanged: {album}')
        self.win.ui.pbAdd.setVisible(True)
        self.win.ui.wRight.setVisible(True)
        self.win.scene2.prepareNewArtwork(1)
        self.textview.setAlbum(album, self.win.ui.te)
        self._get_album(album.malbum['id'])

    @Slot()
    def trackSelectionChanged(self):
        items = self.win.ui.tw.selectedItems()
        for i in items:
            data = i.data(0, UserRoles.Metadata.value)
            print(f'selected \033[1;36m{data}\033[0m')
            print(f'selected: album id \033[0;36m{i.data(0, UserRoles.Album.value).title}\033[0m')

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
    def add(self):
        self.win.ui.w_list.setVisible(True)
        ids = self.tracks_view.add(self.win.ui.tw, self.textview.tracks, self.textview.album)
        # ids = self.tracks_view.getIds(self.win.ui.tw)
        self.player.enqueue(self.session, ids, QoFormat.HiRes192.value)

    @Slot()
    def play(self):
        self._toggleScene(CurrentView.Detail)
        album = self.tracks_view.activeAlbum(self.win.ui.tw)
        self.win.scene2.set(album)
        # track information stored in each item UserRole
        self.player.play()

    @Slot()
    def stop(self):
        self.tracks_view.deselect(self.win.ui.tw)
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
    def on_track_index_changed(self, idx):
        self.tracks_view.select(self.win.ui.tw, idx)
        album = self.tracks_view.activeAlbum(self.win.ui.tw)
        if album is not None:
            self.win.scene2.set(album)

    @Slot(str)
    def on_track_changed(self, track_id):
        album = self.tracks_view.activeAlbum(self.win.ui.tw)
        if album is not None:
            self.win.scene2.set(album)
            self.win.scene2.selectTrack(track_id)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qoqt = QobuzQt()
    sys.exit(app.exec_())
