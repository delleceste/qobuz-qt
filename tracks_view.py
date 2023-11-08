# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import Qt
from datetime import timedelta
from enum import Enum

class UserRoles(Enum):
    Metadata = Qt.UserRole
    AlbumId = Qt.UserRole + 1

class TracksView:

    def __init__(self):
        pass

    def set(self, w : QTreeWidget, tracks : dict, album_id : str):
        w.clear()
        for t in tracks:
            n = t['track_number']
            tit = t['title']
            id = t['id']
            sec = int(t['duration'])
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            if h > 0:
                duration = "{0:02d}:{1:02d}:{2:02d}".format(h, m, s)
            else:
                duration = "{0:02d}:{1:02d}".format(m, s)
            release = t['work']

            i = QTreeWidgetItem(w, [str(n), tit, duration ])
            i.setData(0, UserRoles.Metadata.value, t)
            i.setData(0, UserRoles.AlbumId.value, album_id)
            w.insertTopLevelItem(int(n) - 1, i)

    def getIds(self, w : QTreeWidget):
        ids = []
        for i in range(0, w.topLevelItemCount()):
            it = w.topLevelItem(i)
            ids.append( int(it.data(0, Qt.UserRole)['id']))
        return ids

    def index(self, w: QTreeWidget, it : QTreeWidgetItem):
        return w.indexOfTopLevelItem(it)

    def clear(self, w: QTreeWidget):
        w.clear()

    def select(self, w: QTreeWidget, idx : int):
        self.deselect(w)
        if idx < w.topLevelItemCount():
            i = w.topLevelItem(idx)
            i.setSelected(True)

    def deselect(self, w : QTreeWidget):
        for i in range(0, w.topLevelItemCount()) :
            it = w.topLevelItem(i)
            if it.isSelected():
                it.setSelected(False)





