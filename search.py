# This Python file uses the following encoding: utf-8

from threadable import Threadable
from enum import Enum
from minim import qobuz

class SearchResult(Enum):
    Album = 0
    Artist = 1
    Label = 2

class Search(Threadable):
    def __init__(self, session : qobuz.PrivateAPI ):
        self.session = session
        self.keyword = None;
        self.results = []
        self.result_type = SearchResult.Album

    def getName(self):
        return "Search"

    def setKeyword(self, txt):
        self.keyword = txt

    def setType(self, type = SearchResult.Album):
        self.result_type = type;

    def run(self):
        print(f'performing search with keyword {self.keyword}')
        search_results = self.session.search(self.keyword,  strict=True)
        print(f'results size {len(search_results["albums"]["items"])}')
        for al in search_results["albums"]["items"]:
            json_al = al;
            self.results.append(json_al)
            print(f'JSON album {al} ')
            #self.results.append(qo.Album(al['id'], authenticate=True))

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

