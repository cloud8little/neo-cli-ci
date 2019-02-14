# -*- coding: utf-8 -*-
import json
import os

from neo.wallet import Wallet


class Config():
    realdir = os.path.dirname(os.path.realpath(__file__))
    UTILS_PATH = realdir
    UTILS_PATH = UTILS_PATH.replace("\\\\", "/")
    UTILS_PATH = UTILS_PATH.replace("\\", "/")
    ROOT_PATH = UTILS_PATH.replace("/utils", "")
    print(ROOT_PATH)
    cfg_file = open(ROOT_PATH + "/config.json", "rb")
    cfg_json = json.loads(cfg_file.read().decode("utf-8"))
    cfg_file.close()

    ERR_CODE = {
        0: "SUCCESS",
        54001: "RPC CONNECT ERROR",
        54005: "SERVICE TOOL RPC CONNECT ERROR"
    }

    TOOLS_PATH = ROOT_PATH + "/" + "tools"
    UTILS_PATH = ROOT_PATH + "/" + "utils"
    TESTS_PATH = ROOT_PATH + "/" + "test"
    RESOURCE_PATH = ROOT_PATH + "/resource"
    WALLET_PATH = RESOURCE_PATH + "/wallet"
    LOG_PATH = ROOT_PATH + "/logs"

    TEST_SERVICE_PORT = 23635

    NODES = cfg_json["NODES"]
    for node in NODES:
        node["wallet"] = Wallet(path=WALLET_PATH + "/" + node["walletname"])
    RPC_HEADERS = {'content-type': 'application/json'}
    GEN_BLOCK_TIMEOUT = 30
    WALLETNAMES = cfg_json["WALLETS"]
