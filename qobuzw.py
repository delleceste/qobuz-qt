# This Python file uses the following encoding: utf-8
import sys

from PySide2.QtWidgets import QGraphicsView, QGraphicsScene
from PySide2.QtWidgets import QApplication, QMainWindow, QHeaderView

from list_scene import ListScene
from player_scene import PlayerScene

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_qobuz import Ui_QobuzW
from enum import Enum

class CurrentView(Enum):
    List = 0
    Detail = 1

class QobuzW(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_QobuzW()
        self.ui.setupUi(self)

        self.scene = ListScene(self)
        self.ui.gview.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 1200, 1200)

        # single album scene
        self.player_scene = PlayerScene(self)
        self.player_scene.setSceneRect(self.scene.sceneRect())
        self.ui.gview2.setScene(self.player_scene)

        self.ui.stackW.setCurrentIndex(CurrentView.List.value)

        for i in range(0, self.ui.tw.header().count()):
            self.ui.tw.header().setSectionResizeMode(i, QHeaderView.ResizeToContents)


