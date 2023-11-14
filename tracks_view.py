# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import Qt
from datetime import timedelta
from enum import Enum
from album import Album


class UserRoles(Enum):
    Metadata = Qt.UserRole
    Album = Qt.UserRole + 1

class TracksView:

    def __init__(self):
        pass

    def add(self, w : QTreeWidget, tracks : dict, album : Album):
        icon = album.thpix.scaledToHeight(album.thpix.height() * 0.65);
        smallicon = icon # icon.scaledToHeight(album.thpix.height() * 0.5)
        cnt = 0
        ids = []
        for t in tracks:
            n = t['track_number']
            tit = t['title']
            ids.append(t['id'])
            sec = int(t['duration'])
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            if h > 0:
                duration = "{0:02d}:{1:02d}:{2:02d}".format(h, m, s)
            else:
                duration = "{0:02d}:{1:02d}".format(m, s)
            work = t['work']

            i = QTreeWidgetItem(w, [str(n), tit, duration ])
            i.setToolTip(1, work)
            i.setData(0, UserRoles.Metadata.value, t)
            i.setData(0, UserRoles.Album.value, album)
            i.setData(0, Qt.DecorationRole, smallicon if cnt > 0 else icon)
            w.insertTopLevelItem(int(n) - 1, i)
            cnt += 1

        return ids

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

    def activeAlbum(self, w : QTreeWidget):
        if w.topLevelItemCount() == 0:
            return None
        selected = w.selectedItems()
        item = selected[0] if len(selected) > 0 else w.topLevelItem(0)
        return item.data(0, UserRoles.Album.value)

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





