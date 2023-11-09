# This Python file uses the following encoding: utf-8
from PySide2.QtCore import QObject
from album import Album
from PySide2.QtWidgets import QTextEdit

class TextView(QObject):
    def __init__(self, parent):
        pass

    def set(self, album : Album, te : QTextEdit):
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

        md += '</body>'
        te.setHtml(md)








