# -*- coding:utf-8 -*-
import urllib
import urllib.request
import json
import time
import copy
import os
import paramiko
import sys

sys.path.append('..')
sys.path.append('../src')

import utils.connect
from utils.config import Config
from utils.logger import LoggerInstance as logger
from utils.taskdata import Task
from utils.taskrunner import TaskRunner
from utils.error import RPCError
from api.rpc import RPCApi

class NodeApi:
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
        request = copy.copy(NodeApi.REQUEST_BODY)
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
        (result, response) = TaskRunner.run_single_task(task, False)
        if response is None:
            raise Exception("cli rpc connect error")
        if response["jsonrpc"] != jsonrpc:
            raise Exception("cli rpc connect jsonrpc not valid: " + response["jsonrpc"])
        if response["id"] != id:
            raise Exception("cli rpc connect id not valid: " + str(response["id"]))
        if "error" in response.keys() and response["error"] != 0:
            raise RPCError(json.dumps(response["error"]))
        return response["result"]

    def sftp_transfer(self, _from, _to, remotenode, op="get"):
        # on local host
        # if _node_index == 0:
        #     cmd = "cp -rf " + _from + " " + _to
        #     os.system(cmd)
        #     return
        # private_key = paramiko.RSAKey.from_private_key_file("../../resource/id_rsa", "367wxd")
        transport = paramiko.Transport((Config.NODES[remotenode]["ip"], 22))
        transport.connect(username=Config.NODES[remotenode]["sshuser"], password=Config.NODES[remotenode]["sshpwd"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        if op == "put":
            sftp.put(_from, _to)
        elif op == "get":
            sftp.get(_from, _to)
        else:
            logger.error("operation not supported")
        transport.close()

    def clear(self, blocks=True, acc=True):
        neopath = Config.NODES[self.currentnode]["path"].replace("neo-cli.dll", "")
        cmd = ""
        if blocks:
            cmd += neopath + "/Chain_* " + neopath + "/Index_*"
        if acc:
            if cmd=="":
                cmd += neopath + " *.acc"
            else:
                cmd += " *.acc"
        if cmd =="":
            return 0
        else:
            return self.exec_cmd("rm -rf " +cmd)

    def send_file(self, _from, to):
        pass

    def wait_gen_block(self):
        rpcapi = RPCApi()
        rpcapi.setnode(self.currentnode)
        lastheight = rpcapi.getblockcount()
        times = 0
        while True:
            time.sleep(1)
            times = times + 1
            currentheight = rpcapi.getblockcount()
            if (lastheight != currentheight):
                return True
            if (times > Config.GEN_BLOCK_TIMEOUT):
                return False

    def wait_tx_result(self, txhash):
        pass

    def get_current_node(self):
        currentip = urllib.request.urlopen('http://ip.42.pl/raw').read()
        if not currentip:
            return None
        currentip = (str(currentip).strip("'b"))
        for node_index in range(len(Config.NODES)):
            node = Config.NODES[node_index]
            if node["ip"] == currentip:
                return node_index
        return None

    def check_node_block(self, node_list):
        pass

    '''
    def start_nodes(self, indexs, start_params=Config.DEFAULT_NODE_ARGS, clear_chain=False, clear_log=False, program="ontology", config="config.json"):
        for index in indexs:
            self.start_node(index, start_params, clear_chain, clear_log, program, config)
        time.sleep(10)

    def start_node(self, index, start_params=Config.DEFAULT_NODE_ARGS, clear_chain=False, clear_log=False, program="ontology", config="config.json"):
        logger.info("start node: " + str(index) + " start_params:" + start_params + " clear_chain:" + str(clear_chain) + " clear_log:" + str(clear_log))
        request = {
            "method": "start_node",
            "jsonrpc": "2.0",
            "id": 0,
            "params": {
                "clear_chain": clear_chain,
                "clear_log": clear_log,
                "name": program,
                "node_args": start_params,
                "config": config
            }
        }

        ip = Config.NODES[index]["ip"]
        response = utils.connect.con_test_service(ip, request)
        return response

    def stop_all_nodes(self):
        for node_index in range(len(Config.NODES)):
            self.stop_nodes([node_index])

    def stop_nodes(self, indexs):
        for index in indexs:
            self.stop_node(index)

    def stop_node(self, index):
        logger.info("stop node: " + str(index))
        request = {
            "method": "stop_node",
            "jsonrpc": "2.0",
            "id": 0
        }

        ip = Config.NODES[index]["ip"]
        response = utils.connect.con_test_service(ip, request)

        return response
    '''
    #
    def replace_configs(self, indexs, config=None):
        for index in indexs:
            self.replace_config(index, config)

    def replace_config(self, index, config=None):
        if not config:
            config = {}

        request = {
            "method": "replace_node_config",
            "jsonrpc": "2.0",
            "id": 0,
            "params": config
        }

        ip = Config.NODES[index]["ip"]
        response = utils.connect.con_test_service(ip, request)

        return response

    def exec_cmd(self, cmd):
        return self.simplerun("exec_cmd", {"cmd": cmd})