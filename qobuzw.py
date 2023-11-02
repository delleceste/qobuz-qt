# This Python file uses the following encoding: utf-8
import sys

from PySide2.QtWidgets import QGraphicsView, QGraphicsScene

from PySide2.QtWidgets import QApplication, QMainWindow

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_qobuz import Ui_QobuzW

class QobuzW(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_QobuzW()
        self.ui.setupUi(self)

        self.scene = QGraphicsScene()
        self.ui.gview.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 1200, 1200)



