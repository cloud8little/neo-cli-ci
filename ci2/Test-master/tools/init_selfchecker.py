# -*- coding:utf-8 -*-
import sys
import logging
import json
import numpy as np

sys.path.append('..')
sys.path.append('../src')

from utils.config import Config
from api.apimanager import API

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handle = logging.FileHandler("init_selfcheck.log", mode="w")
handle.setLevel(level=logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handle.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(level=logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handle)
logger.addHandler(console)

np.set_printoptions(precision=16, suppress=True)
class SelfCheck():
    def __init__(self):
        self.remote_tmp_dir = "/home/neo/"
        pass

    def stop_nodes(self):
        for node_index in range(len(Config.NODES)):
            API.clirpc(node_index).terminate()

    def start_nodes(self):
        for node_index in range(len(Config.NODES)):
            if "consensusnode" in Config.NODES[node_index]:
                if Config.NODES[node_index]["consensusnode"]:
                    API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                    API.clirpc(node_index).exec(False)

    def clear_nodes(self):
        logger.info("----------------------------------")
        logger.info("begin clear nodes\n")
        for node_index in range(len(Config.NODES)):
            remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
            logger.info("begin clear " + str(node_index) + "\n")
            API.node(node_index).exec_cmd("rm -rf " + remotenodepath)
        logger.info("end clear nodes\n")

    def copy_node(self):
        logger.info("----------------------------------")
        logger.info("begin copy node\n")
        # remotenodelastfoldername = remotenodepath.split("/")[:-1]
        lastip = ""
        for node_index in range(len(Config.NODES)):
            logger.info("copy node[" + str(node_index) + "]\n")
            remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
            remotenodeprepath = "/".join(remotenodepath.split("/")[:-1])
            API.node(node_index).exec_cmd("mkdir -p " + remotenodeprepath)
            if lastip == Config.NODES[node_index]["ip"]:
                logger.info(lastip + " neo-cli.tar.gz has already exist...")
            else:
                logger.info("begin transfer file" + Config.RESOURCE_PATH + "/nodes/neo-cli.tar.gz" + "\n")
                API.node(node_index).exec_cmd("rm -rf " + self.remote_tmp_dir + "neo-cli.tar.gz")
                API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/neo-cli.tar.gz", self.remote_tmp_dir + "neo-cli.tar.gz", node_index, "put")
                logger.info("end transfer file" + Config.RESOURCE_PATH + "/nodes/neo-cli.tar.gz" + "\n")
                logger.info("begin transfer file" + Config.RESOURCE_PATH + "/nodes/neo-cli2.tar.gz" + "\n")
                API.node(node_index).exec_cmd("rm -rf " + self.remote_tmp_dir + "neo-cli2.tar.gz")
                API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/neo-cli2.tar.gz", self.remote_tmp_dir + "neo-cli2.tar.gz", node_index, "put")
                logger.info("end transfer file" + Config.RESOURCE_PATH + "/nodes/neo-cli2.tar.gz" + "\n")
            if node_index==len(Config.NODES)-1:
                API.node(node_index).exec_cmd("tar -xvf " + self.remote_tmp_dir + "neo-cli2.tar.gz -C " + remotenodeprepath)
            else:
                API.node(node_index).exec_cmd("tar -xvf " + self.remote_tmp_dir + "neo-cli.tar.gz -C " + remotenodeprepath)
            # API.node(node_index).exec_cmd("mv " + remotenodeprepath + "/neo-cli " + remotenodepath)
            if node_index == 0:
                API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/chain.acc", remotenodepath + "/chain.acc", node_index, "put")
            API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/config.json", remotenodepath + "/config.json", node_index, "put")
            API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", remotenodepath + "/protocol.json", node_index, "put")
            API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/wallet/" + Config.NODES[node_index]["walletname"], remotenodepath + "/" + Config.NODES[node_index]["walletname"], node_index, "put")
            lastip = Config.NODES[node_index]["ip"]
        logger.info("end copy node\n")
        logger.info("----------------------------------\n\n")

    def check_connected_nodes(self):
        logger.info("----------------------------------")
        logger.info("start checking connected node count\n")

        connected_node_count = API.rpc().getconnectioncount()
        if connected_node_count != len(Config.NODES) - 1:
            logger.error("connected node counts : %d, config node counts : %d" % (connected_node_count, len(Config.NODES) - 1))

        logger.info("checking connected node count OK")
        logger.info("----------------------------------\n\n")

    def check_all(self):
        # stop all nodes
        self.stop_nodes()
        self.clear_nodes()
        self.copy_node()
        self.start_nodes()
        self.check_connected_nodes()

if __name__ == "__main__":
    selfcheck = SelfCheck()
    selfcheck.check_all()
