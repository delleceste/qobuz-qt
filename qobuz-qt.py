# This Python file uses the following encoding: utf-8
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QGraphicsItem, QGraphicsPixmapItem
from PySide2.QtCore import QObject, Slot, Signal, QThread, QRect, QPoint, QPointF
from PySide2.QtGui import QPixmap
import sys
from enum import Enum
from qobuzw import QobuzW
import aiohttp
from PIL import Image
from io import BytesIO
import asyncio
import math

from minim import qobuz as qo

class Threadable(QObject):

    def getName(self):
        return 'empty'
    def run(self):
        return None

class Login(Threadable):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.session = None

    def getName(self):
        return "Login"

    def run(self):
        self.session = qo.PrivateAPI(email=self.email, password=self.password ,authenticate=True)
        self.name = self.session.get_me()['firstname']
        self.cred = self.session.get_me()['credential']['label']

class SearchResult(Enum):
    Album = 0
    Artist = 1
    Label = 2

class Search(Threadable):
    def __init__(self, session, keyword, type = SearchResult.Album):
        self.keyword = keyword;
        self.session = session
        self.results = []
        self.result_type = type

    def getName(self):
        return "Search"

    def run(self):
        print(f'performing search with keyword {self.keyword}')
        search_results = self.session.search(self.keyword, "ReleaseName", strict=True)
        print(f'results size {len(search_results["albums"]["items"])}')
        for al in search_results["albums"]["items"]:
            json_al = al;
            self.results.append(json_al)
            print(f'JSON album {al} ')
            #self.results.append(qo.Album(al['id'], authenticate=True))



class QobuzQtThread(QThread):

    finished = Signal(object)

    def __init__(self, parent, threadable):
        QtCore.QThread.__init__(self, parent)
        self.threadable = threadable

    def run(self):
        self.threadable.run()
        self.finished.emit(self.threadable)


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

        # connections
        self.win.ui.pbSearch.setDisabled(True)
        self.win.ui.pbSearch.clicked.connect(self.search)


    @Slot(Threadable)
    def on_login(self, login):
        msg = f'logged in as {login.name}'
        self.win.statusBar().showMessage(msg)
        if login.session != None:
            self.session = login.session
            self.win.ui.pbSearch.setEnabled(True)
        pass

    @Slot()
    def search(self):
        
        txt = self.win.ui.leSearch.text()
        th = QobuzQtThread(self, Search(self.session, txt))
        th.finished.connect(self.on_search_results)
        th.start()

    @Slot()
    def on_search_results(self, search):
        urls = []
        if search.result_type == SearchResult.Album:
            for album in search.results:
                # urls.append( album['image']['thumbnail'])
                urls.append( album['image']['small'])

        asyncio.run(self._fetch_img(urls))


    async def _fetch_img(self, urls):
        ssize = self.win.scene.sceneRect().size()
        imgcnt = len(urls)
        rows = math.sqrt(imgcnt)
        maxw = 0.0
        x = 10.0
        y = 10.0
        cnt = 0
        async with aiohttp.ClientSession() as session:
            for url in urls:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f'wating for url {url}')
                        image_bytes = await response.read()
                        # Convert image to black and white
                        pix = QPixmap()
                        pix.loadFromData(image_bytes)
                        pixi = self.win.scene.addPixmap(pix)
                        pixi.setFlag(QGraphicsItem.ItemIsMovable, True)
                        pixi.setFlag(QGraphicsItem.ItemIsSelectable, True)
                        size = pixi.boundingRect().size()
                        pixi.setPos(x, y);
                        print(f'scene size {ssize} item siz {size} pos {pixi.pos()}')
                        x = x + 1.1 * size.width()
                        if maxw < x:
                            maxw = x
                        r = self.win.scene.sceneRect()
                        cnt += 1
                        if cnt >= rows:
                            cnt = 0
                            x = 10.0
                            y = y + 1.1 * size.height()
        r.setWidth(maxw);
        r.setHeight(y)
        self.win.scene.setSceneRect(r)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qoqt = QobuzQt()
    sys.exit(app.exec_())
