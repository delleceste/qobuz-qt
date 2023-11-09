# This Python file uses the following encoding: utf-8

class Album:
    def __init__(self, minim_album: dict):
        self.malbum = minim_album
        self.spix = self.lpix = self.thpix = None # small, large thumbnail pixmaps
        self.artwork_fetch = False
        ma = minim_album
        self.title = ma['title']
        self.artist =  ma['artist']['name']
        self.artist_img = ma['artist']['image']
        self.label = ma['label']['name']
        self.genre = ma['genre']['name']
        self.genre_color = ma['genre']['color']
        self.channels = ma['maximum_channel_count']
        self.max_sample_rate = ma['maximum_sampling_rate']
        self.max_br = ma['maximum_bit_depth']
        self.released = ma['release_date_original']
