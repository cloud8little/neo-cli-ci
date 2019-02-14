import json


# Wallet info
class Wallet:
    def __init__(self, path=""):
        self.path = ""
        if path != "":
            self.path = path
        file = open(path, "rb")
        self.ijson = json.loads(file.read().decode("utf-8"))
        file.close()

    def path(self):
        return self.path

    def name(self):
        return self.ijson["name"]

    def version(self):
        return self.ijson["version"]

    def scrypt_n(self):
        return self.ijson["scrypt"]["n"]

    def scrypt_r(self):
        return self.ijson["scrypt"]["r"]

    def scrypt_p(self):
        return self.ijson["scrypt"]["p"]

    def account(self, index=0):
        if len(self.ijson["accounts"]) <= index:
            raise Exception("account index out of range(" + index + ")")
        return Account(self.ijson["accounts"][index])


# Account info
class Account:
    def __init__(self, jsonobj):
        self.ijson = jsonobj

    def address(self):
        return self.ijson["address"]

    def label(self):
        return self.ijson["label"]

    def isDefault(self):
        return self.ijson["isDefault"]

    def lock(self):
        return self.ijson["lock"]

    def key(self):
        return self.ijson["key"]

    def contract(self):
        return self.ijson["contract"]
