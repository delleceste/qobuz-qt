# This Python file uses the following encoding: utf-8
from PySide2.QtCore import QObject
from album import Album
from PySide2.QtWidgets import QTextEdit

class TextView(QObject):
    def __init__(self, parent):
        self.album = None
        self.tracks = dict()

    def setTracks(self, te : QTextEdit):
        if self.album is not None:
            self.tracks = self.album.tracks
            html = self._makeHtml(self.album, self.tracks)
            te.setHtml(html)


    def setAlbum(self, album : Album, te : QTextEdit):
        self.album = album
        html = self._makeHtml(album, list())
        te.setHtml(html)


    def _makeHtml(self, album: Album, tracks: dict):
        if album.genre_color is not None:
            c = album.genre_color
        else:
            c = "black"
        md = f'<body style="background-color: {c}; color:white; padding: 10px;">\n'


        md += f'<h3>{album.artist}</h3>'
        if album.artist_img is not None:
            md += f'<img src="{album.artist_img}" alt={album.artist_img}/>\n'
        md += f'<h3>{album.title}</h3>\n'
        md += f'<p>Released {album.released} by {album.label}</p>\n'
        md += f'<p>[{album.max_br}/{album.max_sample_rate}]</p>\n'

        if len(tracks) > 0:
            md += '<ul style="list-style: none;">\n'
            for t in tracks:
                n = t['track_number']
                tit = t['title']
                sec = int(t['duration'])
                m, s = divmod(sec, 60)
                h, m = divmod(m, 60)
                if h > 0:
                    duration = "{0:02d}:{1:02d}:{2:02d}".format(h, m, s)
                else:
                    duration = "{0:02d}:{1:02d}".format(m, s)

                md += f'<li>{n}. {tit} [{duration}]</li>\n'

            md += '</ul>\n\n'

        md += '</body>'
        return md





