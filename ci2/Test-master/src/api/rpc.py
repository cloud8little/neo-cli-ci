# -*- coding:utf-8 -*-
import copy
import json
import sys

sys.path.append('..')
sys.path.append('../src')

from utils.taskdata import Task
from utils.taskrunner import TaskRunner
from utils.error import RPCError


class RPCApi:
    REQUEST_BODY = {
        "jsonrpc": "2.0",
        "method": "",
        "params": [],
        "id": 1
    }

    def __init__(self):
        self.currentnode = 0

    def setnode(self, node):
        self.currentnode = node

    def num2str(self, num):
        if num is not None and (isinstance(num, int) or isinstance(num, float)):
            return "num#!#start-%.20f-num#!#end" % num
        else:
            return num

    def simplerun(self, rpcmethod, params, jsonrpc='2.0', id=1):
        request = copy.copy(RPCApi.REQUEST_BODY)
        request["method"] = rpcmethod
        request["params"] = params
        request["jsonrpc"] = jsonrpc
        request["id"] = id

        ijson = {}
        ijson["TYPE"] = "RPC"
        ijson["NODE_INDEX"] = int(self.currentnode)
        ijson["REQUEST"] = request
        ijson["RESPONSE"] = None
        task = Task(name=rpcmethod, ijson=ijson)
        (result, response) = TaskRunner.run_single_task(task, True, False)
        if response is None:
            raise Exception("rpc connect error")
        if response["jsonrpc"] != jsonrpc:
            raise Exception("rpc connect jsonrpc not valid: " + response["jsonrpc"])
        if response["id"] != id:
            raise Exception("rpc connect id not valid: " + str(response["id"]))
        if "error" in response.keys():
            raise RPCError(json.dumps(response["error"]))
        return response["result"]

    def dumpprivkey(self, address=None):
        params = []
        if address != "empty":
            params.append(address)
        return self.simplerun("dumpprivkey", params)

    def getaccountstate(self, address=None):
        params = []
        if address != "empty":
            params.append(address)
        return self.simplerun("getaccountstate", params)

    def getassetstate(self, asset_id=None):
        params = []
        if asset_id != "empty":
            params.append(asset_id)
        return self.simplerun("getassetstate", params)

    def getbalance(self, asset_id=None):
        params = []
        if asset_id != "empty":
            params.append(asset_id)
        return self.simplerun("getbalance", params)

    def getbestblockhash(self):
        return self.simplerun("getbestblockhash", [])

    def getblock(self, hash=None, verbose=None):
        params = []
        if hash != "empty":
            params.append(hash)
        if verbose != "empty":
            params.append(verbose)
        return self.simplerun("getblock", params)

    def getblockcount(self):
        return self.simplerun("getblockcount", [])

    def getblockheader(self, hash=None, verbose=None):
        params = []
        if hash != "empty":
            params.append(hash)
        if verbose != "empty":
            params.append(verbose)
        return self.simplerun("getblockheader", params)

    def getblockhash(self, index=None):
        params = []
        if index != "empty":
            params.append(index)
        return self.simplerun("getblockhash", params)

    def getblocksysfee(self, index=None):
        params = []
        if index != "empty":
            params.append(index)
        return self.simplerun("getblocksysfee", params)

    def getconnectioncount(self):
        return self.simplerun("getconnectioncount", [])

    def getcontractstate(self, script_hash=None):
        params = []
        if script_hash != "empty":
            params.append(script_hash)
        return self.simplerun("getcontractstate", params)

    def getnewaddress(self):
        params = []
        return self.simplerun("getnewaddress", [])

    def getrawmempool(self):
        params = []
        return self.simplerun("getrawmempool", [])

    def getrawtransaction(self, txid=None, verbose=None):
        params = []
        if txid != "empty":
            params.append(txid)
        if verbose != "empty":
            params.append(verbose)
        return self.simplerun("getrawtransaction", params)

    def getstorage(self, script_hash=None, key=None):
        params = []
        if script_hash != "empty":
            params.append(script_hash)
        if key != "empty":
            params.append(key)
        return self.simplerun("getstorage", params)

    def gettxout(self, txid=None, n=0):
        params = []
        if txid != "empty":
            params.append(txid)
        if n != "empty":
            params.append(n)
        return self.simplerun("gettxout", params)

    def getpeers(self):
        params = []
        return self.simplerun("getpeers", [])

    def getvalidators(self):
        params = []
        return self.simplerun("getvalidators", [])

    def getversion(self):
        params = []
        return self.simplerun("getversion", [])

    def getwalletheight(self):
        params = []
        return self.simplerun("getwalletheight", [])

    def invoke(self, scripthash=None, params=None):
        iparams = []
        if scripthash != "empty":
            iparams.append(scripthash)
        if params != "empty":
            iparams.append(params)
        return self.simplerun("invoke", iparams)

    def invokefunction(self, scripthash=None, operation=None, params=None):
        iparams = []
        if scripthash != "empty":
            iparams.append(scripthash)
        if operation != "empty":
            iparams.append(operation)
        if params != "empty":
            iparams.append(params)
        return self.simplerun("invokefunction", iparams)

    def invokescript(self, script=None):
        params = []
        if script != "empty":
            params.append(script)
        return self.simplerun("invokescript", params)

    def listaddress(self):
        params = []
        return self.simplerun("listaddress", [])

    def sendfrom(self, asset_id=None, _from=None, to=None, value=None, fee=None, change_address=None):
        params = []
        if asset_id != "empty":
            params.append(asset_id)
        if _from != "empty":
            params.append(_from)
        if to != "empty":
            params.append(to)
        if value != "empty":
            params.append(self.num2str(value))
        if fee != "empty":
            params.append(self.num2str(fee))
        if change_address != "empty":
            params.append(change_address)
        return self.simplerun("sendfrom", params)

    def sendrawtransaction(self, hex=None):
        params = []
        if hex != "empty":
            params.append(hex)
        return self.simplerun("sendrawtransaction", params)

    def sendtoaddress(self, asset_id=None, address=None, value=None, fee=None, change_address=None):
        params = []
        if asset_id != "empty":
            params.append(asset_id)
        if address != "empty":
            params.append(address)
        if value != "empty":
            params.append(self.num2str(value))
        if fee != "empty":
            params.append(self.num2str(fee))
        if change_address != "empty":
            params.append(change_address)
        return self.simplerun("sendtoaddress", params)

    def sendmany(self, params=None, fee=None, change_address=None):
        iparams = []
        if params != "empty":
            iparams.append(params)
        if fee != "empty":
            iparams.append(self.num2str(fee))
        if change_address != "empty":
            iparams.append(change_address)
        return self.simplerun("sendmany", iparams)

    def validateaddress(self, address=None):
        params = []
        if address != "empty":
            params.append(address)
        return self.simplerun("validateaddress", params)
