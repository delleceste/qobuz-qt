# This Python file uses the following encoding: utf-8

from threadable import Threadable
from minim import qobuz as qo

class Login(Threadable):
    def __init__(self, email : str, password : str):
        self.email = email
        self.password = password
        self.session = None

    def getName(self):
        return "Login"

    def run(self):
        self.session = qo.PrivateAPI(flow="password", email=self.email, password=self.password)
        self.name = self.session.get_profile()['firstname']
        self.cred = self.session.get_profile()['credential']['label']
