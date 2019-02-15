# -*- coding:utf-8 -*-
import copy
import json
import sys 

sys.path.append('..')
sys.path.append('../src')

from utils.taskdata import Task
from utils.taskrunner import TaskRunner
from utils.error import RPCError


# import utils.config
class CLIRPCApi:
    # version   显示当前软件的版本
    REQUEST_BODY = {
        "jsonrpc": "2.0",
        "method": "",
        "params": {},
        "id": 1
    }

    def __init__(self):
        self.currentnode = 0

    def setnode(self, node):
        self.currentnode = node

    def simplerun(self, rpcmethod, params, jsonrpc='2.0', id=1):
        request = copy.copy(CLIRPCApi.REQUEST_BODY)
        request["method"] = rpcmethod
        request["params"] = params
        request["jsonrpc"] = jsonrpc
        request["id"] = id

        ijson = {}
        ijson["TYPE"] = "ST"
        ijson["NODE_INDEX"] = int(self.currentnode)
        ijson["REQUEST"] = request
        ijson["RESPONSE"] = None
        task = Task(name=rpcmethod, ijson=ijson)
        (result, response) = TaskRunner.run_single_task(task, judge=True, process_log=False)
        if response is None:
            raise Exception("cli rpc connect error")
        if response["jsonrpc"] != jsonrpc:
            raise Exception("cli rpc connect jsonrpc not valid: " + response["jsonrpc"])
        if response["id"] != id:
            raise Exception("cli rpc connect id not valid: " + str(response["id"]))
        if "error" in response.keys() and response["error"] != 0:
            raise RPCError(json.dumps(response["error"]))
        return response["result"]

    def init(self, scriptname, neopath):
        # step index
        return self.simplerun("cli_init", {"scriptname": scriptname, "neopath": neopath})

    def readmsg(self):
        return self.simplerun("cli_readmsg", {})

    def clearmsg(self):
        return self.simplerun("cli_clearmsg", {})

    def terminate(self):
        return self.simplerun("cli_terminate", {})

    def exec(self, exitatlast=True):
        return self.simplerun("cli_exec", {"exitatlast": exitatlast})

    def version(self, exceptfunc=None):
        return self.simplerun("cli_version", {"exceptfunc": exceptfunc})

    # help  帮助菜单
    def help(self, exceptfunc=None):
        return self.simplerun("cli_help", {"exceptfunc": exceptfunc})

    def wait(self, times=1):
        return self.simplerun("cli_wait", {"times": times})

    # clear 清除屏幕
    def clear(self):
        return self.simplerun("cli_clear", {})

    # exit  退出程序
    def exit(self):
        return self.simplerun("cli_exit", {})

    # create wallet <path>  创建钱包文件
    def create_wallet(self, filepath, password, exceptfunc=None):
        return self.simplerun("cli_create_wallet", {"filepath": filepath, "password": password, "exceptfunc": exceptfunc})

    # open wallet <path>    打开钱包文件
    def open_wallet(self, filepath, password, exceptfunc=None):
        return self.simplerun("cli_open_wallet", {"filepath": filepath, "password": password, "exceptfunc": exceptfunc})

    # upgrade wallet <path> 升级旧版钱包文件
    def upgrade_wallet(self, filepath, exceptfunc=None):
        return self.simplerun("cli_upgrade_wallet", {"filepath": filepath, "exceptfunc": exceptfunc})

    # rebuild index 重建钱包索引  需要打开钱包
    # 重建钱包索引。为什么要重建钱包索引，重建钱包索引有什么用？
    # 钱包中有一个字段，记录了当前钱包同步的区块高度，每新增加一个区块，钱包客户端就会同步区块，
    # 将钱包中的资产和交易更新。假设当前记录的区块高度为 100，然后你执行了 import key 命令导入了私钥，
    # 这时钱包仍然是从区块高度为 100开始计算你的资产。如果导入的地址在区块高度小于 100的时候有一些交易，
    # 这些交易和对应的资产将不会体现在钱包中，所以要重建钱包索引，强制让钱包从区块高度为0开始计算你的资产。
    # 假如由于种种原因，钱包中的某笔交易未确认，这时资产已经从钱包中扣除，
    # 但并未经过整个区块链网络的确认。如果想删掉这笔未确认的交易使钱包中的资产正常显示也需要重建钱包索引。
    # 新创建的钱包不用重建钱包索引，只有要导入私钥或者钱包中资产显示异常时才需要重建钱包索引。
    def rebuild_index(self, exceptfunc=None):
        return self.simplerun("cli_rebuild_index", {"exceptfunc": exceptfunc})

    # list address  列出钱包中的所有账户  需要打开钱包
    def list_address(self, exceptfunc=None):
        return self.simplerun("cli_list_address", {"exceptfunc": exceptfunc})

    # list asset    列出钱包中的所有资产  需要打开钱包
    def list_asset(self, exceptfunc=None):
        return self.simplerun("cli_list_asset", {"exceptfunc": exceptfunc})

    # list key  列出钱包中的所有公钥  需要打开钱包
    def list_key(self, exceptfunc=None):
        return self.simplerun("cli_list_key", {"exceptfunc": exceptfunc})

    # show utxo [id|alias]  列出钱包中指定资产的 UTXO 需要打开钱包
    # examples:
    # 1. neo>show utxo neo
    #   8674c38082e59455cf35cee94a5a1f39f73b617b3093859aa199c756f7900f1f:2
    #   total: 1 UTXOs
    # 2. neo>show utxo gas
    #   8674c38082e59455cf35cee94a5a1f39f73b617b3093859aa199c756f7900f1f:1
    #   total: 1 UTXOs
    # 3. neo>show utxo 025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4
    #   8674c38082e59455cf35cee94a5a1f39f73b617b3093859aa199c756f7900f1f:0
    #   total: 1 UTXOs
    def show_utxo(self, id_alias=None, exceptfunc=None):
        return self.simplerun("cli_show_utxo", {"id_alias": id_alias, "exceptfunc": exceptfunc})

    # show gas  列出钱包中的所有可提取及不可提取的 GAS   需要打开钱包
    # examples:
    # unavailable: 133.024
    # available: 10.123
    def show_gas(self, exceptfunc=None):
        return self.simplerun("cli_show_gas", {"exceptfunc": exceptfunc})

    # claim gas 提取钱包中的所有可提取的 GAS    需要打开钱包
    def claim_gas(self, exceptfunc=None):
        return self.simplerun("cli_claim_gas", {"exceptfunc": exceptfunc})

    # create address [n=1]  创建地址 / 批量创建地址   需要打开钱包
    def create_address(self, n=None, exceptfunc=None):
        return self.simplerun("cli_create_address", {"n": n, "exceptfunc": exceptfunc})

    # import key <wif|path> 导入私钥 / 批量导入私钥   需要打开钱包
    # examples:
    # import key L4zRFphDJpLzXZzYrYKvUoz1LkhZprS5pTYywFqTJT2EcmWPPpPH
    # import key key.txt
    def import_key(self, wif_path, exceptfunc=None):
        return self.simplerun("cli_import_key", {"wif_path": wif_path, "exceptfunc": exceptfunc})

    # export key [address] [path]   导出私钥    需要打开钱包
    # examples:
    # export key
    # export key AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b
    # export key key.txt
    # export key AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b key.txt
    def export_key(self, password, address=None, path=None, exceptfunc=None):
        return self.simplerun("cli_export_key", {"password": password, "address": address, "path": path, "exceptfunc": exceptfunc})

    # send <id|alias> <address> <value>|all [fee=0] 向指定地址转账 参数分别为：资产 ID，对方地址，转账金额，手续费   需要打开钱包
    # examples:
    # 1. send c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b 100
    # 2. send neo AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b 100
    def send(self, password, id_alias, address, value, fee=0, exceptfunc=None):
        return self.simplerun("cli_export_key", {"password": password, "id_alias": id_alias, "address": address, "value": value, "fee": fee, "exceptfunc": exceptfunc})

    # import multisigaddress m pubkeys...   创建多方签名合约    需要打开钱包
    # examples:
    # import multisigaddress 1 037ebe29fff57d8c177870e9d9eecb046b27fc290ccbac88a0e3da8bac5daa630d 03b34a4be80db4a38f62bb41d63f9b1cb664e5e0416c1ac39db605a8e30ef270cc
    def import_multisigaddress(self, m, pubkeys, exceptfunc=None):
        return self.simplerun("cli_import_multisigaddress", {"m": m, "pubkeys": pubkeys, "exceptfunc": exceptfunc})

    # sign <jsonObjectToSign>   签名 参数为：记录交易内容的 json 字符串 需要打开钱包
    def sign(self, jsonobj, exceptfunc=None):
        return self.simplerun("cli_sign", {"jsonobj": jsonobj, "exceptfunc": exceptfunc})

    # relay <jsonObjectToSign>  广播 参数为：记录交易内容的 json 字符串 需要打开钱包
    def relay(self, jsonobj, exceptfunc=None):
        return self.simplerun("cli_relay", {"jsonobj": jsonobj, "exceptfunc": exceptfunc})

    # show state    显示当前区块链同步状态
    def show_state(self, times=1, exceptfunc=None):
        return self.simplerun("cli_show_state", {"times": times, "exceptfunc": exceptfunc})

    # show node 显示当前已连接的节点地址和端口
    def show_node(self, exceptfunc=None):
        return self.simplerun("cli_show_node", {"exceptfunc": exceptfunc})

    # show pool 显示内存池中的交易（这些交易处于零确认的状态）
    def show_pool(self, exceptfunc=None):
        return self.simplerun("cli_show_pool", {"exceptfunc": exceptfunc})

    # export blocks [path=chain.acc]    导出全部区块数据，导出的结果可以用作离线同步
    def export_all_blocks(self, path=None, exceptfunc=None):
        return self.simplerun("cli_export_all_blocks", {"path": path, "exceptfunc": exceptfunc})

    # export blocks <start> [count] 从指定区块高度导出指定数量的区块数据，导出的结果可以用作离线同步
    def export_blocks(self, start, count=None, exceptfunc=None):
        return self.simplerun("cli_export_blocks", {"start": start, "count": count, "exceptfunc": exceptfunc})

    # start consensus   启动共识
    def start_consensus(self, exceptfunc=None):
        return self.simplerun("cli_start_consensus", {"exceptfunc": exceptfunc})
