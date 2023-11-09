
from PySide2.QtCore import QObject, Slot, Signal, QTimer
from PySide2.QtMultimedia import QMediaPlayer, QAudioProbe, QMediaPlaylist, QMediaContent, QAudio
import sys
from PySide2.QtWidgets import QApplication

urls = [
  "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763457&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545247&hmac=341tZuA4Ssedvt-C8cZcctPrqVg"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763458&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545248&hmac=SA7Hkwy9e__EGwdmqihrsKNS6OE"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763459&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545248&hmac=yMmK9X1ZTSe5yVPe_UfUzJktIWk"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763460&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545248&hmac=hKw0mSyzrv7hR4nSdBwDucwV_fc"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763461&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545248&hmac=tsNkz9C0y92QvmFpIeIiTdl1HwE"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763462&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545248&hmac=XuL_IbplraMhg0-70LRur1p6YD8"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763463&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545249&hmac=pIBb3KGz8FqrmsJdLvh5paDQWdY"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763464&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545249&hmac=3v6r-7F4VwB-8cx_OnnFuG3TOcY"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763465&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545249&hmac=NB9el5LcgIND9211YJsme4F4V-Y"
, "https://streaming-qobuz-std.akamaized.net/file?uid=591901&eid=193763466&fmt=27&profile=raw&app_id=950096963&cid=1277411&etsp=1699545249&hmac=hW1917OipABq1yGncE9lcKLaySU"
]

class Player(QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        playlist = QMediaPlaylist()
        media_content = []
        for url in urls:
            print(f'url: {len(media_content)+1} \033[0;32m{url}\033[0m')
            media_content.append(QMediaContent(url))
        self.player = self._setup_player()
        playlist.addMedia(media_content)
        self.player.setMedia(QMediaContent(playlist))
        #self.player.setPlaylist(playlist)


        ### change 0 with > 0 and it (seems to) work correctly
        playlist.setCurrentIndex(0)
        print(f'player has playlist size {self.player.playlist().mediaCount()}... buf fill {self.player.bufferStatus()}')

        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(self.play)
        interval = 6000
        print('starting timer: will play in {interval} ms')
        t.setInterval(interval)
        t.start()

    def _setup_player(self):
        player = QMediaPlayer(self)
        player.setAudioRole(QAudio.MusicRole);
        player.error.connect(self.on_player_err)
        player.stateChanged.connect(self.on_state_changed)
        player.mediaStatusChanged.connect(self.on_status_changed)
        player.bufferStatusChanged.connect(self.on_buf_stat_changed)
        return player

    @Slot()
    def play(self):
        print(f'playing playlist size {self.player.playlist().mediaCount()}... buf fill {self.player.bufferStatus()}')
        self.player.play()
        print(f'playing playlist at index {self.player.playlist().currentIndex()}')


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

    @Slot()
    def on_playlist_loaded(self):
        print(f'player.py: playlist loaded. size: {self.playlist.mediaCount()}')

    @Slot(int)
    def on_track_changed(self, idx):
        self.track_changed.emit(idx)

    @Slot()
    def on_playlist_load_failed(self):
        print(f'player.py: playlist load failed: {self.playlist.errorString()}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = Player()
    sys.exit(app.exec_())
