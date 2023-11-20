# This Python file uses the following encoding: utf-8

from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from datetime import timedelta
from enum import Enum
from album import Album
from qobuzw import CurrentView


class UserRoles(Enum):
    Metadata = Qt.UserRole
    Album = Qt.UserRole + 1
    Enqueued = Album + 1

class TracksView:

    def __init__(self):
        pass

    def add(self, w : QTreeWidget, tracks : dict, album : Album, select : bool = True):
        icon = album.thpix.scaledToHeight(album.thpix.height() * 0.65);
        smallicon = icon # icon.scaledToHeight(album.thpix.height() * 0.5)
        cnt = 0
        ids = []
        for t in tracks:
            i = self.findItem(w, t['id'])
            ids.append(t['id'])
            if i is None:
                n = t['track_number']
                tit = t['title']
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
                i.setSelected(select)
                w.insertTopLevelItem(int(n) - 1, i)

                i.setData(0, UserRoles.Enqueued.value, False)

            cnt += 1

        return ids

    def markSelectedEnqueued(self, w : QTreeWidget):
        f = w.font()
        f.setBold(True)
        ids = []
        for i in range(0, w.topLevelItemCount()):
            item = w.topLevelItem(i)
            if item.isSelected():
                track = item.data(0, UserRoles.Metadata.value) # track: dict
                item.setData(0, UserRoles.Enqueued.value, True)
                ids.append(track['id'])
                for col in range(0, item.columnCount()):
                    item.setFont(col, f)
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

    def enqueuedCnt(self, w : QTreeWidget):
        return len(self.getEnqueuedIds(w))

    def getEnqueuedIds(self, w : QTreeWidget):
        ids = []
        for i in range(0, w.topLevelItemCount()) :
            it = w.topLevelItem(i)
            if it.data(0, UserRoles.Enqueued.value) == True:
                track = it.data(0, UserRoles.Metadata.value)
                ids.append(track['id'])
        return ids

    def getNotEnqueuedIds(self, w : QTreeWidget):
        ids = []
        for i in range(0, w.topLevelItemCount()) :
            it = w.topLevelItem(i)
            if it.data(0, UserRoles.Enqueued.value) == False:
                track = it.data(0, UserRoles.Metadata.value)
                ids.append(track['id'])
        return ids

    def remove(self, w : QTreeWidget, track_ids : list):
        rem = []
        for i in range(0, w.topLevelItemCount()) :
            it = w.topLevelItem(i)
            track = it.data(0, UserRoles.Metadata.value) # track: dict
            if track_ids.count(track['id']) > 0:
                rem.append(it)
        for item in rem:
            w.takeTopLevelItem(w.indexOfTopLevelItem(item))

    def findItem(self, w : QTreeWidget, track_id : str):
        for i in range(0, w.topLevelItemCount()) :
            it = w.topLevelItem(i)
            track = it.data(0, UserRoles.Metadata.value) # track: dict
            if track['id'] == track_id:
                return it
        return None

    def mainViewChanged(self, w : QTreeWidget, view : CurrentView):
#        f = w.font()
#        fb = QFont(f)
#        fb = f.setBold(True)
        rem = []
        for i in range(0, w.topLevelItemCount()) :
            it = w.topLevelItem(i)
            enqueued = (it.data(0, UserRoles.Enqueued.value) == True)
#            for col in range(0, it.columnCount()):
#                it.setFont(col, fb if view == CurrentView.List and enqueued else f)
            # remove items not enqueued when switching to detail view
            if view == CurrentView.Detail and not enqueued:
                rem.append(it)
        for it in rem:
            w.takeTopLevelItem(w.indexOfTopLevelItem(it))



