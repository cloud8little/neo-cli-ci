# -*- coding:utf-8 -*-
import unittest
import os
import sys
import traceback
import json
import time
import shutil

sys.path.append('..')
sys.path.append('../..')
testpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(testpath)
ConfigPath=testpath.split("/test/test_rpc")[0]

from utils.logger import LoggerInstance as logger
from utils.parametrizedtestcase import ParametrizedTestCase
from utils.error import AssertError, RPCError
from utils.config import Config
from api.apimanager import API
from neo.walletmanager import WalletManager
from neo.wallet import Wallet, Account
from test_rpc.test_config import test_config


######################################################
# test cases
class test_rpc(ParametrizedTestCase):
    
    def test_init(self):
        #关闭四个共识节点
        for node_index in range(len(Config.NODES)):
            if "consensusnode" in Config.NODES[node_index]:
                if Config.NODES[node_index]["consensusnode"]:
                    API.clirpc(node_index).terminate()
        time.sleep(10)
        # delete files(需要删除区块链及所有.acc文件)
        for node_index in range(len(Config.NODES)):
            if "consensusnode" in Config.NODES[node_index]:
                if Config.NODES[node_index]["consensusnode"]:
                    remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                    logger.info("begin clear " + str(node_index) + "\n")
                    API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"*.acc")
                    API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Chain_*")
                    API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Index_*")
        time.sleep(10)
        fpath=Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
        #删除Chain和Index文件夹
        for root , dirs, files in os.walk(fpath):
            for name in dirs:
                if 'Chain_' in name or 'Index_' in name:
                    print ("delete file:"+name)
                    filename=fpath+name+"/"
                    shutil.rmtree(filename)
        #删除所有.acc的文件
        os.system("rm -rf "+fpath+"*.acc")
        # 将protocol.json copy 到所有节点内替换原有的文件
        #从源文件中copy出需要的.acc文件放到对应根目录
        for node_index in range(len(Config.NODES)):
            if "consensusnode" in Config.NODES[node_index]:
                if Config.NODES[node_index]["consensusnode"]:
                    remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                    API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/" + "chain.acc", remotenodepath + "chain.acc", node_index, "put")
                    API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/node" +str(node_index+1)+ "/protocol.json", remotenodepath + "protocol.json", node_index, "put")
        #copy
        os.system("cp "+Config.RESOURCE_PATH + "/nodes/" + "chain.acc"+" "+fpath+"chain.acc")
        # 启动共识节点
        for node_index in range(len(Config.NODES)):
            if "consensusnode" in Config.NODES[node_index]:
                if Config.NODES[node_index]["consensusnode"]:
                    print(node_index)
                    API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                    API.clirpc(node_index).exec(False)
        time.sleep(10)
    
    def setUp(self):
        API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
        logger.open("test_rpc/" + self._testMethodName + ".log", self._testMethodName)

    def tearDown(self):
        API.cli().terminate()
        logger.close(self.result())

    def return_balance(self,balanceRes):
        if not "balance" in balanceRes:
            return 0
        else:
            return balanceRes["balance"]
        
 

    ##neo:flag=true gas:flag=false
    def return_neo_gas(self,accountstate,flag=False):
        if not "balances" in accountstate:
            return 0
        if len(accountstate["balances"])<=0:
            return 0
        if flag:
            asset_id="0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
        else:
            asset_id="0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"
        for tempRes in accountstate["balances"]:
            if not "value" in tempRes:
                break
            if not "asset" in tempRes:
                break
            else:
                if tempRes["asset"]==asset_id:
                    return tempRes["value"]
        return 0 
    ###dumpprivkey
    def test_001_dumpprivkey(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).dumpprivkey(WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(result == test_config.privkey, "privkey not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_002_dumpprivkey(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).dumpprivkey(test_config.address_notexist1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Object reference not set to an instance of an object." , "error message not match")            
        except Exception as e:        
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
              
    def test_003_dumpprivkey(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).dumpprivkey(test_config.address_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
            
    def test_005_dumpprivkey(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)            
            result = API.rpc(test_config.node_default).dumpprivkey("")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
      
    def test_006_dumpprivkey(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).dumpprivkey(address=None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")            
        except Exception as e:            
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
  
    def test_007_dumpprivkey(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).dumpprivkey(WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Access denied" , "error message not match")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

###getaccountstate
    def test_008_getaccountstate(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ###调用getaccountstate查看钱包内地址的资产，将neo资产存至balance1            
            result1 = API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address())
            balance1 =self.return_neo_gas(result1,True)
            self.ASSERT(result1 != None, "get getaccountstate error!")

            result2 = API.rpc(test_config.node_default).getaccountstate(test_config.address_default)
            balance2 =self.return_neo_gas(result2,True)
            self.ASSERT(result2 != None, "get getaccountstate error!")
            ###调用getbalance查看当前钱包的neo资产并存至balance2
            result3 = API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo)
            self.ASSERT(result3 != None, "get getbalance error!")            
            balance3 = result3["balance"]
            print(balance1)
            print(balance2)
            print(balance3)
            self.ASSERT(round(float(balance3),8) == round(float(balance1),8)+round(float(balance2),8), "Assets information not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_009_getaccountstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist1)
            self.ASSERT(result["balances"] == [], "")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_010_getaccountstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)            
            result = API.rpc(test_config.node_default).getaccountstate(test_config.address_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
    
    def test_012_getaccountstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getaccountstate("")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

###getaccountstate()
    def test_013_getaccountstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getaccountstate(address = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")            
        except Exception as e:            
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

##getassetstate            
    def test_014_getassetstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)            
            result = API.rpc(test_config.node_default).getassetstate(test_config.asset_id_neo)
            self.ASSERT(result == test_config.assetstate, "Assets information not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
               
    def test_015_getassetstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getassetstate(test_config.asset_id_notexist)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Unknown asset" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
    
    def test_016_getassetstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getassetstate(test_config.asset_id_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
   
    def test_018_getassetstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getassetstate("")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
     
    def test_019_getassetstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getassetstate(asset_id = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc()) 
            self.ASSERT(False, "error:Exception")            

###getbalance
    def test_020_getbalance(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            #调用cli的list_asset查看wallet_5.json的Neo资产
            API.cli().list_asset(exceptfunc = lambda msg: msg.find(test_config.asset_id_neo) >= 0)        
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "list asset failed")
            try:
                balance1 =climsg.split("name:NEO")[1].split("confirmed:")[0].split("balance:")[1]
            except:
                self.ASSERT(False, "can not get balance value")
            try:
                confirmed1 =climsg.split("name:NEO")[1].split("confirmed:")[1].split("\n")[0]
            except:
                self.ASSERT(False, "can not get confirmed value")
            #调用getbalance查看Neo资产，看是否一致
            result1 = API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo)                       
            balance2 = result1["balance"]
            confirmed2 = result1["confirmed"]
            if result1 == None:
                self.ASSERT(False, "get balance failed")
            else:
                if balance1.strip() == balance2.strip() and confirmed1.strip() == confirmed2.strip():
                    flag=True
                else:
                    flag=False 
            self.ASSERT(flag, "asset not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
    
    def test_021_getbalance(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getbalance(test_config.asset_id_notexist)
            self.ASSERT(result == test_config.asset_id_notexist_result, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
 
    def test_022_getbalance(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getbalance(test_config.asset_id_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "asset_id not exists" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
   
    def test_024_getbalance(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getbalance("")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc()) 
            self.ASSERT(False, "error:Exception")            
   
    def test_025_getbalance(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getbalance(asset_id = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_026_getbalance(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Access denied." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

###getbestblockhash
    def test_027_getbestblockhash(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getbestblockhash获取当前最高区块的hash值#            
            result = API.rpc(test_config.node_default).getbestblockhash()
            #调用getblockcount获取当前区块数量#
            bestblockhash_height = API.rpc(test_config.node_default).getblockcount()
            #将区块数量-1传入getblock获取当前最高区块的hash值，两次hash值进行对比#
            bestblockhash = (API.rpc(test_config.node_default).getblock((bestblockhash_height-1), 1))["hash"]            
            self.ASSERT(result == bestblockhash, "get bestblockhash failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

###getblock
    def test_028_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getblock获取index为104区块的hash值#            
            result = API.rpc(test_config.node_default).getblock(test_config.index_right, 1)
            #将hash值传入getblock方法，两次返回的信息是否一致#
            bestblock_message = API.rpc(test_config.node_default).getblock(result["hash"], 1)            
            self.ASSERT(result == bestblock_message, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())  
            self.ASSERT(False, "error:Exception")            
        
    def test_029_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock(test_config.hash_notexist, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Unknown block" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
           
    def test_030_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock(test_config.hash_wrong_str, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
           
    def test_032_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock("", 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())  
            self.ASSERT(False, "error:Exception")     

    def test_033_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock(hash=None,verbose = 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())  
            self.ASSERT(False, "error:Exception")             

    def test_036_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(test_config.hash_default, test_config.verbose_negative)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc()) 
            self.ASSERT(False, "error:Exception")            

    def test_037_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock(test_config.hash_default, test_config.verbose_beyond)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_038_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock(test_config.hash_default, test_config.verbose_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
   
    def test_040_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock(test_config.hash_default, "")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        

    def test_041_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblock(test_config.hash_default , verbose = "empty")
            self.ASSERT(result == test_config.message_serialized, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
 
    def test_042_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getblock获取index为104区块的hash值#            
            result = API.rpc(test_config.node_default).getblock(test_config.index_right, 1)
            #将hash值传入getblock方法，两次返回的信息是否一致#
            bestblock_message = API.rpc(test_config.node_default).getblock(result["hash"], 1)            
            self.ASSERT(result == bestblock_message, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_043_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getblockcount获取区块数量#
            index_beyond = (API.rpc(test_config.node_default).getblockcount())+10            
            result = API.rpc(test_config.node_default).getblock(index_beyond, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_044_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(test_config.index_wrong_str, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
            
    def test_045_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(test_config.index_negative, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")          
            
    def test_048_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(hash = None, verbose=1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception") 
 
    def test_051_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(test_config.index_right, test_config.verbose_negative)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_052_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(test_config.index_right, test_config.verbose_beyond)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        

    def test_053_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(test_config.index_right, test_config.verbose_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_055_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblock(test_config.index_right, "")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
         
    def test_056_getblock(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)            
            result = API.rpc(test_config.node_default).getblock(test_config.index_right,verbose = "empty")
            self.ASSERT(result == test_config.message_serialized, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
             
###getblockcount
    def test_057_getblockcount(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            result = API.rpc(test_config.node_default).getblockcount()            
            result1 = API.rpc(test_config.node_other1).getblockcount()        
            self.ASSERT(result == result1, "can not get block count")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

###getblockheader
    def test_058_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getblockhash获取index值为104区块的hash值#            
            result1 = API.rpc(test_config.node_default).getblockhash(test_config.index_right)
            #104区块的hash值传入getblockheader，返回信息的index是否为104#            
            result = API.rpc(test_config.node_default).getblockheader(result1, 1)
            self.ASSERT(result["index"] == test_config.index_right, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
              
    def test_059_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader(test_config.hash_notexist, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Unknown block" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
           
    def test_060_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader(test_config.hash_wrong_str, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
                 
    def test_062_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader("", 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_063_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader(hash=None, verbose=1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")             

    def test_066_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader(test_config.hash_default, test_config.verbose_negative)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_067_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader(test_config.hash_default, test_config.verbose_beyond)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        

    def test_068_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader(test_config.hash_default, test_config.verbose_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
            
    def test_070_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader(test_config.hash_default, "")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_071_getblockheader(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).getblockheader( hash=test_config.hash_default , verbose = "empty")
            self.ASSERT(result == test_config.message_serialized2, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

###getblockhash
    def test_072_getblockhash(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getblockhash获取该区块hash值#            
            result1 = API.rpc(test_config.node_default).getblockhash(test_config.index_right)
            #将获取的区块hash值传入getblock，输出信息中index与getblockhash的index值是否一致#
            result = API.rpc(test_config.node_default).getblock(result1, 1)
            self.ASSERT(result["index"] == test_config.index_right, "get blockhash failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
               
    def test_073_getblockhash(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getblockcount获取区块数量#
            index_beyond = (API.rpc(test_config.node_default).getblockcount())+10            
            result = API.rpc(test_config.node_default).getblockhash(index_beyond)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Invalid Height" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
              
    def test_074_getblockhash(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblockhash(test_config.index_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Specified cast is not valid." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
              
    def test_075_getblockhash(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblockhash(test_config.index_negative)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Invalid Height" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
           
    def test_078_getblockhash(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblockhash(index = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

###getblocksysfee            
    def test_079_getblocksysfee(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblocksysfee(test_config.index_right)
            self.ASSERT(result == test_config.blocksysfee_indexNonzero, "System fee not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_080_getblocksysfee(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblocksysfee(test_config.index_right_zero)
            self.ASSERT(result == test_config.blocksysfee, "System fee not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
      
    def test_081_getblocksysfee(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getblockcount获取区块数量#
            index_beyond = (API.rpc(test_config.node_default).getblockcount())+10            
            result = API.rpc(test_config.node_default).getblocksysfee(index_beyond)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Invalid Height" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
            
    def test_082_getblocksysfee(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblocksysfee(test_config.index_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Specified cast is not valid." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
         
    def test_083_getblocksysfee(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblocksysfee(test_config.index_negative)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Invalid Height" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
            
    def test_086_getblocksysfee(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getblocksysfee(index = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        

###getconnectioncount
    def test_087_getconnectioncount(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")       
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            result2 = API.cli().readmsg()
            logger.print(result2)
            #show_state waitsync 获取当前连接数#
            lastline = result2[result2.rfind("block: "):]
            try:
                result1 = lastline.split("unconnected:")[0].split("connected:")[1]
            except:
                self.ASSERT(False, "can not get connected value")                
            logger.print(result1)            
            self.ASSERT(status, info)
            #调用getconnectioncount获取当前连接数，进行比较#             
            result = API.rpc(test_config.node_default).getconnectioncount()
            self.ASSERT(str(result).strip() == str(result1).strip(), "connectioncount not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

###getcontractstate
    def test_088_getcontractstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getcontractstate(test_config.contract_script_hash)
            self.ASSERT(result == test_config.contractstate_message, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception") 

    def test_089_getcontractstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getcontractstate(test_config.contract_script_hash_notexist)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Unknown contract" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_090_getcontractstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getcontractstate(test_config.contract_script_hash_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_092_getcontractstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getcontractstate("")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_093_getcontractstate(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getcontractstate(script_hash = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

###getnewaddress    创建新地址    
    def test_094_getnewaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            #调用getnewaddress创建新地址#            
            result1 = API.rpc(test_config.node_default).getnewaddress()        
            self.ASSERT(result1 != None, "create a new address Failed")
            API.cli().terminate()
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            #list address，查看新地址是否存在#
            API.cli().list_address(exceptfunc=(lambda msg: msg.find("Standard") >= 0))
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "list address failed")
            try:
                count =climsg.split("list address")[1].count("Standard",0,len(climsg))
            except:
                self.ASSERT(False, "can not get address count")
            try:
                str1 = climsg.split("Standard")[count-1]
            except:
                self.ASSERT(False, "can not get address")
            self.ASSERT(result1.strip() == str1.strip(), "not find new address")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
    
    def test_095_getnewaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getnewaddress()
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Access denied" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
         
###getrawmempool
    def test_096_getrawmempool(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            #发送一笔交易#
            result1 = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_neo,WalletManager().wallet(test_config.node_default).account().address(),test_config.address_default,1,fee = "empty",change_address = "empty")
            #立即调用getrawmempool，查看输出的txid与sendfrom的txid是否一致#            
            result = API.rpc(test_config.node_default).getrawmempool()
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            self.ASSERT(''.join(result) == result1["txid"], "Unconfirmed transactions not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
  
###getrawtransaction
    def test_097_getrawtransaction(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")            
            #发送一笔交易#            
            result1 = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_neo,WalletManager().wallet(test_config.node_default).account().address(),test_config.address_default,1000,fee = "empty",change_address = "empty")
            self.ASSERT(result1!=None, "get sendfrom failed")
            if "txid" in result1:
                txid=result1["txid"]
            else:
                txid=""
            #等一个区块#                
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            #确认交易完成#
            if txid!="":
                #将交易的txid传入getrawtransaction,确认输出的交易信息与sendfrom输出的一致#
                resTest=API.rpc(test_config.node_default).getrawtransaction(txid=txid,verbose=1);
                if resTest!=None:
                    if result1["vout"] == resTest["vout"]:
                        self.ASSERT(True, "")
                    else:
                        self.ASSERT(False, "get getrawtransaction failed")                    
            else:
                self.ASSERT(False, "no txid!")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
           
    def test_098_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(test_config.txid_wrong_notexist, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Unknown transaction" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
           
    def test_099_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(test_config.txid_wrong_str, 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
               
    def test_101_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction("", 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
             
    def test_102_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(txid = None,verbose = 1)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")                   
          
    def test_105_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(test_config.txid, test_config.verbose_negative)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
            
    def test_106_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(test_config.txid, test_config.verbose_beyond)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
    
    def test_107_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(test_config.txid, test_config.verbose_wrong_str)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_109_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(test_config.txid, "")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
  
    def test_110_getrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getrawtransaction(txid=test_config.txid,verbose = "empty")
            self.ASSERT(result == test_config.message_serialized3, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

###getstorage       
    def test_111_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage(test_config.contract_script_hash, test_config.key)
            self.ASSERT(result == test_config.storage_value, "message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception") 

    def test_112_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage(test_config.contract_script_hash_notexist, test_config.key)
            self.ASSERT(result == None, "result != null")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_113_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage(test_config.contract_script_hash_wrong_str, test_config.key)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_115_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage("", test_config.key)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_116_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage(script_hash = None,key = test_config.key)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_119_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage(test_config.contract_script_hash, test_config.key_wrong_str)
            self.ASSERT(result == None, "result != null")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_121_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage(test_config.contract_script_hash, "")
            self.ASSERT(result == None, "result != null")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_122_getstorage(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).getstorage( script_hash = test_config.contract_script_hash, key = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
           
###gettxout             
    def test_124_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).gettxout(test_config.txid_wrong_notexist, test_config.index_right)
            self.ASSERT(result == None, "result != null")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")                
                
    def test_125_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)            
            result = API.rpc(test_config.node_default).gettxout(test_config.txid_wrong_str, test_config.index_right)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)            
            self.ASSERT(json.loads(e.msg)["message"] == "Input string was not in a correct format." , "error message not match")        
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")                         
        
    def test_127_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).gettxout("", test_config.index_right)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
                 
    def test_128_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).gettxout( n = test_config.index_right)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        
        
    def test_129_gettxout(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            #发送一笔交易#            
            result1 = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_neo,WalletManager().wallet(test_config.node_default).account().address(),test_config.address_default,1000,fee = "empty",change_address = "empty")
            self.ASSERT(result1!=None, "get sendfrom failed")
            if "txid" in result1:
                txid=result1["txid"]
            else:
                txid=""
            #等一个区块#                
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            #确认交易完成#
            if txid!="":
                #将交易的txid传入gettxout#
                result = API.rpc(test_config.node_default).gettxout(result1["txid"], 1)
                if result!=None:
                    value1 = result["value"]
                    n = result["n"]                    
                else:
                    self.ASSERT(False, "get gettxout failed!")
                #将交易的txid传入getrawtransaction#
                resTest=API.rpc(test_config.node_default).getrawtransaction(txid=txid,verbose=1)
                if resTest!=None:
                    #获取getrawtransaction对应n值的value，与gettxout的value值比较#
                    for tempRes in resTest["vout"]:
                        if tempRes["n"] == n:
                            vulue2 = tempRes["value"]                            
                            if value1 == vulue2:
                                self.ASSERT(True, "")
                            else:
                                self.ASSERT(False, "value not match")                            
                        else:
                            if tempRes["n"] == None:                            
                                self.ASSERT(False, "vout meaasge not match")                        
                else:
                    self.ASSERT(False, "no confirm!")
            else:
                self.ASSERT(False, "no txid!")                        
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")                           
               
    def test_132_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)            
            result = API.rpc(test_config.node_default).gettxout(test_config.txid, test_config.index_wrong_str)
            self.ASSERT(False, "no error message")        
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)        
            self.ASSERT(json.loads(e.msg)["message"] == "Specified cast is not valid." , "error message not match")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
 
    def test_133_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).gettxout(test_config.txid, test_config.index_negative)         
            self.ASSERT(False, "no error message")            
        except AssertError as e:       
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:       
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")
        except Exception as e:        
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
           
    def test_135_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).gettxout(test_config.txid, "")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "One of the identified items was in an invalid format." , "error message not match")           
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")     

    def test_136_gettxout(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)        
            result = API.rpc(test_config.node_default).gettxout(txid=test_config.txid, n = None)
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"] == "Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index" , "error message not match")           
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
             
###getpeers
    def test_137_getpeers(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")        
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)            
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")    
            #获取getpeers返回的connected的节点port口#            
            result1 = API.rpc(test_config.node_default).getpeers()
            self.ASSERT(result1 != None, "getpeers failed")
            str0 = ''.join('%s' %id for id in result1["connected"])
            count = str0.count("port",0,len(str0))
            i = 0 
            if i<count:            

                print(str0)
                if "connected" in result1:
                    str1 =result1["connected"][0]["port"]                    
                    #str1 = ''.join('%s' %id for id in str0['port']).strip()
                else:
                    self.ASSERT(False, "can not get connected port")
                print(str1)
                #获取当前节点路径，读取config文件，与getpeers返回的节点port口是否一致#
                fp = open(ConfigPath+"/config.json", 'r', encoding='utf-8')
                str2 = fp.read()
                fp.close()
                print(ConfigPath+"/config.json")
                flag = str2.find(str(str1))
                if flag == False:
                    self.ASSERT(False, "connected nodes not match")
                i+=1
            
            self.ASSERT(flag, "connected nodes not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")        

###getvalidators
    def test_138_getvalidators(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")        
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")            
            result = API.rpc(test_config.node_default).getvalidators()
            print (str(result))
            self.ASSERT(result != None, "message not match")
            self.ASSERT(len(result) >=1, "message not match")
            for tmpRes in result:
                if (not "publickey" in tmpRes) and (not "votes" in tmpRes) and (not "active" in tmpRes):
                    self.ASSERT(False, "validator param miss!")
            ##这里目前无返回只能如此判断，如果加了返回可以在这里验证公钥及票数
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
           
###getversion
    def test_139_getversion(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)            
            result = API.rpc(test_config.node_default).getversion()
            self.ASSERT(result["port"] == test_config.port, "version meaasge not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

###getwalletheight
    def test_140_getwalletheight(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")        
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info) 
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            result1 = API.cli().readmsg()
            logger.print(result1)            
            #获取waitsync的第一个参数，即钱包高度#            
            lastline = result1[result1.rfind("block: "):]
            try:
                result2 = lastline.split("block: ")[1].split("/")[0]
            except:
                self.ASSERT(False, "can not get wallet height")                
            #调用getwalletheight获取钱包高度，与show_state的值作比较# 
            result = API.rpc(test_config.node_default).getwalletheight()
            self.ASSERT(int(result2) != 0 , "show state failed")
            self.ASSERT(str(result).strip() == str(result2).strip(), "walletheight not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")


           
    ###invoke 141-152
    ###正确的值

    def test_141_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=test_config.contract_script_hash,params=[{"type": "String","value": "name"},{"type":"Boolean","value": False}])
            if "state" in result:
                self.ASSERT(result["state"]=="HALT, BREAK", "invoke state error!!!")
            else:
                self.ASSERT(False, "no state in result")
            ##需要检查实际的name是不是注册进去的nep5test
            
            ###值需要放到config
            if "stack" in result:
                print (len(result["stack"]))
                if len(result["stack"])>0:
                    self.ASSERT(result["stack"][0]["value"]==test_config.storage_value,"name check")
                else:
                    self.ASSERT(False,"value have no value")  
            else:
                self.ASSERT(False,"stack have no value")  
            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
       
    ###invokescript_notexist
    def test_142_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=test_config.contract_script_hash_notexist, params=[{"type": "String","value": "name"},{"type":"Boolean","value": False}])
            self.ASSERT(result["state"]=="FAULT, BREAK", "invoke state error!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###wrong_str
    def test_143_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=test_config.wrong_str,params= [{"type": "String","value": "name"},{"type":"Boolean","value": False}])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###scripthash  ""        
    def test_145_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash="", params=[{"type": "String","value": "name"},{"type":"Boolean","value": False}])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###scripthash不填    
    def test_146_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=None,params=[{"type": "String","value": "name"},{"type":"Boolean","value": False}])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###param []
    def test_149_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=test_config.contract_script_hash, params=[])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###param wrong_str
    def test_150_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=test_config.contract_script_hash, params=test_config.wrong_str)
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###param ""
    def test_151_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=test_config.contract_script_hash, params=[""])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###param不填
    def test_152_invoke(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invoke(scripthash=test_config.contract_script_hash,params="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    


    ###invokefunction 153-170
    ###正确的值
    def test_153_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(scripthash=test_config.contract_script_hash, operation="name", params=[])
            if "state" in result:
                self.ASSERT(result["state"]=="HALT, BREAK", "invoke state error!!!")
            else:
                self.ASSERT(False, "no state in result")
            ##需要检查实际的name是不是注册进去的nep5test
            
            ###值需要放到config
            if "stack" in result:
                print (len(result["stack"]))
                if len(result["stack"])>0:
                    print(result["stack"][0]["value"]=="6e65703574657374")
                    self.ASSERT(result["stack"][0]["value"]=="6e65703574657374","name check")
                else:
                    self.ASSERT(False,"value have no value")  
            else:
                self.ASSERT(False,"stack have no value")  
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
         
    ###invokescript_notexist
    def test_154_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(scripthash=test_config.contract_script_hash_notexist, operation="name", params=[])
            self.ASSERT(result["state"]=="FAULT, BREAK", "invoke state error!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###invokescript wrong_str
    def test_155_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(scripthash=test_config.wrong_str,operation= "name", params=[])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###invokescript ""
    def test_157_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction("", "name", [])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###invokescript不填
    def test_158_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction( scripthash=None,operation="name", params=[])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###operation不存在
    def test_160_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, "test", [])
            self.ASSERT(result["state"]=="FAULT, BREAK", "invoke state error!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###operation abc
    def test_161_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, test_config.wrong_str, [])
            self.ASSERT(result["state"]=="FAULT, BREAK", "invoke state error!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###operation ""
    def test_163_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, "", [])
            self.ASSERT(result["state"]=="FAULT, BREAK", "invoke state error!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###operation 不填
    def test_164_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, operation=None,params=[])
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Specified cast is not valid.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
      
    ###param []
    def test_166_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, "balanceOf",[])
            if "state" in result:
                self.ASSERT(result["state"]=="HALT, BREAK", "invoke state error!!!")
            else:
                self.ASSERT(False, "no state in result")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
      
    ###params abc
    def test_167_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, "balanceOf", test_config.wrong_str)
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###param ""
    def test_169_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, "balanceOf", "")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###param不填
    def test_170_invokefunction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).invokefunction(test_config.contract_script_hash, "balanceOf","empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###invokescript 171-176
    ###正确的值
    def test_171_invokescript(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).invokescript(test_config.invokescript)
           # print ("result:"+str(result))
            if "state" in result:
                self.ASSERT(result["state"]=="HALT, BREAK", "invoke state error!!!")
            else:
                self.ASSERT(False, "no state in result")
            ##需要检查实际的name是不是注册进去的nep5test
            
            ###值需要放到config
            if "stack" in result:
                print (len(result["stack"]))
                if len(result["stack"])>0:
                    print(result["stack"][0]["value"]==test_config.storage_value)
                    self.ASSERT(result["stack"][0]["value"]==test_config.storage_value,"name check")
                else:
                    self.ASSERT(False,"value have no value")  
            else:
                self.ASSERT(False,"stack have no value")  
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###script invokescript_notexist
    def test_172_invokescript(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            
            result = API.rpc(test_config.node_default).invokescript(test_config.invokescript_notexist)
            
            self.ASSERT(result!=None, "result error!!!")
            self.ASSERT(result["state"]=='FAULT, BREAK', "state error!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###script abc
    def test_173_invokescript(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).invokescript(test_config.invokescript_wrong_str)
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###script ""
    def test_175_invokescript(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).invokescript("")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###script不填        
    def test_176_invokescript(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).invokescript()
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###listaddress 177-178
    ###正确的值
    def test_177_listaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).listaddress()
            #首先把列表中的address都获取出来
            if len(result)>0:
                mylist=[]
                for tempRes in result:
                    if "address" in tempRes:
                        mylist.append(tempRes["address"])
                if len(mylist)<=0:
                    self.ASSERT(False, "no address!!")
            else:
                self.ASSERT(False, "no result!!")
            ##然后获取钱包中的所有address地址
            account=[]
            with open(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], mode='r', encoding='utf-8') as f:
                str=f.readlines()
                f.close()                
                #test=json.loads(str)
                if "accounts" in json.loads(str[0]):
                    account=json.loads(str[0])["accounts"]
                else:
                    self.ASSERT(False, "no address in wallet!!")
                    #print(account)
            if len(account)>0:
                mylist2=[]
                for tempRes in account:
                    if "address" in tempRes:
                        mylist2.append(tempRes["address"])
                if len(mylist2)<=0:
                    self.ASSERT(False, "no address in wallet!!")
            else:
                self.ASSERT(False, "no address in wallet!!")
            ##检查list及list2是否含有相同address信息
            for resAddr in mylist:
                print(resAddr)
                flag=False
                for resAddr2 in mylist2:
                    if resAddr2==resAddr:
                        flag=True
                        break
                if not flag:
                    self.ASSERT(False, "no address "+resAddr+" in wallet!!")
                else:
                    self.ASSERT(True, "address "+resAddr+" in wallet!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###不打开钱包
    def test_178_listaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).listaddress()
            #print ("result:"+str(result))
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Access denied.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###sendfrom 179-213 
    ###正确的值
    def test_179_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            if "txid" in result:
                txid=result["txid"]
            else:
                txid=""
            ##事后获取
            if txid!="":
                resTest=API.rpc(test_config.node_default).getrawtransaction(txid=txid,verbose=1);
                if "confirmations" in resTest:
                    logger.print("now confirmations="+str(resTest["confirmations"]))
                    self.ASSERT(resTest["confirmations"]>0, "no confirm!")
                else:
                    self.ASSERT(False, "no confirm!")
            else:
                self.ASSERT(False, "no txid!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            ##计算结果
            value=10
            
            self.ASSERT((float(addr2Gas2)-float(addr2Gas))==value, "arrive address gas check")
            self.ASSERT((float(addr1Gas)-float(addr1Gas2))==value, "send address gas check")
            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
          
    ###asset_id_notexist
    def test_180_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_notexist,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="not found", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###wrong_str
    def test_181_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.wrong_str,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###asset_id ""        
    def test_183_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom("",
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###asset_id 不填
    def test_184_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###from格式正确但不存在
    def test_186_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                test_config.address_notexist,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###from abc
    def test_187_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                test_config.wrong_str,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###from ""        
    def test_189_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                "",
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###from不填
    def test_190_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    ###to格式正确但不存在
    def test_192_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账test_config.address_notexist的值不对，目前使用AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.address_notexist,value=10,fee=0,change_address="empty")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            ##计算结果
            value=10
            
            self.ASSERT((float(addr2Gas2)-float(addr2Gas))==value, "arrive address gas check")
            self.ASSERT((float(addr1Gas)-float(addr1Gas2))==value, "send address gas check")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    ###to abc
    def test_193_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                test_config.wrong_str,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(result, "")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###to ""        
    def test_195_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                "", value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###to不填
    def test_196_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###value=0        
    def test_199_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error!")
            self.ASSERT(res2!=None, "get getaccountstate error!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=0,fee=0,change_address="empty")
            self.ASSERT(result!=None, "")
                
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error!")
            self.ASSERT(res2!=None, "get getaccountstate error!")
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            ##计算结果
            value=0
            
            self.ASSERT((float(addr2Gas2)-float(addr2Gas))==value, "arrive address gas check")
            self.ASSERT((float(addr1Gas)-float(addr1Gas2))==value, "send address gas check")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###value过大
    def test_200_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=1000000000,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Insufficient funds", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###value<0        
    def test_201_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=-1,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    ###value abc
    def test_202_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=test_config.wrong_str,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    ###value ""
    def test_203_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value="",fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###value不填
    def test_204_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(),fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###fee=0.00000001    
    def test_207_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_neo,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=1,fee=0.00000001,change_address="empty")
            self.ASSERT(result!=None, "")
            self.ASSERT(result["net_fee"]=="0.00000001", "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            ##计算结果
            value=1
            fee=0.00000001
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==fee, "send address gas check")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
         
    ###0<fee<0.00000001
    def test_208_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0.00000000001,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Arithmetic operation resulted in an overflow.", "msg:Arithmetic operation resulted in an overflow. check")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee过大
    def test_209_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=100000000,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Insufficient funds", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee<0
    def test_210_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=-1,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee ""
    def test_211_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee="",change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Input string was not in a correct format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
      
    ###fee不填
    def test_212_sendfrom(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_neo,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee="empty",change_address="empty")
            self.ASSERT(result!=None, "")
            self.ASSERT(result["net_fee"]=="0", "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            ##计算结果
            value=10
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==fee, "send address gas check")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
           
    #不打开钱包
    def test_213_sendfrom(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_default).account().address(),
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Access denied", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            


    ###正确的值
    def test_214_sendrawtransaction(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##raw为获取当前账户balance内有多少nep5test资产
            result = API.rpc(test_config.node_default).sendrawtransaction("d101361417cf616df70247e8ec5efc80c139450608f3536c51c10962616c616e63654f6667220567141df11f104fc3a07cd52b735ab6a99de0000000000000000000000000")
            self.ASSERT(result, "send error!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###hex_notexists
    def test_215_sendrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ##raw为获取当前账户balance内有多少nep5test资产并作更改，send正常
            result = API.rpc(test_config.node_default).sendrawtransaction("d101361417cf616df70247e8ec5efc80c139450608f3536c51c10962616c616e63654f6667220567141df11f104fc3a07cd52b735ab6a99d10000000000000000000000000")
            self.ASSERT(result, "send error!!!")
            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###wrong_str
    def test_216_sendrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).sendrawtransaction(test_config.wrong_str)
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###hex ""        
    def test_218_sendrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).sendrawtransaction("")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###hex不填
    def test_219_sendrawtransaction(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendrawtransaction()
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_220_sendrawtransaction(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##raw为获取当前账户balance内有多少nep5test资产
            result = API.rpc(test_config.node_default).sendrawtransaction("d101361417cf616df70247e8ec5efc80c139450608f3536c51c10962616c616e63654f6667220567141df11f104fc3a07cd52b735ab6a99de0000000000000000000000000")
            self.ASSERT(False, "no error message")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Access denied", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")


    ###sendtoaddress 221-250 
    ###正确的值

    def test_221_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_neo,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(result!=None, "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=10
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==fee, "send address gas check")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###asset_id_notexist
    def test_222_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_notexist,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="not found", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###asset_id abc        
    def test_224_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress("abc",
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###asset_id ""
    def test_225_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress("",
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###asset_id不填
    def test_226_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###value超出原有金额        
    def test_228_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), 1000000000,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Insufficient funds", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###value<0
    def test_229_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), -1,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
  
    ###value 0.1
    def test_230_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=0.1,fee=0,change_address="empty")
            self.ASSERT(result!=None, "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=0
            gasvalue=0.1
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==gasvalue, "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "send address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###value abc
    def test_232_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), test_config.wrong_str,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###value ""
    def test_233_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), "",fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###value不填
    def test_234_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(asset_id=test_config.asset_id_gas,
                address=WalletManager().wallet(test_config.node_other5).account().address(),value=None,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###test_config.address_notexist（地址不存在但符合格式要求
    def test_236_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_neo,
                test_config.address_notexist, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=10
            gasvalue=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==gasvalue, "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
          
    ###address abc
    def test_238_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                "abc", value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###address ""
    def test_239_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                "", value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###address 不填
    def test_240_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                value=10,fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###fee=0.00000001
    def test_241_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_neo,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0.00000001,change_address="empty")
            self.ASSERT(result!=None, "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=10
            gasvalue=0
            fee=0.00000001
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
           
    ###fee太小
    def test_242_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0.000000001,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Arithmetic operation resulted in an overflow.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
          
    ###fee=1
    def test_244_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            ###临时定义
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_neo,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=1,change_address="empty")
            self.ASSERT(result!=None, "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=10
            gasvalue=0
            fee=1
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check")  
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
          
    ###fee=-1
    def test_245_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=-1,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee过大
    def test_246_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=1000000000,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Insufficient funds", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee abc
    def test_247_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=test_config.wrong_str)
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Input string was not in a correct format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee ""
    def test_248_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee="")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Input string was not in a correct format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
           
    ###fee不填
    def test_249_sendtoaddress(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_neo,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee="empty",change_address="empty")
            self.ASSERT(result!=None, "")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=10
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #不打开钱包
    def test_250_sendtoaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).sendtoaddress(test_config.asset_id_gas,
                WalletManager().wallet(test_config.node_other5).account().address(), value=10,fee=0)
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Access denied", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")


    ###sendmany 251-279
    ###需要先打开钱包
    ###100个同时转账，都为正确
    def test_251_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            testObj={"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address()}
            paramstest=[]
            for index in range(0,100):
                paramstest.append(testObj)
            result=API.rpc(test_config.node_default).sendmany(paramstest,fee=0,change_address="empty")
            self.ASSERT(result!=None, "")
            if "txid" in result:
                txid=result["txid"]
            else:
                txid=""
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事后获取
            if txid!="":
                resTest=API.rpc(test_config.node_default).getrawtransaction(txid=txid,verbose=1);
                if "confirmations" in resTest:
                    logger.print("now confirmations="+str(resTest["confirmations"]))
                    self.ASSERT(resTest["confirmations"]>0, "no confirm!")
                else:
                    self.ASSERT(False, "no confirm!")
            else:
                self.ASSERT(False, "no txid!")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=100
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###100个同时转账，50组出错        
    def test_252_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            testObj={"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address()}
            testObjErr={"asset":test_config.asset_id_neo,"value":-1,"address":WalletManager().wallet(test_config.node_other5).account().address()}
            paramstest=[]
            for index in range(0,50):
                paramstest.append(testObj)
                paramstest.append(testObjErr)
            result=API.rpc(test_config.node_default).sendmany(paramstest,fee=0,change_address="empty")
            self.ASSERT(result==None, "OK")
            
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=0
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=0
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

      
    ###单独一组转账,正确
    def test_253_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            ##转账 
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(result!=None, "")
            
            ##事后获取
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=1
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
      
    #asset不合法
    def test_254_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.wrong_str,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    #[{"":""}]
    def test_255_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"":""}],fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###"value": -1
    def test_256_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":-1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###"value": ""
    def test_257_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":"","address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###"address": "abc"
    def test_258_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":test_config.wrong_str,"fee":0}],fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###"address": ""
    def test_259_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":"","fee":0}],fee=0,change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###第一个[]出错
    def test_260_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":-1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address="empty")
            self.ASSERT(result==None, "OK")
            
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=0
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=0
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
    ###三个[]同时出错
    def test_261_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":-1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":-1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":-1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address="empty")
            self.ASSERT(result==None, "OK")
            
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=0
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=0
            gasvalue=0
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
    ###[""]
    def test_262_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([],fee=0,change_address="empty")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Invalid params", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###[]不填
    def test_263_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany(params="empty",fee="empty",change_address="empty")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            self.ASSERT(False, "no error message!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee=0.00000001
    def test_264_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0.00000001,change_address="empty")
            self.ASSERT(result!=None, "")            
            ##事后检查
            if "txid" in result:
                txid=result["txid"]
            else:
                txid=""
            ##事后获取
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            if txid!="":
                resTest=API.rpc(test_config.node_default).getrawtransaction(txid=txid,verbose=1);
                if "confirmations" in resTest:
                    logger.print("now confirmations="+str(resTest["confirmations"]))
                    self.ASSERT(resTest["confirmations"]>0, "no confirm!")
                else:
                    self.ASSERT(False, "no confirm!")
            else:
                self.ASSERT(False, "no txid!")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=1
            gasvalue=1
            fee=0.00000001
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###0<fee<0.00000001
    def test_266_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0.0000000001,change_address="empty")
            self.ASSERT(result!=None, "")            
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=1
            gasvalue=1
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###0<fee<原有本金
    def test_267_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=1,change_address="empty")
            self.ASSERT(result!=None, "")            
            ##事后检查
            if "txid" in result:
                txid=result["txid"]
            else:
                txid=""
            ##事后获取
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            if txid!="":
                resTest=API.rpc(test_config.node_default).getrawtransaction(txid=txid,verbose=1);
                if "confirmations" in resTest:
                    logger.print("now confirmations="+str(resTest["confirmations"]))
                    self.ASSERT(resTest["confirmations"]>0, "no confirm!")
                else:
                    self.ASSERT(False, "no confirm!")
            else:
                self.ASSERT(False, "no txid!")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=1
            gasvalue=1
            fee=1
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
            
    ###fee<0
    def test_268_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=-1,change_address="empty")
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee>原有本金
    def test_269_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=10000000000,change_address="empty")
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Insufficient funds", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee="abc"
    def test_270_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee="abc",change_address="empty")
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Input string was not in a correct format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee=""
    def test_271_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=None,change_address="empty")
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Input string was not in a correct format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###fee不填
    def test_272_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            ##事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee="empty",change_address=WalletManager().wallet(test_config.node_default).account().address())
            self.ASSERT(result!=None, "")            
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=1
            gasvalue=1
            fee=0
            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==value, "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception") 
    #change_address不存在（但符合格式）
    def test_274_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            #事前获取
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            res4=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            self.ASSERT(res1!=None, "get getbalance error1!")
            self.ASSERT(res3!=None, "get getbalance error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            self.ASSERT(res4!=None, "get getaccountstate error1!")
            addr1Neo=self.return_balance(res1)
            addr1Gas=self.return_balance(res3)
            addr2Neo=self.return_neo_gas(res2,True)
            addr3Neo=self.return_neo_gas(res4,True)
            addr2Gas=self.return_neo_gas(res2,False)
            addr3Gas=self.return_neo_gas(res4,False)

            result1 = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_neo,WalletManager().wallet(test_config.node_default).account().address(),WalletManager().wallet(test_config.node_default).account().address(),100,fee = "empty",change_address = "empty")
            result1 = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_gas,WalletManager().wallet(test_config.node_default).account().address(),WalletManager().wallet(test_config.node_default).account().address(),1,fee = "empty",change_address = "empty")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_neo,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0},{"asset":test_config.asset_id_gas,"value":0.1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address=test_config.address_notexist)
            self.ASSERT(result!=None, "")            
            ##事后检查
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            res1=API.rpc(test_config.node_default).getbalance(test_config.asset_id_neo);
            res3=API.rpc(test_config.node_default).getbalance(test_config.asset_id_gas);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_other5).account().address());
            res4=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            self.ASSERT(res1!=None, "get getbalance error2!")
            self.ASSERT(res3!=None, "get getbalance error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            self.ASSERT(res4!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_balance(res1)
            addr1Gas2=self.return_balance(res3)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr3Neo2=self.return_neo_gas(res4,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            addr3Gas2=self.return_neo_gas(res4,False)
            #print(addr2Neo2)
            #print(addr2Neo)
            ##计算结果
            value=1
            gasvalue=0.1
            fee=0

            self.ASSERT((float(addr2Neo2)-float(addr2Neo))==value, "arrive address neo check")
            self.ASSERT((float(addr1Neo)-float(addr1Neo2))==(value+int(addr3Neo2)-int(addr3Neo)), "send address neo check")
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)!=round(gasvalue+fee,8), "send address gas check?") 
            self.ASSERT(round(float(addr1Gas)-float(addr1Gas2),8)==round(gasvalue+fee+float(addr3Gas2)-float(addr3Gas),8), "send address gas check!") 
            self.ASSERT(round(float(addr2Gas2)-float(addr2Gas),8)==gasvalue, "arrive address gas check") 

        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    ###change_address="abc"
    def test_276_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address=test_config.wrong_str)
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###change_address=""
    def test_277_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address="")
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="One of the identified items was in an invalid format.", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###change_address不填
    def test_278_sendmany(self):
        try:
            API.cli().open_wallet(Config.WALLET_PATH + "/" + Config.NODES[test_config.node_default]["walletname"], "11111111")
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().rebuild_index()
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result0 = API.cli().waitsync(timeoout=120)
            self.ASSERT(result0 , "show_state waitsync failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            waitRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitRes , "wait generate block failed")
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}],fee=0,change_address="empty")
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###不打开钱包
    def test_279_sendmany(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).sendmany([{"asset":test_config.asset_id_gas,"value":1,"address":WalletManager().wallet(test_config.node_other5).account().address(),"fee":0}])
            self.ASSERT(False, "No Error Return!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Access denied", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###validateaddress 280-285完成
    ###正确的值
    def test_280_validateaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).validateaddress(WalletManager().wallet(test_config.node_default).account().address())
            if "address" in result:
                self.ASSERT(result["address"]==WalletManager().wallet(test_config.node_default).account().address(), "result[address] not the same")
            else:
                self.ASSERT(False, "result[address] not exist")
            if "isvalid" in result:
                self.ASSERT(result["isvalid"]==True, "")
            else:
                self.ASSERT(False, "result[isvalid] not exist")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    ###test_config.address_notexist
    def test_281_validateaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).validateaddress(test_config.address_notexist)
            if "address" in result:
                self.ASSERT(result["address"]==test_config.address_notexist, "result[address] not the same")
            else:
                self.ASSERT(False, "result[address] not exist")
            if "isvalid" in result:
                self.ASSERT(result["isvalid"]==True, "")
            else:
                self.ASSERT(False, "result[isvalid] not exist")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###abc
    def test_283_validateaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).validateaddress(test_config.wrong_str)
            if "address" in result:
                self.ASSERT(result["address"]==test_config.wrong_str, "result[address] not the same")
            else:
                self.ASSERT(False, "result[address] not exist")
            if "isvalid" in result:
                self.ASSERT(result["isvalid"]==False, "")
            else:
                self.ASSERT(False, "result[isvalid] not exist")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###""
    def test_284_validateaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).validateaddress("")
            if "address" in result:
                self.ASSERT(result["address"]=="", "result[address] not the same")
            else:
                self.ASSERT(False, "result[address] not exist")
            if "isvalid" in result:
                self.ASSERT(result["isvalid"]==False, "")
            else:
                self.ASSERT(False, "result[isvalid] not exist")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    ###address不填
    def test_285_validateaddress(self):
        try:
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).validateaddress(address="empty")
            self.ASSERT(False, "no error return!!!")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(json.loads(e.msg)["message"]=="Index was out of range. Must be non-negative and less than the size of the collection.\nParameter name: index", "error message error!!")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

if __name__ == '__main__':
    unittest.main()
