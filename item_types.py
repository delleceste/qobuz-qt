# This Python file uses the following encoding: utf-8

from enum import Enum
from PySide2.QtWidgets import QGraphicsItem

class ItemTypes(Enum):
    Art = QGraphicsItem.UserType + 2
    AlbumPlay = Art + 1
    Track = AlbumPlay + 1
