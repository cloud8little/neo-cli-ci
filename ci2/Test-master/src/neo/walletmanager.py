from neo.wallet import Wallet
from utils.config import Config


class WalletManager:
    def __init__(self):
        pass

    def wallet(self, index=0):
        if index >= len(Config.WALLETNAMES):
            raise Exception("Wallet out of range(" + index + ")")
        return Wallet(Config.WALLET_PATH + "/" + Config.WALLETNAMES[index])
