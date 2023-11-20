# This Python file uses the following encoding: utf-8
from PySide2.QtCore import QObject, Signal, QThread, Slot

class Threadable(QObject):

    def getName(self):
        return 'empty'
    def run(self):
        return None

    @Slot()
    def on_finished(self):
        pass
    @Slot()
    def on_started(self):
        pass

class QobuzQtThread(QThread):

    finished = Signal(object)

    def __init__(self, parent, threadable):
        QThread.__init__(self, parent)
        self.threadable = threadable
        self.finished.connect(self.threadable.on_finished())

    def run(self):
        self.threadable.run()
        self.finished.emit(self.threadable)
