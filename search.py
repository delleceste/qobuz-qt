# This Python file uses the following encoding: utf-8

from threadable import Threadable, QobuzQtThread
from enum import Enum
from minim import qobuz
from album import Album
import json
from PySide2.QtCore import  Slot, Signal, QObject

class SearchResult(Enum):
    Album = 0
    Artist = 1
    Label = 2

class Search(Threadable):
    search_complete = Signal()

    def __init__(self, session : qobuz.PrivateAPI, parent : QObject, limit = 10, offset = 0 ):
        Threadable.__init__(self, parent)
        self.session = session
        self.keyword = None;
        self.limit = limit
        self.offset = offset
        self.partial = 0
        self.total = 0
        self.results = []
        self.result_type = SearchResult.Album
        self.running = False
        self.thcnt = 0

    @Slot()
    def on_finished(self, threadable : Threadable):
        print(f'threads {self.thcnt} search.on_finished: resetting running to \033[1;32mFalse\033[0m')
        self.running = False
        self.search_complete.emit()
        self.thcnt -= 1

    @Slot()
    def search(self):
        print(f'threads {self.thcnt} search.search: setting running to \033[1;32mTrue\033[0m')
        self.results = []
        self.running = True
        th = QobuzQtThread(self, self)
        th.finished.connect(self.on_finished)
        th.start()
        self.thcnt += 1

    def clearResults(self):
        self.results = []

    def nextResults(self):
        self.offset += 10

    def getName(self):
        return "Search"

    def setKeyword(self, txt):
        self.results.clear()
        if self.keyword != txt:
            self.keyword = txt
            self.offset = 0
            self.total = 0

    def setType(self, type = SearchResult.Album):
        self.result_type = type;

    def run(self):
        print(f'search.run() \033[1;32menter\033[0m... {self.keyword} total {self.total} offset {self.offset}')
        if self.total == 0 or self.offset < self.total:
            search_results = self.session.search(self.keyword, limit=self.limit, offset=self.offset, strict=False)
            self.total = int(search_results["albums"]["total"])
            print(f'results size {len(search_results["albums"]["items"])} offset {self.offset} limit {self.limit} total {self.total}')

            for minim_album in search_results["albums"]["items"]:
                self.results.append(Album(minim_album))
        else:
            print(f'\033[1;33mreached total in results: {self.total}')
        print(f'search.run() \033[1;35mexit\033[0m... {self.keyword} total {self.total} offset {self.offset}')

class AlbumFetch(Threadable):
    def __init__(self, session : qobuz.PrivateAPI, id: str):
        self.id = id
        self.session = session
        self.tracks = []

    def getName(self):
        return "AlbumFetch"

    def run(self):
        album = self.session.get_album(self.id)
        for track in album["tracks"]["items"]:
            self.tracks.append(track)

    def getTracks(self) -> list:
        return self.tracks

