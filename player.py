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
    track_index_changed = Signal(int)
    enqueued = Signal()

    def __init__(self, parent: QObject):
        QObject.__init__(self, parent)
        self.playlist = QMediaPlaylist()
        self.qmplayer = self._setup_player()
        self.probe = QAudioProbe()
        self.ids = []
        self.offset = -1
        self.enqueue_ready = False # used by enqueue and on_urls_ready

        self.playlist.loaded.connect(self.on_playlist_loaded)
        self.playlist.currentIndexChanged.connect(self.on_track_index_changed)
        self.playlist.loadFailed.connect(self.on_playlist_load_failed)

    def enqueue(self, session: qo.PrivateAPI, ids: list, format_id: Union[int, str]):
        self.enqueue_ready = False
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
            self.ids.append(str(tu['track_id']))
        self.playlist.addMedia(media_content)
        self.qmplayer.setMedia(QMediaContent(self.playlist))
        self.enqueued.emit()
        self.enqueue_ready = True

    def play(self, offset : int = 0):
        self.offset = offset
        print(f'player.play: playlist empyty {self.playlist.isEmpty()} qmplayer playlist none? {self.qmplayer.playlist()} offset {offset}')
        if not self.playlist.isEmpty():
            if self.qmplayer.playlist() is None:
                self.qmplayer.setMedia(self.playlist)
            self.playlist.setCurrentIndex(offset)
            self.on_track_index_changed(offset)
            self.qmplayer.play()
            print(f'playing playlist at index {self.qmplayer.playlist().currentIndex()} buf {self.qmplayer.bufferStatus()} ')

    def play_by_id(self, track_id : str):
        try:
            print(f'type of track_id: {type(track_id)} track ids {self.ids}')
            idx = self.ids.index(track_id)
            self.play(idx)
        except ValueError:
            print(f'player.play: track id {track_id} not in playlist')

    def stop(self):
        print('stopping')
        self.offset = -1
        if self.qmplayer is not None:
            # let Python recycle the player and thus release the audio device
            self.qmplayer.stop() # stop and setMedia with and empty content
            self.qmplayer.setMedia(QMediaContent()) # to release audio device

    @Slot(float)
    def seek(self, percent):
        to = int(self.qmplayer.duration() * percent)
        print(f'seeking to {percent}, position {to} duration {self.qmplayer.duration()}')
        self.qmplayer.setPosition(to)


    def clear(self):
        self.offset = -1
        if self.qmplayer is not None:
            self.qmplayer.stop()
            self.qmplayer.setMedia(QMediaContent()) # to release audio device
            self.playlist.clear()
            self.ids.clear();

    def trackId(self, index : int):
        print(f'player.trackId type of input index {type(index)} value {index}')
        return self.ids[index] if index < len(self.ids) else str()

    def status(self):
        return self.qmplayer.mediaStatus()

    def enqueueReady(self):
        return self.enqueue_ready

    @Slot(QMediaPlayer.Error)
    def on_player_err(self, e):
        print(f'player.py: player error: {e}')

    @Slot(QMediaPlayer.State)
    def on_state_changed(self, state):
        print(f'player.py: player state changed: {state} sender {self.sender}')

    @Slot(QMediaPlayer.MediaStatus)
    def on_status_changed(self, status):
        print(f'player.py: player status changed SENDER {self.sender()}: \033[1;34m{status}\033[0m player is {self.qmplayer if self.qmplayer is not None else "None"} state \033[1;35m{self.qmplayer.state() if self.qmplayer is not None else "None"}\033[0m media status is \033[1;36m{self.qmplayer.mediaStatus() if self.qmplayer is not None else "None"}\033[0m')
        # check self.qmplayer not none in order not to attempt playing after stop
        # was clicked
#        if (status == QMediaPlayer.LoadedMedia or status == QMediaPlayer.BufferedMedia) and self.qmplayer is not None:
#            print('calling self.qmplayer.\033[1;32mplay\033[0m!')
#            self.qmplayer.play()

    @Slot(int)
    def on_buf_stat_changed(self, percent):
        if percent == 100:
            print(f'player.py: player buffer fill: {percent} sender {self.sender}')

    @Slot(float)
    def on_rate_changed(self, rate):
        print(f'player.py: player rate changed: {rate}')

    @Slot()
    def on_playlist_loaded(self):
        print(f'player.py: playlist loaded. size: {self.playlist.mediaCount()}')

    @Slot(int)
    def on_track_index_changed(self, idx):
        self.track_index_changed.emit(idx)

    @Slot()
    def on_playlist_load_failed(self):
        print(f'player.py: playlist load failed: {self.playlist.errorString()}')


    def _setup_player(self):
        print(f'player._setup_player: allocating new player')
        player = QMediaPlayer(self)
        player.setAudioRole(QAudio.MusicRole);
        player.error.connect(self.on_player_err)
        player.stateChanged.connect(self.on_state_changed)
        player.mediaStatusChanged.connect(self.on_status_changed)
        player.playbackRateChanged.connect(self.on_rate_changed)
        player.bufferStatusChanged.connect(self.on_buf_stat_changed)
        return player

