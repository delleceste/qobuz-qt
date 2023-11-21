# This Python file uses the following encoding: utf-8
from PySide2.QtCore import QObject, Signal, QThread, Slot

class Threadable(QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)

    def getName(self):
        return 'empty'
    def run(self):
        return None

class QobuzQtThread(QThread):

    finished = Signal(object)

    def __init__(self, parent, threadable):
        QThread.__init__(self, parent)
        self.threadable = threadable

    def run(self):
        self.threadable.run()
        self.finished.emit(self.threadable)
