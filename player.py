# This Python file uses the following encoding: utf-8

from PySide2.QtCore import QObject, Slot, QUrl, Signal
from threadable import Threadable, QobuzQtThread
from PySide2.QtMultimedia import QMediaPlayer, QAudioProbe, QMediaPlaylist, QMediaContent, QAudio

from minim import qobuz as qo
from typing import Union

class TrackUriFetch(Threadable):
    def __init__(self, session: qo.PrivateAPI, tracks : list, format_id: Union[int, str]):
        self.tracks = tracks
        self.format = format_id
        self.turls = []
        self.session = session

    def run(self):
        for t in self.tracks:
            self.turls.append(self.session.get_track_file_url(t, self.format))

    def getName(self):
        return "TrackUriFetch"


class Player(QObject):
    track_changed = Signal(int)

    def __init__(self, parent: QObject):
        QObject.__init__(self, parent)
        self.playlist = QMediaPlaylist()
        self.player = None
        self.probe = QAudioProbe()

        self.playlist.loaded.connect(self.on_playlist_loaded)
        self.playlist.currentIndexChanged.connect(self.on_track_changed)
        self.playlist.loadFailed.connect(self.on_playlist_load_failed)

    def enqueue(self, session: qo.PrivateAPI, ids: list, format_id: Union[int, str]):
        th = QobuzQtThread(self, TrackUriFetch(session, ids, format_id))
        th.finished.connect(self.on_urls_ready)
        th.start()

    @Slot(TrackUriFetch)
    def on_urls_ready(self, trackurif):
        pos = self.playlist.mediaCount()
        media_content = []
        print(f'on_urls_ready: media count {pos} adding {len(trackurif.turls)}')
        for tu in trackurif.turls:
            media_content.append(QMediaContent(tu['url']))
        self.playlist.addMedia(media_content)
        if self.playlist.mediaCount() > 0:
            if self.player is None:
                self.player = self._setup_player()
        self.player.setMedia(QMediaContent(self.playlist))

    def play(self, offset : int = 0):
        if not self.playlist.isEmpty():
            if self.player is None:
                self.player = self._setup_player()
                self.player.setMedia(QMediaContent(self.playlist))
            print(f'playing playlist size {self.playlist.mediaCount()}... buf fill {self.player.bufferStatus()} offset \033[32m{offset}\033[0m')
            self.playlist.setCurrentIndex(offset)
            self.on_track_changed(offset)
            self.player.play()
            print(f'playing playlist at index {self.player.playlist().currentIndex()}')

    def stop(self):
        print('stopping')
        # self.playlist.clear() # for now
        if self.player is not None:
            self.player.stop()
            self.player = None # release resource

    def clear(self):
        if self.player is not None:
            self.player.stop()
            self.player = None
            self.playlist.clear()

    @Slot(QMediaPlayer.Error)
    def on_player_err(self, e):
        print(f'player.py: player error: {e}')

    @Slot(QMediaPlayer.State)
    def on_state_changed(self, state):
        print(f'player.py: player state changed: {state} sender {self.sender}')

    @Slot(QMediaPlayer.MediaStatus)
    def on_status_changed(self, status):
        print(f'player.py: player state changed: {status} sender {self.sender}')

    @Slot(int)
    def on_buf_stat_changed(self, percent):
        print(f'player.py: player buffer fill: {percent} sender {self.sender}')

    @Slot(float)
    def on_rate_changed(self, rate):
        print(f'player.py: player rate changed: {rate}')

    @Slot()
    def on_playlist_loaded(self):
        print(f'player.py: playlist loaded. size: {self.playlist.mediaCount()}')


    @Slot(int)
    def on_track_changed(self, idx):
        self.track_changed.emit(idx)

    @Slot()
    def on_playlist_load_failed(self):
        print(f'player.py: playlist load failed: {self.playlist.errorString()}')


    def _setup_player(self):
        player = QMediaPlayer(self)
        player.setAudioRole(QAudio.MusicRole);
        player.error.connect(self.on_player_err)
        player.stateChanged.connect(self.on_state_changed)
        player.mediaStatusChanged.connect(self.on_status_changed)
        player.playbackRateChanged.connect(self.on_rate_changed)
        player.bufferStatusChanged.connect(self.on_buf_stat_changed)
        return player

