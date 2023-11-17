# This Python file uses the following encoding: utf-8
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QGraphicsItem, QGraphicsPixmapItem, QTreeWidgetItem
from PySide2.QtCore import QObject, Slot, Signal, QThread, QRect, QPoint, QPointF, QDateTime, Qt, QTimer
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
from PySide2.QtMultimedia import QMediaPlayer

from minim import qobuz as qo

class QoFormat(Enum):
    MP3 = 5
    CD = 6
    HiRes96 = 7
    HiRes192 = 27

class QobuzQtStatus:
    def __init__(self):
        self.play_scheduled = False

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
        self.status = QobuzQtStatus()

        # Player
        self.player = Player(self)

        # Text View helper
        self.textview = TextView(self)

        # connections
        self.win.ui.pbSearch.setDisabled(True)
        self.win.ui.pbSearch.clicked.connect(self.search)
        self.win.scene.albumSelectionChanged.connect(self.albumSelectionChanged)
        self.win.player_scene.trackDoubleClicked.connect(self.sceneTrackDoubleClicked)
        self.win.player_scene.seekToPos.connect(self.player.seek)
        self.win.ui.pbBack.clicked.connect(self.showListView)
        self.win.ui.tw.itemSelectionChanged.connect(self.trackSelectionChanged)
        self.win.ui.tw.itemDoubleClicked.connect(self.trackDoubleClicked)
        self.win.ui.pbPlay.clicked.connect(self.play)
        self.win.ui.pbStop.clicked.connect(self.stop)
        self.win.ui.pbClear.clicked.connect(self.clear)
        self.win.ui.pbAdd.clicked.connect(self.add)

        self.player.track_index_changed.connect(self.on_track_index_changed)
        self.player.qmplayer.mediaStatusChanged.connect(self.on_player_media_status_changed)
        self.player.enqueued.connect(self.on_player_enqueued)

        # qmediaplayer connections
        self.player.qmplayer.durationChanged.connect(self.on_player_durationChanged)
        self.player.qmplayer.positionChanged.connect(self.on_player_positionChanged)
        self.player.qmplayer.seekableChanged.connect(self.on_player_seekableChanged)

        # init visibility / UI
        self.win.ui.pbBack.setVisible(False)

        # albums Album in album.py minim.Album + extensions (pixmaps)
        self.albums = dict()

        # TracksView helper class
        self.tracks_view = TracksView()

        # search: will be initialized after login with a valid session
        self._search = None


        # for testing
        self.win.ui.leSearch.setText("let it bleed")

        # more UI setup
        self.win.ui.wRight.setVisible(False)
        self.win.ui.w_list.setVisible(False)
        self.win.ui.pbAdd.setVisible(False)
        self.win.ui.wRight.setVisible(False)
        self.win.ui.pbPlay.setVisible(False)


    @Slot(Threadable)
    def on_login(self, login):
        msg = f'logged in as {login.name}'
        self.win.statusBar().showMessage(msg)
        if login.session != None:
            self.session = login.session
            self._search = Search(self.session)
            self.win.ui.pbSearch.setEnabled(True)

            self.win.ui.leSearch.textChanged.connect(self.on_search_text_changed)
            self._search_tmr = QTimer(self)
            self._search_tmr.timeout.connect(self.search)
            self._search_tmr.setSingleShot(True)
            self._search_tmr.setInterval(500)

    @Slot(str)
    def on_search_text_changed(self, str):
        print(f'restarting timer {str}')
        self._search_tmr.start()

    @Slot()
    def search(self):
        # self.win.scene.clear()
        self._search.setKeyword(self.win.ui.leSearch.text())
        self.win.statusBar().showMessage(f'searching {self.win.ui.leSearch.text()}')
        th = QobuzQtThread(self, self._search)
        th.finished.connect(self.on_search_results)
        th.start()
        self.win.ui.pbAdd.setDisabled(True)
        self.win.ui.pbPlay.setDisabled(True)

    @Slot()
    def on_search_results(self, search: Search):
        self.win.ui.stackW.setCurrentIndex(0)
        changed = False
        if search.result_type == SearchResult.Album:
            idrem = []
            found_ids = []
            for a in search.results:
                found_ids.append(a['id'])

            for id in self.albums:
                if id not in found_ids:
                    idrem.append(id)

            for r in idrem:
                changed = True
                print(f'\033[1;31mremove album \033[1;33m{self.albums.get(r).malbum["title"]}\033[0m')
                self.albums.pop(r)

            for album in search.results:
                myal = Album(album) # album is minim.qobuz.Album
                if self.albums.get(myal.id) == None:
                    changed = True
                    self.albums[myal.id] = myal
                else:
                    print(f'\033[1;32malbums already contains \033[1;33m{myal.malbum["title"]}\033[0m')

            if changed:
                albums = []
                for id in self.albums:
                    albums.append(self.albums[id])
                self.win.scene.prepareNewArtwork(albums)
                for a in albums:
                    th = QobuzQtThread(self, ArtworkFetch(a))
                    th.finished.connect(self.on_img_ready)
                    th.start()

    @Slot(Threadable)
    def on_img_ready(self, artwork_fetch: ArtworkFetch):
        alist = []
        for a in self.albums:
            alist.append(self.albums[a])
            if not self.albums[a].artwork_fetch: # not all albums with artwork yet
                return

        self.win.scene.addArtwork(alist)

        self.win.statusBar().showMessage(f'found {len(self.albums)} albums matching {self.win.ui.leSearch.text()}')


    @Slot(Threadable)
    def on_album_fetched(self, album_f : AlbumFetch):
        if album_f.id == self.win.scene.selectedAlbum.id:
            self.win.scene.selectedAlbum.setTracks(album_f.getTracks())
            self.textview.setTracks(self.win.ui.te)
            self.win.ui.pbAdd.setEnabled(True)
            self.win.ui.pbPlay.setEnabled(True)

    @Slot(Album)
    def albumSelectionChanged(self, album : Album):
        print(f'albumSelectionChanged: {album}')
        self.win.ui.pbAdd.setEnabled(True)
        self.win.ui.pbPlay.setEnabled(True)
        self.win.ui.pbAdd.setVisible(True)
        self.win.ui.pbPlay.setVisible(True)
        self.win.ui.wRight.setVisible(True)
        self.win.player_scene.prepareNewArtwork(1)
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
        self.win.ui.pbSearch.setVisible(cur_view == CurrentView.List)

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
    def play(self, offset : int = 0):
        if self.win.ui.tw.topLevelItemCount() == 0:
            self.add()
        self._toggleScene(CurrentView.Detail)
        album = self.tracks_view.activeAlbum(self.win.ui.tw)
        self.win.player_scene.set(album)
        print(f'qobuz_qt.play: media status: {self.player.qmplayer.mediaStatus()}')
        if self.player.enqueueReady():
            self.player.play(offset)
        else: # self.add calls player.enqueue that fetches urls in a secondary thread
            self.status.play_scheduled = True


    @Slot()
    def stop(self):
        self.tracks_view.deselect(self.win.ui.tw)
        self.win.player_scene.stop()
        self.player.stop()

    @Slot()
    def clear(self):
        self.player.stop()
        self.player.clear()
        self.tracks_view.clear(self.win.ui.tw)
        self.showListView()

    @Slot(QTreeWidgetItem, int)
    def trackDoubleClicked(self, it, col):
        print(f'track double clicked index {self.tracks_view.index(self.win.ui.tw, it)}')
        self.play(self.tracks_view.index(self.win.ui.tw, it));

    @Slot(str)
    def sceneTrackDoubleClicked(self, track_id):
        print(f'trackDoubleClicked: {track_id}')
        self.player.play_by_id(track_id)

    @Slot(int)
    def on_track_index_changed(self, idx):
        self.tracks_view.select(self.win.ui.tw, idx)
        album = self.tracks_view.activeAlbum(self.win.ui.tw)
        print(f'qobuz_qt.on_track_index_changed: current album {album.malbum}')
        if album is not None:
            self.win.player_scene.set(album)
            self.win.player_scene.selectTrack(self.player.trackId(idx))

    @Slot(QMediaPlayer.MediaStatus)
    def on_player_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.win.statusBar().showMessage("media loaded")

    @Slot()
    def on_player_enqueued(self):
        if self.status.play_scheduled:
            self.player.play()
            self.status.play_scheduled = False

    @Slot(int)
    def on_player_durationChanged(self, duration):
        self.win.player_scene.setPlayerDuration(duration)

    @Slot(int)
    def on_player_positionChanged(self, p):
        self.win.player_scene.setPlayerPos(p)

    @Slot(bool)
    def on_player_seekableChanged(self, s):
        print(f'player seekable changed to {s}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qoqt = QobuzQt()
    sys.exit(app.exec_())
