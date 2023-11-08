# This Python file uses the following encoding: utf-8

class Album:
    def __init__(self, minim_album: dict):
        self.malbum = minim_album
        self.spix = self.lpix = self.thpix = None # small, large thumbnail pixmaps
        self.artwork_fetch = False
