# This Python file uses the following encoding: utf-8

from threadable import Threadable
from enum import Enum
from minim import qobuz
import json
from PySide2.QtCore import  Slot

class SearchResult(Enum):
    Album = 0
    Artist = 1
    Label = 2

class Search(Threadable):
    def __init__(self, session : qobuz.PrivateAPI, limit = 10, offset = 0 ):
        self.session = session
        self.keyword = None;
        self.limit = limit
        self.offset = offset
        self.partial = 0
        self.total = 0
        self.results = []
        self.result_type = SearchResult.Album
        self.running = False

    @Slot()
    def on_started(self):
        self.running = True
    @Slot()
    def on_finished(self):
        self.running = False

    def nextResults(self):
        if not self.running:
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
        if self.total == 0 or self.offset < self.total:
            search_results = self.session.search(self.keyword, limit=self.limit, offset=self.offset, strict=False)
            self.total = int(search_results["albums"]["total"])
            print(f'results size {len(search_results["albums"]["items"])} offset {self.offset} limit {self.limit} total {self.total}')
            self.partial += len(search_results)

            for al in search_results["albums"]["items"]:
                json_al = al;
                self.results.append(json_al)
                #self.results.append(qo.Album(al['id'], authenticate=True))
        else:
            print(f'\033[1;33mreached total in results: {self.total}')

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

