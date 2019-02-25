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

from utils.logger import LoggerInstance as logger
from utils.parametrizedtestcase import ParametrizedTestCase
from utils.error import AssertError, RPCError
from utils.config import Config

from api.apimanager import API
from neo.walletmanager import WalletManager
from neo.wallet import Wallet, Account
from test_config import test_config

######################################################
# test cases
class test_cli(ParametrizedTestCase):
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
        
    def return_balance(self,balanceRes):
        if not "balance" in balanceRes:
            return 0
        else:
            return balanceRes["balance"]
    
    # @classmethod
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
                    API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", remotenodepath + "protocol.json", node_index, "put")
        #copy
        os.system("cp "+Config.RESOURCE_PATH + "/nodes/" + "chain.acc"+" "+fpath+"chain.acc")
        #把protocol.json文件替换为最初的文件
        nodepath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
        os.system("cp "+Config.RESOURCE_PATH + "/nodes/node" + str(test_config.node_default+1) + "/protocol.json"+" "+fpath+"protocol.json")            # 将protocol.json copy 到所有节点内替换原有的文件
        #shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", nodepath+"protocol.json")
        # 启动共识节点
        for node_index in range(len(Config.NODES)):
            if "consensusnode" in Config.NODES[node_index]:
                if Config.NODES[node_index]["consensusnode"]:
                    print(node_index)
                    API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                    API.clirpc(node_index).exec(False)
        time.sleep(10)
        

    # def test_init(self):
        # #关闭四个共识节点
        # for node_index in range(len(Config.NODES)):
            # if "consensusnode" in Config.NODES[node_index]:
                # if Config.NODES[node_index]["consensusnode"]:
                    # API.clirpc(node_index).terminate()
        # time.sleep(10)
        # # delete files(需要删除区块链及所有.acc文件)
        # for node_index in range(len(Config.NODES)):
            # if "consensusnode" in Config.NODES[node_index]:
                # if Config.NODES[node_index]["consensusnode"]:
                    # remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                    # logger.info("begin clear " + str(node_index) + "\n")
                    # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"*.acc")
                    # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Chain_*")
                    # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Index_*")
        # time.sleep(10)
        # fpath=Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
        # #删除Chain和Index文件夹
        # for root , dirs, files in os.walk(fpath):
            # for name in dirs:
                # if 'Chain_' in name or 'Index_' in name:
                    # print ("delete file:"+name)
                    # filename=fpath+name+"/"
                    # shutil.rmtree(filename)
        # #删除所有.acc的文件
        # os.system("rm -rf "+fpath+"*.acc")
        # # 将protocol.json copy 到所有节点内替换原有的文件
        # #从源文件中copy出需要的.acc文件放到对应根目录
        # for node_index in range(len(Config.NODES)):
            # if "consensusnode" in Config.NODES[node_index]:
                # if Config.NODES[node_index]["consensusnode"]:
                    # remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                    # API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/" + "chain.acc", remotenodepath + "chain.acc", node_index, "put")
        # #copy
        # os.system("cp "+Config.RESOURCE_PATH + "/nodes/" + "chain.acc"+" "+fpath+"chain.acc")
        # #把protocol.json文件替换为SeedList未被删除的文件
        # nodepath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
        # shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", nodepath+"protocol.json")
        # # 启动共识节点
        # for node_index in range(len(Config.NODES)):
            # if "consensusnode" in Config.NODES[node_index]:
                # if Config.NODES[node_index]["consensusnode"]:
                    # print(node_index)
                    # API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                    # API.clirpc(node_index).exec(False)
        # time.sleep(10)
    
    def setUp(self):
        API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
        logger.open("test_cli/" + self._testMethodName + ".log", self._testMethodName)

    def tearDown(self):
        API.cli().terminate()
        logger.close(self.result())

    def test_003_createwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有wallet_name_json文件'''
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            '''创建并打开钱包'''
            API.cli().create_wallet(filepath=fpath+test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().open_wallet(fpath+test_config.wallet_name_json, test_config.wallet_password)
            API.cli().list_address(exceptfunc=(lambda msg: msg.find("Standard") >= 0))            
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)
            self.ASSERT(result, "create wallet failed")
            '''钱包是否存在'''            
            flag0=os.path.exists(fpath+test_config.wallet_name_json)
            self.ASSERT(flag0, "wallet not exist")
            try:
                result1 = climsg.split("address:")[1].split("\n")[0]
            except:
                self.ASSERT(False, "can not get list address")
            '''钱包存在比对地址'''            
            if flag0:
                with open(fpath+test_config.wallet_name_json, mode='r', encoding='utf-8') as f:
                    str=f.readlines()
                    try:
                        str="".join(str).split("\"address\":\"")[1].split("\",\"")[0]
                    except:
                        self.ASSERT(False, "can not get wallet address")
                    if str.strip()==result1.strip():
                        flag=True
                    else:
                        flag=False
            f.close()
            self.ASSERT(flag, "wallet address not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_004_createwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有test223.db3文件，相对路径下创建test223.db3钱包'''
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().list_address(exceptfunc=(lambda msg: msg.find("Standard") >= 0))
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)
            self.ASSERT(result, "create wallet failed1")
            '''查看当前节点路径下是否有该钱包'''
            flag=os.path.exists(fpath+test_config.wallet_name_db3)
            self.ASSERT(flag, "create wallet failed2")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_005_createwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有wallet_name_wrong文件'''
            if os.path.exists(fpath+test_config.wallet_name_wrong):
                os.remove(fpath+test_config.wallet_name_wrong)
            API.cli().create_wallet(filepath=test_config.wallet_name_wrong, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("Wallet files in that format are not supported, please use a .json or .db3 file extension.") >= 0)
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_007_createwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有wallet_name_db3文件'''
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            '''创建并打开钱包'''
            API.cli().create_wallet(filepath=fpath+test_config.wallet_name_db3, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().open_wallet(fpath+test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().list_address(exceptfunc=(lambda msg: msg.find("Standard") >= 0))
            '''创建重名的钱包'''            
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, clearfirst = False, exceptfunc=lambda msg: msg.find("Existing wallet file,cover it or not?") >= 0)
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_008_createwallet(self):
        try:
            API.cli().create_wallet(filepath=None,password=test_config.wallet_password,password2=test_config.wallet_password,exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)    
            self.ASSERT(result, "error message not match")
        except AssertError as e:        
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    '''新添加的case，不填密码'''
    def test_155_createwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有wallet_name_nopws文件'''
            if os.path.exists(fpath+test_config.wallet_name_nopws):
                os.remove(fpath+test_config.wallet_name_nopws)
            API.cli().create_wallet(filepath=test_config.wallet_name_nopws, password = None,password2 = None,exceptfunc = lambda msg: msg.find("cancelled") >= 0)
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)    
            self.ASSERT(result, "error message not match")
        except AssertError as e:        
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    '''新添加的case，第二遍密码输入错误'''
    def test_156_createwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有wallet_name_nopws文件'''
            if os.path.exists(fpath+test_config.wallet_name_nopws):
                os.remove(fpath+test_config.wallet_name_nopws)
            API.cli().create_wallet(filepath=test_config.wallet_name_nopws, password=test_config.wallet_password,password2=test_config.wallet_password_wrong, exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)    
            self.ASSERT(result, "error message not match")
        except AssertError as e:        
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_009_openwallet(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().list_address(exceptfunc = lambda msg: msg.find(test_config.wallet_default_address) >= 0)
            (result, stepname, climsg) = API.cli().exec()                
            logger.print(climsg)
            self.ASSERT(result, "open wallet failed")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_010_openwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()       
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().list_address(exceptfunc=(lambda msg: msg.find("Standard") >= 0))
            (result, stepname, climsg) = API.cli().exec()                
            logger.print(climsg)
            self.ASSERT(result, "open wallet failed")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_011_openwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有000test000.json文件'''
            if os.path.exists(fpath+test_config.wallet_name_notexist):
                os.remove(fpath+test_config.wallet_name_notexist)
            API.cli().open_wallet(test_config.wallet_name_notexist, exceptfunc = lambda msg: msg.find("File does not exist") >= 0)
            (result, stepname, climsg) = API.cli().exec()        
            logger.print(climsg)
            self.ASSERT(result, "error message not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_012_openwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''新建一个后缀错误的钱包'''
            if os.path.exists(fpath+test_config.wallet_name_exist_wrong):
                os.remove(fpath+test_config.wallet_name_exist_wrong)
            f = open(fpath+test_config.wallet_name_exist_wrong, 'w')
            f1 = open(fpath+test_config.wallet_name_json, 'r')
            indata = f1.read()
            f.write(indata)
            f.close()
            f1.close()
            API.cli().open_wallet(test_config.wallet_name_exist_wrong, test_config.wallet_password, exceptfunc = lambda msg: msg.find("error") < 0)
            (result, stepname, climsg) = API.cli().exec()                
            logger.print(climsg)
            self.ASSERT(result, "error message not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_014_openwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''新建一个名称为乱码的钱包'''
            if os.path.exists(fpath+test_config.wallet_name_exist_erroecode_json):
                os.remove(fpath+test_config.wallet_name_exist_erroecode_json)
            f = open(fpath+test_config.wallet_name_exist_erroecode_json, 'w')
            f1 = open(fpath+test_config.wallet_name_json, 'r')
            indata = f1.read()
            f.write(indata)
            f.close()
            f1.close()
            API.cli().open_wallet(test_config.wallet_name_exist_erroecode_json, test_config.wallet_password, exceptfunc = lambda msg: msg.find("File does not exist") >= 0)
            (result, stepname, climsg) = API.cli().exec()                
            logger.print(climsg)        
            self.ASSERT(result, "error message not match")                
        except AssertError as e:
            logger.error(e.msg)            
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_015_openwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().list_address(exceptfunc=(lambda msg: msg.find("Standard") >= 0))
            (result, stepname, climsg) = API.cli().exec()                
            logger.print(climsg)        
            self.ASSERT(result, "open wallet failed")                
        except AssertError as e:
            logger.error(e.msg)            
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_016_openwallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''新建一个内容为空的钱包'''
            if os.path.exists(fpath+test_config.wallet_name_null):
                os.remove(fpath+test_config.wallet_name_null)
            f = open(fpath+test_config.wallet_name_null, 'w')
            f.close()
            API.cli().open_wallet(test_config.wallet_name_null, test_config.wallet_password, exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()                
            logger.print(climsg)        
            self.ASSERT(result, "error message not match")                
        except AssertError as e:
            logger.error(e.msg)            
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_018_openwallet(self):
        try:
            API.cli().open_wallet(filepath=None, exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()                
            logger.print(climsg)        
            self.ASSERT(result, "error message not match")                
        except AssertError as e:
            logger.error(e.msg)            
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_020_upgradewallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有升级过后的钱包文件存在'''
            if os.path.exists(fpath+test_config.wallet_name_db3_upgrade):
                os.remove(fpath+test_config.wallet_name_db3_upgrade)
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().upgrade_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password, exceptfunc = lambda msg: msg.find("Wallet file upgrade complete. New wallet file has been auto-saved at: "+test_config.wallet_name_db3_upgrade) >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "upgrade the wallet file failed")
            '''判断升级后的钱包文件是否存在'''
            if os.path.exists(fpath+test_config.wallet_name_db3_upgrade):
                flag = True
            else:
                flag = False
            self.ASSERT(flag, "upgraded files do not exist")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_021_upgradewallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有000test000.json文件'''
            if os.path.exists(fpath+test_config.wallet_name_notexist):
                os.remove(fpath+test_config.wallet_name_notexist)
            API.cli().upgrade_wallet(filepath=test_config.wallet_name_notexist,exceptfunc = lambda msg: msg.find("File does not exist") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_022_upgradewallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''新建一个后缀错误的钱包'''
            if os.path.exists(fpath+test_config.wallet_name_exist_wrong):
                os.remove(fpath+test_config.wallet_name_exist_wrong)
            f = open(fpath+test_config.wallet_name_exist_wrong, 'w')
            f1 = open(fpath+test_config.wallet_name_json, 'r')
            indata = f1.read()
            f.write(indata)
            f.close()
            f1.close()
            API.cli().upgrade_wallet(filepath=test_config.wallet_name_exist_wrong,exceptfunc = lambda msg: msg.find("Can't upgrade the wallet file.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_024_upgradewallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''复制一个db3格式的钱包并重命名'''
            if os.path.exists(fpath+test_config.wallet_name_exist_erroecode_db3):
                os.remove(fpath+test_config.wallet_name_exist_erroecode_db3)
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            shutil.copy(fpath+test_config.wallet_name_db3,fpath+test_config.wallet_name_exist_erroecode_db3)
            API.cli().upgrade_wallet(filepath=test_config.wallet_name_exist_erroecode_db3,password=test_config.wallet_password, exceptfunc = lambda msg: msg.find("File does not exist") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_025_upgradewallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            API.cli().create_wallet(filepath=test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().upgrade_wallet(filepath=test_config.wallet_name_json, exceptfunc = lambda msg: msg.find("Can't upgrade the wallet file.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            

    def test_026_upgradewallet(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''新建一个内容为空的钱包'''
            if os.path.exists(fpath+test_config.wallet_name_null):
                os.remove(fpath+test_config.wallet_name_null)
            f = open(fpath+test_config.wallet_name_null, 'w')
            f.close()
            API.cli().upgrade_wallet(filepath=test_config.wallet_name_null,password=test_config.wallet_password, exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")             

    def test_028_upgradewallet(self):
        try:
            API.cli().upgrade_wallet(exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
      
    def test_029_rebuildindex(self):
        try:
            '''获取当前节点路径'''

            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            API.cli().create_wallet(filepath=test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)
            API.cli().rebuild_index()
            API.cli().show_state(10)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "rebuildindex failed")
            '''查看区块高度与钱包高度是否一致'''
            lastline = climsg[climsg.rfind("block: "):]
            try:
                blockheight = lastline.split("block: ")[1].split("/")[0]
            except:
                self.ASSERT(False, "can not get wallet height")                
            walletheight = API.rpc(test_config.node_default).getwalletheight()
            print(blockheight)
            print(walletheight)
            if blockheight.strip() == str(walletheight).strip():
                flag=True
            else:
                flag=False 
            self.ASSERT(flag, "rebuildindex failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")                
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")                

    def test_030_rebuildindex(self):
        try:
            API.cli().rebuild_index(exceptfunc = lambda msg: msg.find("error") < 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")            
   
    def test_031_listaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().list_address(exceptfunc = lambda msg: msg.find(test_config.wallet_default_address) >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "list address failed")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
  
    def test_032_listaddress(self):
        try:
            API.cli().list_address(exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
   
    def test_033_listasset(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            '''查看wallet_5.json的Neo资产'''
            API.cli().list_asset(exceptfunc = lambda msg: msg.find(test_config.asset_neo_id) >= 0)        
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "list asset failed1")
            try:
                str=climsg.split("name:NEO")[1].split("balance:")[1].split("\n")[0]
            except:
                self.ASSERT(False, "can not get NeoGas balance value")
            '''调用getbalance查看Neo资产，看是否一致'''            
            asset = API.rpc(test_config.node_default).getbalance(test_config.asset_neo_id)["balance"]
            if str.strip() == asset.strip():
                flag=True
            else:
                flag=False 
            self.ASSERT(flag, "list asset failed2")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
  
    def test_034_listasset(self):
        try:
            API.cli().list_asset(exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
  
    def test_035_listkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().list_key(exceptfunc = lambda msg: msg.find(test_config.wallet_default_pubkey) >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "list publickey failed")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    
    
    def test_036_listkey(self):
        try:
            API.cli().list_key(exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_037_showutxo(self):
        try:
            '''show utxo , list address'''
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().list_address(exceptfunc = lambda msg: msg.find(test_config.wallet_default_address) >= 0)
            API.cli().show_utxo(exceptfunc = lambda msg: msg.find("UTXOs") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "show utxo failed1")
            '''将所有交易txid存入list，传入gettxout方法，返回的地址信息与list address比对'''
            try:
                count = int(climsg.split("total: ")[1].split(" UTXOs")[0])
            except:
                self.ASSERT(False, "can not get total UTXOs count")
            try:
                msg = climsg.split("show utxo")[1].split("total")[0].strip().split("\n")
            except:
                self.ASSERT(False, "can not get UTXOs message")
            i = 0
            str = []
            while i < count:
                str.append(msg[i])
                logger.print(str[i])
                i += 1
            i = 0
            while i < count:
                try:            
                    getaddress = API.rpc(test_config.node_default).gettxout(''.join(str[i]).split(":")[0], ''.join(str[i]).split(":")[1])
                except:
                    self.ASSERT(False, "can not get address")                    
                i += 1
                flag = climsg.find(''.join(getaddress))
                if flag ==False:
                    break                 
            self.ASSERT(flag, "show utxo failed2")                        
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_038_showutxo(self):
        try:
            API.cli().show_utxo(exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_039_showutxo(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().list_address(exceptfunc = lambda msg: msg.find(test_config.wallet_default_address) >= 0)
            API.cli().show_utxo(test_config.asset_neo_id,exceptfunc = lambda msg: msg.find("UTXOs") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "show utxo failed1")
            try:
                count = int(climsg.split("total: ")[1].split(" UTXOs")[0])
            except:
                self.ASSERT(False, "can not get total UTXOs count")
            try:
                msg = climsg.split(test_config.asset_neo_id)[1].split("total")[0].strip().split("\n")
            except:
                self.ASSERT(False, "can not get UTXOs message")
            i = 0
            str = []
            while i < count:
                str.append(msg[i])
                logger.print(str[i])
                i += 1
            i = 0
            while i < count:
                try:
                    getaddress = API.rpc(test_config.node_default).gettxout(''.join(str[i]).split(":")[0], ''.join(str[i]).split(":")[1])
                except:
                    self.ASSERT(False, "can not get address")
                i += 1
                flag = climsg.find(''.join(getaddress))
                if flag ==False:
                    break                 
            self.ASSERT(flag, "show utxo failed2")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_041_showutxo(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().show_utxo(test_config.asset_notexist_id,exceptfunc = lambda msg: msg.find("0 UTXOs") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_042_showutxo(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().show_utxo(test_config.asset_wrong_str_id,exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_043_showutxo(self):
        try:
            API.cli().show_utxo(test_config.asset_neo_id,exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_044_showutxo(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)        
            API.cli().show_utxo(test_config.alias_right,exceptfunc = lambda msg: msg.find("UTXOs") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "Can't show utxo1")
            try:
                count = int(climsg.split("total: ")[1].split(" UTXOs")[0])
            except:
                self.ASSERT(False, "can not get total UTXOs count")
            try:
                msg = climsg.split("show utxo neo")[1].split("total")[0].strip().split("\n")
            except:
                self.ASSERT(False, "can not get UTXOs message")
            i = 0
            str = []
            while i < count:
                str.append(msg[i])
                logger.print(str[i])
                i += 1
            i = 0
            while i < count:
                try:            
                    getaddress = API.rpc(test_config.node_default).gettxout(''.join(str[i]).split(":")[0], ''.join(str[i]).split(":")[1])
                except:
                    self.ASSERT(False, "can not get address")
                i += 1
                flag = climsg.find(''.join(getaddress))
                if flag ==False:
                    break                 
            self.ASSERT(flag, "show utxo failed2")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_046_showutxo(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)        
            API.cli().show_utxo(test_config.alias_notexist,exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
 
    def test_048_showgas(self):
        try:
            plus=0
            
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().show_gas(exceptfunc = lambda msg: msg.find("unavailable") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "show gas failed1")
            count1 = API.rpc(test_config.node_default).getblockcount()
            try:
                number1 = float(climsg.split("unavailable: ")[1].split("\n")[0].strip())
            except:
                self.ASSERT(False, "show gas failed2")
            result0 = API.cli().waitsync()
            self.ASSERT(result0 , "show_state waitsync failed")
            API.cli().terminate()
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().show_gas(exceptfunc = lambda msg: msg.find("unavailable") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "show gas failed3")
            count2 = API.rpc(test_config.node_default).getblockcount()
            try:
                number2 = float(climsg.split("unavailable: ")[1].split("\n")[0].strip())
            except:
                self.ASSERT(False, "show gas failed4")
                result0 = API.cli().waitsync()
                self.ASSERT(result0 , "show_state waitsync failed")
            API.cli().terminate()

            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().show_gas(exceptfunc = lambda msg: msg.find("unavailable") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "show gas failed5")
            count3 = API.rpc(test_config.node_default).getblockcount()
            try:
                number3 = float(climsg.split("unavailable: ")[1].split("\n")[0].strip())
            except:
                self.ASSERT(False, "show gas failed6")
            # logger.print(climsg)
            # self.ASSERT(result, "show gas failed1")
            print (number1)
            print (number2)
            print (number3)
            
            if number1 == number2 or number2 == number3:
                plus=0
                API.cli().terminate()
            else:   
                if round((number2-number1)/(int(count2)-int(count1)),8) == round((number3-number2)/(int(count3)-int(count2)),8):
                    flag=True
                else:
                    flag=False                
                self.ASSERT(flag, "gas value not match")
                plus=1
                
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
  
    def test_049_showgas(self):
        try:
            API.cli().show_gas(exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
  
    def test_050_claimgas(self):
        try:
        
            #从wallet_5向wallet_4转账10000neo
            
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            #API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_neo, WalletManager().wallet(test_config.wallet6node).account().address(), value="10000",fee=None)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            result0 = API.cli().waitsync()
            self.ASSERT(result0 , "show_state waitsync failed")
            API.cli().terminate()
            
            #获取钱包4gas
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_password)
            API.cli().list_asset(exceptfunc = lambda msg: msg.find("balance") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            try:            
                str1=climsg.split("name:NeoGas")[1].split("balance:")[1].split("\n")[0]
            except:
                str1=0
            print(str1)                             
            API.cli().terminate()
            
            ##从wallet_4向wallet_5转账100gas
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_password)             
            API.cli().send(test_config.wallet_password,test_config.asset_neo_id, test_config.wallet_default_address , "1000", fee=0,exceptfunc = lambda msg: msg.find("TXID") >= 0)
            API.cli().show_state(times=10)
            API.cli().waitnext(timeout=15, times=1)
            (result, stepname, climsg) = API.cli().exec(False)
            ###等一个区块

            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            result0 = API.cli().waitsync()
            self.ASSERT(result0 , "show_state waitsync failed")
            API.cli().terminate()

            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)                     
            API.cli().show_gas(exceptfunc = lambda msg: msg.find("unavailable") >= 0)           
            API.cli().claim_gas(exceptfunc = lambda msg: msg.find("Tranaction") >= 0)
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "claim gas failed")
            ###等一个区块
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            result0 = API.cli().waitsync()
            self.ASSERT(result0 , "show_state waitsync failed")
            try:            
                str2=climsg.split("  available:")[1].split("\n")[0]
            except:
                self.ASSERT(False, "can not get available NeoGas value")           
            API.cli().terminate()            
            
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_password)             
            API.cli().list_asset()
            (result, stepname, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(result, "claim gas failed")            
            try:            
                str3=climsg.split("name:NeoGas")[1].split("balance:")[1].split("\n")[0]
            except:
                self.ASSERT(False, "list asset failed")
                                          
            logger.print(str1)
            logger.print(str2)
            logger.print(str3)
            if round(float(str3),8) == round(float(str1),8)+round(float(str2),8):
              
                flag=True
            else:
                flag=False 
            self.ASSERT(flag, "neoGas not match")            
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

  
    def test_051_claimgas(self):
        try:
            API.cli().claim_gas(exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >=0 )
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
  
    '''批量创建100个地址'''    
    def test_052_createaddress(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().list_address()
            API.cli().create_address(test_config.n_right,exceptfunc = lambda msg: msg.find("export addresses to address.txt") >= 0,timeout=200)
            API.cli().list_address()
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "create address failed1")
            try:
                count0 =climsg.split("create address")[0].count("Standard",0,len(climsg))
            except:
                self.ASSERT(False, "can not get address count0")
            try:                
                count1 =climsg.split("create address")[1].count("Standard",0,len(climsg))
            except:
                self.ASSERT(False, "can not get address count1")
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()            
            fpath2 = open(fpath+"address.txt",'r')
            count2 = len(fpath2.readlines())
            fpath2.close()            
            if count2 == (count1-count0):
                flag=True
            else:
                flag=False 
            self.ASSERT(flag, "create address failed2")
            try:
                str1 = climsg.split("Standard")[count0+count1-1]
            except:
                self.ASSERT(False, "can not get the last address")
            with open(fpath+"address.txt", 'r') as f:  
                lines = f.readlines() #####读取所有行
                last_line = lines[-1] #####取最后一行            
            if str1.strip() == last_line.strip():
                flag=True
            else:
                flag=False
            f.close()                
            self.ASSERT(flag, "create address failed3")        
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    '''创建1个地址'''        
    def test_053_createaddress(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().list_address()            
            API.cli().create_address(exceptfunc = lambda msg: msg.find("export addresses to address.txt") >= 0,timeout=5)
            API.cli().list_address()
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "create address failed1")
            try:
                count0 =climsg.split("create address")[0].count("Standard",0,len(climsg))
            except:
                self.ASSERT(False, "can not get address count0")
            try:                
                count1 =climsg.split("create address")[1].count("Standard",0,len(climsg))
            except:
                self.ASSERT(False, "can not get address count1")
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            logger.print(test_config.ConfigPath+"config.json")
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            logger.print(fpath)    
            fpath2 = open(fpath+"address.txt",'r')
            count2 = len(fpath2.readlines())
            fpath2.close()            
            if count2 == (count1-count0):
                flag=True
            else:
                flag=False 
            self.ASSERT(flag, "create address failed2")
            try:            
                str1 = climsg.split("Standard")[count0+count1-1]
            except:
                self.ASSERT(False, "can not get the last address")
            with open(fpath+"address.txt", 'r') as f:  
                lines = f.readlines() ####读取所有行
                last_line = lines[-1] ####取最后一行            
            if str1.strip() == last_line.strip():
                flag=True
            else:
                flag=False
            f.close()                
            self.ASSERT(flag, "create address failed3")                    
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
     
    def test_054_createaddress(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()        
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().create_address(test_config.n_wrong_str,exceptfunc = lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_056_createaddress(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()        
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().create_address(test_config.n_zero,exceptfunc = lambda msg: msg.find("export addresses to address.txt") >= 0,timeout=5)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "Can't create address1")
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            logger.print(test_config.ConfigPath+"config.json")
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            logger.print(fpath)    
            fpath2 = open(fpath+"address.txt",'r')
            count2 = len(fpath2.readlines())
            fpath2.close()
            if count2 == 0:
                flag=True
            else:
                flag=False 
            self.ASSERT(flag, "create address failed2")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
     
    def test_057_createaddress(self):
        try:
            API.cli().create_address(test_config.n_right,exceptfunc = lambda msg: msg.find("You have to open the wallet first.") >=0 )
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception") 

    def test_058_importkey(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()        
            '''导出wallet_5.json的一个私钥'''
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            API.cli().create_wallet(filepath=test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_password)
            API.cli().export_key(test_config.wallet_password,WalletManager().wallet(test_config.node_default).account().address(),None)
            (result, stepname, climsg) = API.cli().exec()
            logger.info("[test_058_importkey] climsg: {0}".format(climsg))
            self.ASSERT(result, "export key failed1")
            try:
                str1 =climsg.split("********")[4].split("neo>")[0].strip()
            except:
                self.ASSERT(False, "can not get key")
            logger.info("[test_058_importkey] export private key: " + str1)
            API.cli().terminate()
            '''wallet_5.json的私钥导入test.json'''
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)            
            API.cli().import_key(wif_path=str1,exceptfunc = lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >=0 )
            '''导出test.json的私钥，与wallet_5.json的私钥对比'''            
            API.cli().export_key(test_config.wallet_password,exceptfunc=lambda msg: msg.find(str1)>= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.info("[test_058_importkey] climsg: {0}".format(climsg))
            self.ASSERT(result, "import key failed2")                         
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
 
    def test_059_importkey(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()        
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            API.cli().create_wallet(filepath=test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)
            API.cli().import_key(test_config.wif_notexist,exceptfunc = lambda msg: msg.find("address") >=0 )
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "Can't import key")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_060_importkey(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()        
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            API.cli().create_wallet(filepath=test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)
            API.cli().import_key(test_config.wif_wrong_str,exceptfunc = lambda msg: msg.find("error") >=0 )
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
             
    def test_061_importkey(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()       
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            API.cli().create_wallet(filepath=test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)
            API.cli().import_key(wif_path=None, exceptfunc = lambda msg: msg.find("error") >=0 )
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_062_importkey(self):
        try:
            API.cli().import_key(test_config.wif_right,exceptfunc = lambda msg: msg.find("error") >=0 )
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_063_importkey(self):
        try:
            '''导出test.json的全部私钥到当前节点的akey.txt文件'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            if os.path.exists(fpath+test_config.pathname):
                os.remove(fpath+test_config.pathname)
            if os.path.exists(fpath+test_config.wallet_name_json):
                os.remove(fpath+test_config.wallet_name_json)
            if os.path.exists(fpath+test_config.wallet_name_db3):
                os.remove(fpath+test_config.wallet_name_db3)
            API.cli().create_wallet(filepath=test_config.wallet_name_json, password=test_config.wallet_password, password2=test_config.wallet_password, exceptfunc=(lambda msg: msg.find("address") >= 0))
            API.cli().create_wallet(filepath=test_config.wallet_name_db3, password=test_config.wallet_password,password2=test_config.wallet_password, exceptfunc=lambda msg: msg.find("address") >= 0)
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)
            API.cli().export_key(test_config.wallet_password,None,fpath+test_config.pathname)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "export key failed1")                
            API.cli().terminate()
            '''将akey.txt文件中的私钥导入至test223.db3'''
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_name_db3, test_config.wallet_password)
            API.cli().import_key(fpath+test_config.pathname)
            '''导出test223.db3的私钥'''
            API.cli().export_key(test_config.wallet_password)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "import key failed2")
            f = open(fpath+test_config.pathname, mode='r', encoding='utf-8')
            line = f.readline() 
            while line:
                flag = climsg.find(line)            
                line = f.readline()
            f.close() 
            self.ASSERT(flag != -1, "create address failed2")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_064_importkey(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            fp.close()
            '''确保没有1allkeys1.txt文件'''
            if os.path.exists(fpath+test_config.path_notexist):
                os.remove(fpath+test_config.path_notexist)
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)
            API.cli().import_key(test_config.path_notexist,exceptfunc = lambda msg: msg.find("error") >=0 )
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)            
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    

    def test_065_importkey(self):
        try:
            '''获取当前节点路径'''
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            '''新建一个后缀错误的path'''
            if os.path.exists(fpath+test_config.path_wrong):
                os.remove(fpath+test_config.path_wrong)
            f = open(fpath+test_config.path_wrong, 'w')
            API.cli().open_wallet(test_config.wallet_name_json, test_config.wallet_password)
            API.cli().import_key(test_config.path_wrong,exceptfunc = lambda msg: msg.find("error") < 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.info("[test_065_importkey] climsg: {0}".format(climsg))
            fp.close()            
            f.close()            
            self.ASSERT(result, "error message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    '''新添加的case，测version'''
    def test_157_version(self):
        try:
            API.cli().version()
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)
            result = str(climsg).find("2.9.3.0")            
            self.ASSERT(result, "version message not match")
        except AssertError as e:        
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    '''新添加的case，测help'''
    def test_158_help(self):
        try:
            API.cli().help()
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)
            result = str(climsg).find("create wallet")            
            self.ASSERT(result, "help message not match")
        except AssertError as e:        
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    '''新添加的case，测clear'''
    def test_159_clear(self):
        try:
            API.cli().clear()
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)    
            self.ASSERT(result, "clear failed")
        except AssertError as e:        
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    '''新添加的case，测exit'''
    '''exec()默认自带exit'''
    def test_160_exit(self):
        try:
            (result, stepname, climsg) = API.cli().exec()          
            logger.print(climsg)    
            self.ASSERT(result, "exit failed")
        except AssertError as e:        
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")            
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")    


    
    
    
    
    
    
    
    
    
    
    #address和path不填
    def test_069_exportkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            API.cli().export_key(test_config.wallet_pwd, exceptfunc=lambda msg: msg.find(test_config.key) >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "")
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
    def test_070_exportkey(self):
        try:
            API.cli().export_key(test_config.wallet_pwd, exceptfunc=lambda msg: msg.find("You have to open the wallet first") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result, "")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_071_exportkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            filename=test_config.filename
            API.cli().export_key(test_config.wallet_pwd,WalletManager().wallet(test_config.node_default).account().address(),filename)
            (result, stepname, climsg) = API.cli().exec()
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            flag=os.path.exists(fpath+filename)
            self.ASSERT(flag, "file not exists")
            with open(fpath+filename, mode='r', encoding='utf-8') as f:
                str=f.readline()
                str=str.split("\n")[0]
                if str==test_config.key:
                    flag=True
                else:
                    flag=False
                print (flag)
            f.close()
            logger.print(climsg)
            self.ASSERT(flag, "key not right")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_072_exportkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            filename=test_config.filename
            API.cli().export_key(test_config.wallet_pwd,None,filename)
            (result, stepname, climsg) = API.cli().exec()
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            flag=os.path.exists(fpath+filename)
            self.ASSERT(flag, "file not exists")
            with open(fpath+filename, mode='r', encoding='utf-8') as f:
                str=f.readline()
                str=str.split("\n")[0]
                if str==test_config.key:
                    flag=True
                else:
                    flag=False
                print (flag)
            logger.print(climsg)
            self.ASSERT(flag, "key not right")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_073_exportkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            filename=test_config.filename
            API.cli().export_key(test_config.wallet_pwd,test_config.address_notexist,filename,exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_075_exportkey(self):
        try:
            API.cli().list_address()
            filename=test_config.filename
            API.cli().export_key(test_config.wallet_pwd,WalletManager().wallet(test_config.node_default).account().address(),filename,exceptfunc=lambda msg: msg.find("You have to open the wallet first") >= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_077_exportkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            API.cli().export_key(test_config.wallet_pwd,WalletManager().wallet(test_config.node_default).account().address(),None, exceptfunc=lambda msg: msg.find(test_config.key)>= 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_078_exportkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            filename=test_config.filename
            API.cli().export_key(test_config.wallet_pwd,WalletManager().wallet(test_config.node_default).account().address(),filename)
            (result, stepname, climsg) = API.cli().exec()
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            flag=os.path.exists(fpath+filename)
            self.ASSERT(flag,"file not exists")
            with open(fpath+filename, mode='r', encoding='utf-8') as f:
                str=f.readline()
                str=str.split("\n")[0]
                if str==test_config.key:
                    flag=True
                else:
                    flag=False
                print (flag)
            logger.print(climsg)                
            self.ASSERT(flag, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #bug
    def test_079_exportkey(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            filename=test_config.wrongfilename
            API.cli().export_key(test_config.wallet_pwd,WalletManager().wallet(test_config.node_default).account().address(),filename, exceptfunc=lambda msg: msg.find("error") < 0)
            (result, stepname, climsg) = API.cli().exec()
            logger.print(climsg)
            self.ASSERT(result, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    
    
    def test_082_send(self):
        try:
            ##事前获取
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()            
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")

            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            try:
                addr2Neo=self.return_neo_gas(res2,True)
            except:
                addr2Neo=0
            try:
                addr2Gas=self.return_neo_gas(res2,False)
            except:
                addr2Gas=0
            API.cli().terminate()
        

            #从wallet_5向wallet_6转账10neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, WalletManager().wallet(test_config.wallet6node).account().address(), value="10",fee=None)
            (result, stepname, msg1) = API.cli().exec(False)
            logger.print(msg1)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #API.cli().terminate()

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
    
    
    
    def test_083_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_notexist, WalletManager().wallet(test_config.node_default).account().address(), "10",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    
    def test_085_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,None,WalletManager().wallet(test_config.node_default).account().address(), "10",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_086_send(self):
        try:
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_notexist,WalletManager().wallet(test_config.node_default).account().address(), "10",exceptfunc=lambda msg: msg.find("You have to open the wallet first") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    
    def test_087_send(self):
        try:
            ##事前获取
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            try:
                addr2Neo=self.return_neo_gas(res2,True)
            except:
                addr2Neo=0
            try:
                addr2Gas=self.return_neo_gas(res2,False)
            except:
                addr2Gas=0
            API.cli().terminate()
        

            #从wallet_5向wallet_6转账10neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,"NEO", WalletManager().wallet(test_config.wallet6node).account().address(), value="10",fee=None)
            (result, stepname, msg1) = API.cli().exec(False)
            logger.print(msg1)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #API.cli().terminate()

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
            
    def test_088_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.wrong_str,WalletManager().wallet(test_config.node_default).account().address(), "10",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_092_send(self):
        try:
            #获取wallet_6余额
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)

            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            logger.print(msg)
            w2neobalance1=0
            try:    
                w2neobalance1=msg.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            except:
                w2neobalance1=0
            API.cli().terminate()
            
            #从wallet_5向wallet_6转账10neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, WalletManager().wallet(test_config.wallet6node).account().address(), "10")
            (result, stepname, msg1) = API.cli().exec(False)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()            
            #获取转账后的neo值
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            (result, stepname, msg2) = API.cli().exec(False)
            logger.print(msg1)
            logger.print(msg2)
            API.cli().terminate()
            neobalance1=msg1.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            neobalance2=msg2.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            gasbalance1=msg1.split("NeoGas\n")[1].split("balance:")[1].split("\n")[0]
            gasbalance2=msg2.split("NeoGas\n")[1].split("balance:")[1].split("\n")[0]
            print ("**********************neobalance1:"+neobalance1+"************")
            print ("**********************neobalance2:"+neobalance2+"************")
            print ("**********************gasbalance1:"+gasbalance1+"************")
            print ("**********************gasbalance2:"+gasbalance2+"************")
            plus1=float(neobalance1)-float(neobalance2)
            plus2=float(gasbalance1)-float(gasbalance2)
            
            #获取钱包2的NEO
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            w2neobalance2=msg.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            print ("**********************w2neobalance1:"+str(w2neobalance1)+"************")
            print ("**********************w2neobalance2:"+w2neobalance2+"************")
            plus3=float(w2neobalance2)-float(w2neobalance1)
            flag=False
            if int(plus1)==10 and int(plus2)==0 and int(plus3)==10:
                flag=True
            self.ASSERT(flag,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    
    def test_093_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,None, "10",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    ###address不存在情况会error
    def test_094_send(self):
        try:
            #获取不存在的地址的余额
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            (result, stepname, msg2) = API.cli().exec(False)
            res1=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            w2neobalance1=0
            w2gasbalance1=0
            if res1==None:
                w2neobalance1=0
                w2gasbalance1=0
            else:
                w2neobalance1=self.return_neo_gas(res1,True)
                w2gasbalance1=self.return_neo_gas(res1,False)
            API.cli().terminate()
            
            #从wallet_5向不存在的地址转账10neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, test_config.address_notexist, "10")
            (result, stepname, msg1) = API.cli().exec(False)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            #获取转账后的neo值
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            (result, stepname, msg2) = API.cli().exec(False)
            logger.print(msg1)
            logger.print(msg2)
            API.cli().terminate()
            neobalance1=msg1.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            neobalance2=msg2.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            gasbalance1=msg1.split("NeoGas\n")[1].split("balance:")[1].split("\n")[0]
            gasbalance2=msg2.split("NeoGas\n")[1].split("balance:")[1].split("\n")[0]
            print ("**********************neobalance1:"+neobalance1+"************")
            print ("**********************neobalance2:"+neobalance2+"************")
            print ("**********************gasbalance1:"+gasbalance1+"************")
            print ("**********************gasbalance2:"+gasbalance2+"************")
            plus1=float(neobalance1)-float(neobalance2)
            plus2=float(gasbalance1)-float(gasbalance2)
            
            #获取不存在的地址的余额
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            (result, stepname, msg2) = API.cli().exec(False)
            res1=API.rpc(test_config.node_default).getaccountstate(test_config.address_notexist);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            w2neobalance2=self.return_neo_gas(res1,True)
            w2gasbalance2=self.return_neo_gas(res1,False)
            # API.cli().terminate()
            
            print ("**********************w2neobalance1:"+str(w2neobalance1)+"************")
            print ("**********************w2neobalance2:"+str(w2neobalance2)+"************")
            print ("**********************w2neobalance2:"+str(w2gasbalance1)+"************")
            print ("**********************w2neobalance2:"+str(w2gasbalance2)+"************")
            plus3=float(w2neobalance2)-float(w2neobalance1)
            plus4=float(w2gasbalance2)-float(w2gasbalance1)
            
            ##计算结果
            value=10
            gasvalue=0
            fee=0
            self.ASSERT(plus3==value, "arrive address neo check")
            self.ASSERT(plus1==value, "send address neo check")
            self.ASSERT(plus2==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(round(plus4)==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_095_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,test_config.wrong_str, "10",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
            
    
    def test_098_send(self):
        try:
            #获取wallet_6余额
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            logger.print(msg)
            w2neobalance1=0
            try:    
                w2neobalance1=msg.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            except:
                w2neobalance1=0
            API.cli().terminate()
            
            #从wallet_5向wallet_6转账10neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, WalletManager().wallet(test_config.wallet6node).account().address(), "0")
            (result, stepname, msg1) = API.cli().exec(False)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()            
            #获取转账后的neo值
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            (result, stepname, msg2) = API.cli().exec(False)
            logger.print(msg1)
            logger.print(msg2)
            API.cli().terminate()
            try:
                neobalance1=msg1.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
                neobalance2=msg2.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
                gasbalance1=msg1.split("NeoGas\n")[1].split("balance:")[1].split("\n")[0]
                gasbalance2=msg2.split("NeoGas\n")[1].split("balance:")[1].split("\n")[0]
            except:
                self.ASSERT(False,"error:get neo balance failed")
            print ("**********************neobalance1:"+neobalance1+"************")
            print ("**********************neobalance2:"+neobalance2+"************")
            print ("**********************gasbalance1:"+gasbalance1+"************")
            print ("**********************gasbalance2:"+gasbalance2+"************")
            plus1=float(neobalance1)-float(neobalance2)
            plus2=float(gasbalance1)-float(gasbalance2)
            
            #获取钱包2的NEO
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            try:
                w2neobalance2=msg.split("NEO\n")[1].split("balance:")[1].split("\n")[0]
            except:
                self.ASSERT(False,"error:get neo balance failed")
            print ("**********************w2neobalance1:"+str(w2neobalance1)+"************")
            print ("**********************w2neobalance2:"+w2neobalance2+"************")
            plus3=float(w2neobalance2)-float(w2neobalance1)
            flag=False
            if int(plus1)==0 and int(plus2)==0 and int(plus3)==0:
                flag=True
            self.ASSERT(flag,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_099_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, WalletManager().wallet(test_config.wallet6node).account().address(), value=None,fee=None,exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_100_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,WalletManager().wallet(test_config.wallet6node).account().address(), test_config.wrong_str,exceptfunc=lambda msg: msg.find("Incorrect Amount Format") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_101_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,WalletManager().wallet(test_config.wallet6node).account().address(), "1000000000",exceptfunc=lambda msg: msg.find("Insufficient funds") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_102_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,WalletManager().wallet(test_config.wallet6node).account().address(), "-1",exceptfunc=lambda msg: msg.find("Negative values cannot be sent") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
                        
    def test_104_send(self):
        try:
            #从钱包5向钱包6转账100neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, test_config.wallet_default3address, value="100")
            (result, stepname, msg1) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
             
            ##事前获取
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default3, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            logger.print(msg)
            res1=API.rpc(test_config.node_default).getaccountstate(test_config.wallet_default3address);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            neobalance1=self.return_neo_gas(res1,True)
            gasbalance1=self.return_neo_gas(res1,False)
            w2neobalance1=0
            w2gasbalance1=0
            try:
                w2neobalance1=self.return_neo_gas(res2,True)
            except:
                w2neobalance1=0
            try:
                w2gasbalance1=self.return_neo_gas(res2,False)
            except:
                w2gasbalance1=0
            API.cli().terminate()
            
            #从wallet_7向wallet_6转账所有neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default3, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, WalletManager().wallet(test_config.wallet6node).account().address(), value="all",fee=None)
            (result, stepname, msg1) = API.cli().exec(False)
            logger.print(msg1)
            #等一个block
            ##事后获取
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(test_config.wallet_default3address);
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            neobalance2=0
            gasbalance2=0
            try:
                neobalance2=self.return_neo_gas(res1,True)
            except:
                neobalance2=0
            try:
                gasbalance2=self.return_neo_gas(res1,False)
            except:
                gasbalance2=0
            w2neobalance2=self.return_neo_gas(res2,True)
            w2gasbalance2=self.return_neo_gas(res2,False)
            print ("**********************neobalance1:"+str(neobalance1)+"************")
            print ("**********************neobalance2:"+str(neobalance2)+"************")
            print ("**********************gasbalance1:"+str(gasbalance1)+"************")
            print ("**********************gasbalance2:"+str(gasbalance2)+"************")
            print ("**********************w2neobalance1:"+str(w2neobalance1)+"************")
            print ("**********************w2neobalance2:"+str(w2neobalance2)+"************")
            print ("**********************w2neobalance1:"+str(w2gasbalance1)+"************")
            print ("**********************w2neobalance2:"+str(w2gasbalance2)+"************")
            plus1=float(neobalance1)-float(neobalance2)
            plus2=float(gasbalance1)-float(gasbalance2)
            plus3=float(w2neobalance2)-float(w2neobalance1)
            plus4=float(w2gasbalance2)-float(w2gasbalance1)
            #计算结果
            value=float(neobalance1)
            gasvalue=0
            fee=0
            self.ASSERT(plus3==value, "arrive address neo check")
            self.ASSERT(plus1==value, "send address neo check")
            self.ASSERT(plus2==round(gasvalue+fee,8), "send address gas check") 
            self.ASSERT(plus4==gasvalue, "arrive address gas check") 
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_105_send(self):
        try:
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,WalletManager().wallet(test_config.wallet6node).account().address(), "1",exceptfunc=lambda msg: msg.find("You have to open the wallet first") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_106_send(self):
        try:
            ##事前获取
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            try:
                addr2Neo=self.return_neo_gas(res2,True)
            except:
                addr2Neo=0
            try:
                addr2Gas=self.return_neo_gas(res2,False)
            except:
                addr2Gas=0
            API.cli().terminate()
        

            #从wallet_5向wallet_6转账10neo,1gas
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, WalletManager().wallet(test_config.wallet6node).account().address(), value="10",fee="1")
            (result, stepname, msg1) = API.cli().exec(False)
            logger.print(msg1)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #API.cli().terminate()

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
            
    def test_107_send(self):
        try:
            ##事前获取
            API.cli().open_wallet(test_config.wallet_default2, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            try:
                addr2Neo=self.return_neo_gas(res2,True)
            except:
                addr2Neo=0
            try:
                addr2Gas=self.return_neo_gas(res2,False)
            except:
                addr2Gas=0
            API.cli().terminate()
        

            #从wallet_5向wallet_6转账10neo,1gas
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().show_state(times=10)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right, WalletManager().wallet(test_config.wallet6node).account().address(), value="0",fee="0")
            (result, stepname, msg1) = API.cli().exec(False)
            logger.print(msg1)
            #等一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.wallet6node).account().address());
            self.ASSERT(res1!=None, "get getaccountstate error2!")
            self.ASSERT(res2!=None, "get getaccountstate error2!")
            addr1Neo2=self.return_neo_gas(res1,True)
            addr1Gas2=self.return_neo_gas(res1,False)
            addr2Neo2=self.return_neo_gas(res2,True)
            addr2Gas2=self.return_neo_gas(res2,False)
            #API.cli().terminate()

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
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_108_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,WalletManager().wallet(test_config.wallet6node).account().address(), "1",test_config.wrong_str,exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_109_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,WalletManager().wallet(test_config.wallet6node).account().address(), "1","1000000000",exceptfunc=lambda msg: msg.find("Insufficient funds") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_110_send(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().send(test_config.wallet_pwd,test_config.asset_id_right,WalletManager().wallet(test_config.wallet6node).account().address(), "1","-1",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    
    def test_112_import_multisigaddress(self):
        try:
            # # #从钱包5内默认地址向钱包5内multi地址转10neo（RPC）
            # #API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().show_state(10)
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            if res2!=None:
                addr2Neo=self.return_neo_gas(res2,True)
                addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.mutiaddress, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "")
            self.ASSERT(result["net_fee"]=="0", "")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate("Ae5FRbhndo2XKRFqEQ9Mn99bRbeKqHLxWV");
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
            API.cli().terminate()
            #从mutiaddress向钱包5默认地址转5Neo，获取第一次生成的交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().show_state(times=10)  
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                test_config.mutiaddress,
                WalletManager().wallet(test_config.node_default).account().address(), value=5,fee=0,change_address=test_config.mutiaddress)
            self.ASSERT(result!=None, "")
            json1=str(result)
            print("++++++++++++++:"+json1)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            #确认存在后使用relay方法广播jsonObject(cli，需要检查结果，应该广播不出去)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            API.cli().terminate()
            logger.print(msg)
            flag1=False
            if msg.find("The signature is incomplete.")>=0:
                flag1=True
            self.ASSERT(flag1, "relay1 failed")
            # #先sign交易json，获取输出的json，需要检查，如果没有输出json则报错
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)            
            API.cli().list_asset()
            API.cli().sign(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(str(msg).find("Signed Output")>=0, "failed to sign")
            #在relay前确认钱包5默认地址余额和mutiaddress内余额
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            w5neo1=self.return_neo_gas(res1,True)
            muneo1=self.return_neo_gas(res2,True)
            API.cli().terminate()
            try:
                json2=msg.split("Signed Output:\n\n")[1].split("\n")[0]
            except:
                self.ASSERT(False,"error:unable to get json2")
            # #relay输出的交易json，需要检查结果，应该广播成功
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json2)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            flag2=False
            if msg.find("success")>=0:
                flag2=True
            self.ASSERT(flag2, "relay2 failed")
            # #等待一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            # #检查钱包5内默认地址的余额是否增加5neo(RPC),mutiaddress内是否减少5neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            logger.print(msg)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            w5neo2=self.return_neo_gas(res1,True)
            muneo2=self.return_neo_gas(res2,True)
            plus1=float(w5neo2)-float(w5neo1)
            plus2=float(muneo1)-float(muneo2)
            print(str(w5neo1)+"  "+str(w5neo2)+"  "+str(muneo1)+"  "+str(muneo2))
            self.ASSERT(int(plus1)==5, "send address neo check")
            self.ASSERT(int(plus2)==5, "arrive address neo check")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_114_import_multisigaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().import_multisigaddress(None,[test_config.key1,test_config.key2],exceptfunc=lambda msg: msg.find("Error. Use at least 2 public keys to create a multisig address.") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_115_import_multisigaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().import_multisigaddress("abc",[test_config.key1,test_config.key2],exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_116_import_multisigaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().import_multisigaddress("3",[test_config.key1,test_config.key2],exceptfunc=lambda msg: msg.find("Error. Invalid parameters") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_117_import_multisigaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().import_multisigaddress("0",[test_config.key1,test_config.key2],exceptfunc=lambda msg: msg.find("Error. Invalid parameters") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_118_import_multisigaddress(self):
        try:
            API.cli().import_multisigaddress("2",[test_config.key1,test_config.key2],exceptfunc=lambda msg: msg.find("You have to open the wallet first") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_120_import_multisigaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().import_multisigaddress("2",None,exceptfunc=lambda msg: msg.find("Error. Use at least 2 public keys to create a multisig address.") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_121_import_multisigaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().import_multisigaddress("2",[test_config.key3,test_config.key2],exceptfunc=lambda msg: msg.find("Multisig. Addr.: APkNTWRpoJCCxn7YR6Jc7ALCExGMGLsrp4") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_122_import_multisigaddress(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().import_multisigaddress("2",['abc',test_config.key2],exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_123_import_multisigaddress(self):
        try:
            API.cli().import_multisigaddress("2",[test_config.key1,test_config.key2],exceptfunc=lambda msg: msg.find("You have to open the wallet first") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    
    
    
    def test_124_jsonObjectToSign(self):
        try:
            # # #从钱包5内默认地址向钱包5内multi地址转10neo（RPC）
            # #API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().show_state(10)
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            if res2!=None:
                addr2Neo=self.return_neo_gas(res2,True)
                addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.mutiaddress, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "sendfrom failed")
            self.ASSERT(result["net_fee"]=="0", "")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate("Ae5FRbhndo2XKRFqEQ9Mn99bRbeKqHLxWV");
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
            API.cli().terminate()
            #从mutiaddress向钱包5默认地址转5Neo，获取第一次生成的交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().show_state(times=10)  
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                test_config.mutiaddress,
                WalletManager().wallet(test_config.node_default).account().address(), value=5,fee=0,change_address=test_config.mutiaddress)
            self.ASSERT(result!=None, "sendfrom failed")
            json1=str(result)
            print("++++++++++++++:"+json1)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            #确认存在后使用relay方法广播jsonObject(cli，需要检查结果，应该广播不出去)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            API.cli().terminate()
            logger.print(msg)
            flag1=False
            if msg.find("The signature is incomplete.")>=0:
                flag1=True
            self.ASSERT(flag1, "relay1 failed")
            # #先sign交易json，获取输出的json，需要检查，如果没有输出json则报错
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().sign(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(str(msg).find("Signed Output")>=0, "failed to sign")
            #在relay前确认钱包5默认地址余额和mutiaddress内余额
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            w5neo1=self.return_neo_gas(res1,True)
            muneo1=self.return_neo_gas(res2,True)
            API.cli().terminate()
            try:
                json2=msg.split("Signed Output:\n\n")[1].split("\n")[0]
            except:
                self.ASSERT(False,"error:unable to get json2")
            # #relay输出的交易json，需要检查结果，应该广播成功
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json2)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            flag2=False
            if msg.find("success")>=0:
                flag2=True
            self.ASSERT(flag2, "relay2 failed")
            # #等待一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            # #检查钱包5内默认地址的余额是否增加5neo(RPC),mutiaddress内是否减少5neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            logger.print(msg)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            w5neo2=self.return_neo_gas(res1,True)
            muneo2=self.return_neo_gas(res2,True)
            plus1=float(w5neo2)-float(w5neo1)
            plus2=float(muneo1)-float(muneo2)
            print(str(w5neo1)+"  "+str(w5neo2)+"  "+str(muneo1)+"  "+str(muneo2))
            self.ASSERT(int(plus1)==5, "sign failed")
            self.ASSERT(int(plus2)==5, "sign failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #jsonObjectToSign不填
    def test_125_jsonObjectToSign(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().sign(jsonobj=None)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(str(msg).find("You must input JSON object pending signature data.")>=0, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #重复签名
    def test_126_jsonObjectToSign(self):
        try:
            # # #从钱包5内默认地址向钱包5内multi地址转10neo（RPC）
            # #API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().show_state(10)
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.mutiaddress, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "sendfrom failed")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            #从mutiaddress向钱包5默认地址转5Neo，获取第一次生成的交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().show_state(times=10)  
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                test_config.mutiaddress,
                WalletManager().wallet(test_config.node_default).account().address(), value=5,fee=0,change_address=test_config.mutiaddress)
            self.ASSERT(result!=None, "sendfrom failed")
            json1=str(result)
            print("++++++++++++++:"+json1)
            time.sleep(20)
            API.cli().terminate()
            # #先sign交易json，获取输出的json，需要检查，如果没有输出json则报错
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().sign(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            
            
            API.cli().terminate()
            logger.print(msg)
            self.ASSERT(str(msg).find("Signed Output")>=0, "failed to sign")
            try:
                json2=msg.split("Signed Output:\n\n")[1].split("\n")[0]
            except:
                self.ASSERT(False, "first sign failed")
            ##重复sign交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().sign(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            API.cli().terminate()
            logger.print(msg)
            self.ASSERT(str(msg).find("Signed Output")>=0, "failed to sign")
            try:
                json3=msg.split("Signed Output:\n\n")[1].split("\n")[0]
            except:
                self.ASSERT(False, "second sign failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #jsonObjectToSign格式错误
    def test_127_jsonObjectToSign(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().sign(jsonobj="abc")
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(str(msg).find("One of the identified items was in an invalid format.")>=0, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #未打开钱包
    def test_128_jsonObjectToSign(self):
        try:
            # # #从钱包5内默认地址向钱包5内multi地址转10neo（RPC）
            # #API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().show_state(10)
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            if res2!=None:
                addr2Neo=self.return_neo_gas(res2,True)
                addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.mutiaddress, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "sendfrom failed")
            self.ASSERT(result["net_fee"]=="0", "")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate("Ae5FRbhndo2XKRFqEQ9Mn99bRbeKqHLxWV");
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
            API.cli().terminate()
            #从mutiaddress向钱包5默认地址转5Neo，获取第一次生成的交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().show_state(times=10)  
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                test_config.mutiaddress,
                WalletManager().wallet(test_config.node_default).account().address(), value=5,fee=0,change_address=test_config.mutiaddress)
            self.ASSERT(result!=None, "sendfrom failed")
            json1=str(result)
            print("++++++++++++++:"+json1)
            time.sleep(20)
            API.cli().terminate()
            # #未打开钱包的状态下sign交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().list_asset()
            API.cli().sign(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            API.cli().terminate()
            logger.print(msg)
            self.ASSERT(str(msg).find("You have to open the wallet first.")>=0, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_129_relay(self):
        try:
            # # #从钱包5内默认地址向钱包5内multi地址转10neo（RPC）
            # #API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().show_state(10)
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            try:
                addr2Neo=self.return_neo_gas(res2,True)
            except:
                addr2Neo=0
            try:
                addr2Gas=self.return_neo_gas(res2,False)
            except:
                addr2Gas=0
            # if res2!=None:
                # addr2Neo=self.return_neo_gas(res2,True)
                # addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.mutiaddress, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "sendfrom failed")
            self.ASSERT(result["net_fee"]=="0", "net_fee false")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate("Ae5FRbhndo2XKRFqEQ9Mn99bRbeKqHLxWV");
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
            API.cli().terminate()
            #从mutiaddress向钱包5默认地址转5Neo，获取第一次生成的交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().show_state(times=10)  
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                test_config.mutiaddress,
                WalletManager().wallet(test_config.node_default).account().address(), value=5,fee=0,change_address=test_config.mutiaddress)
            self.ASSERT(result!=None, "sendfrom failed")
            json1=str(result)
            print("++++++++++++++:"+json1)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            #确认存在后使用relay方法广播jsonObject(cli，需要检查结果，应该广播不出去)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            API.cli().terminate()
            logger.print(msg)
            flag1=False
            if msg.find("The signature is incomplete.")>=0:
                flag1=True
            self.ASSERT(flag1, "relay1 failed")
            # #先sign交易json，获取输出的json，需要检查，如果没有输出json则报错
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().sign(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(str(msg).find("Signed Output")>=0, "failed to sign")
            #在relay前确认钱包5默认地址余额和mutiaddress内余额
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            w5neo1=self.return_neo_gas(res1,True)
            muneo1=self.return_neo_gas(res2,True)
            API.cli().terminate()
            try:
                json2=msg.split("Signed Output:\n\n")[1].split("\n")[0]
            except:
                self.ASSERT(False,"error:unable to get json2")
            # #relay输出的交易json，需要检查结果，应该广播成功
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json2)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            flag2=False
            if msg.find("success")>=0:
                flag2=True
            self.ASSERT(flag2, "relay2 failed")
            # #等待一个block
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            # #检查钱包5内默认地址的余额是否增加5neo(RPC),mutiaddress内是否减少5neo
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().rebuild_index()
            API.cli().show_state(times=10)
            API.cli().list_asset()
            (result, stepname, msg) = API.cli().exec(False)
            waitsyncRes=API.cli().waitsync(timeoout=120)
            self.ASSERT(waitsyncRes, "wait waitsync error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            logger.print(msg)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            w5neo2=self.return_neo_gas(res1,True)
            muneo2=self.return_neo_gas(res2,True)
            plus1=float(w5neo2)-float(w5neo1)
            plus2=float(muneo1)-float(muneo2)
            print(str(w5neo1)+"  "+str(w5neo2)+"  "+str(muneo1)+"  "+str(muneo2))
            self.ASSERT(int(plus1)==5, "sign failed")
            self.ASSERT(int(plus2)==5, "sign failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #jsonObjectToSign不填
    def test_130_relay(self):
        try:
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().relay(jsonobj=None)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(msg.find("You must input JSON object to relay")>=0, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #jsonObjectToSign不完整
    def test_131_relay(self):
        try:
            # # #从钱包5内默认地址向钱包5内multi地址转10neo（RPC）
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().show_state(10)
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            if res2!=None:
                addr2Neo=self.return_neo_gas(res2,True)
                addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.mutiaddress, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "sendfrom failed")
            self.ASSERT(result["net_fee"]=="0", "net_fee false")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate("Ae5FRbhndo2XKRFqEQ9Mn99bRbeKqHLxWV");
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
            API.cli().terminate()
            #从mutiaddress向钱包5默认地址转5Neo，获取第一次生成的交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().show_state(times=10)  
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                test_config.mutiaddress,
                WalletManager().wallet(test_config.node_default).account().address(), value=5,fee=0,change_address=test_config.mutiaddress)
            self.ASSERT(result!=None, "sendfrom failed")
            json1=str(result)
            print("++++++++++++++:"+json1)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            #确认存在后使用relay方法广播jsonObject(cli，需要检查结果，应该广播不出去)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            API.cli().terminate()
            logger.print(msg)
            flag1=False
            if msg.find("The signature is incomplete.")>=0:
                flag1=True
            self.ASSERT(flag1, "assert error")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #jsonObjectToSign="abc"
    def test_132_relay(self):
        try:
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().relay(jsonobj=test_config.wrong_str)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(msg.find("One of the identified items was in an invalid format.")>=0, "assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    #未打开钱包进行relay
    def test_133_relay(self):
        try:
            # # #从钱包5内默认地址向钱包5内multi地址转10neo（RPC）
            # #API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address(lambda msg: msg.find(WalletManager().wallet(test_config.node_default).account().address()) >= 0)
            API.cli().show_state(10)
            (status, info, climsg) = API.cli().exec(False)
            logger.print(climsg)
            self.ASSERT(status, info)
            ##事前获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            addr1Neo=self.return_neo_gas(res1,True)
            addr1Gas=self.return_neo_gas(res1,False)
            addr2Neo=0
            addr2Gas=0
            if res2!=None:
                addr2Neo=self.return_neo_gas(res2,True)
                addr2Gas=self.return_neo_gas(res2,False)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                WalletManager().wallet(test_config.node_default).account().address(),
                test_config.mutiaddress, value=10,fee=0,change_address="empty")
            self.ASSERT(result!=None, "sendfrom failed")
            self.ASSERT(result["net_fee"]=="0", "")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            ##事后获取
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate("Ae5FRbhndo2XKRFqEQ9Mn99bRbeKqHLxWV");
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
            API.cli().terminate()
            #从mutiaddress向钱包5默认地址转5Neo，获取第一次生成的交易json
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.mutiname, test_config.wallet_pwd)
            API.cli().show_state(times=10)  
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).sendfrom(test_config.asset_id_right,
                test_config.mutiaddress,
                WalletManager().wallet(test_config.node_default).account().address(), value=5,fee=0,change_address=test_config.mutiaddress)
            self.ASSERT(result!=None, "sendfrom failed")
            json1=str(result)
            print("++++++++++++++:"+json1)
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            waitblockRes=API.node(test_config.node_default).wait_gen_block()
            self.ASSERT(waitblockRes, "wait block error!")
            API.cli().terminate()
            #确认存在后使用relay方法广播jsonObject(cli，需要检查结果，应该广播不出去)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().relay(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            API.cli().terminate()
            logger.print(msg)
            flag1=False
            if msg.find("The signature is incomplete.")>=0:
                flag1=True
            self.ASSERT(flag1, "relay1 failed")
            # #先sign交易json，获取输出的json，需要检查，如果没有输出json则报错
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_asset()
            API.cli().sign(jsonobj=json1)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(str(msg).find("Signed Output")>=0, "failed to sign")
            #在relay前确认钱包5默认地址余额和mutiaddress内余额
            res1=API.rpc(test_config.node_default).getaccountstate(WalletManager().wallet(test_config.node_default).account().address());
            res2=API.rpc(test_config.node_default).getaccountstate(test_config.mutiaddress);
            self.ASSERT(res1!=None, "get getaccountstate error1!")
            self.ASSERT(res2!=None, "get getaccountstate error1!")
            w5neo1=self.return_neo_gas(res1,True)
            muneo1=self.return_neo_gas(res2,True)
            API.cli().terminate()
            try:
                json2=msg.split("Signed Output:\n\n")[1].split("\n")[0]
            except:
                self.ASSERT(False,"error:unable to get json2")
            # #不打开前钱包，relay输出的交易json，需要检查结果，应该广播成功
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().relay(jsonobj=json2)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            self.ASSERT(msg.find("success")>=0, "wallet not open")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_134_showstate(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().show_state(2)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            #加一句waitsync,会return true/false，直接作为结果即可
            result=API.cli().waitsync()
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_135_shownode(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().show_node(exceptfunc=lambda msg: msg.find("error: command not found") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.info("[test_135_shownode] msg: {0}".format(msg))
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_136_showpool(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            API.cli().show_state(times=10)
            API.cli().send(password=test_config.wallet_pwd, id_alias="NEO",address=test_config.address_right, value=10)
            API.cli().waitnext(timeout=1, times=1)
            API.cli().show_pool()
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            #发完send交易后立即发showpool，total的值应该为1
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    
    def test_138_export_all_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            content=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            path=Config.NODES[test_config.node_default]["walletname"]
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            
            #导出0to30的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_blocks(start="0",count="30",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to30.acc")
            print ("export 0to30.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            
            #导入0to30区块
            #把protocol.json文件替换为SeedList被删除的文件
            shutil.copyfile(test_config.copypath+"protocol_deleted.json", fpath+"protocol.json")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #复制0to30.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to30.acc", fpath+"chain.0.acc")
            print ("copy file 0to30.acc success")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()

            #导出所有区块(0to30)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_all_blocks(path="chainAll.acc",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chainAll.acc", test_config.copypath+"chainAll.acc")
            print ("export chainAll.acc success")
            if os.path.exists(fpath+"chainAll.acc"):
                os.remove(fpath+"chainAll.acc")
            #复制chainAll.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chainAll.acc", fpath+"chainAll.acc")
            print ("copy file chainAll.acc success")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #启动节点，判断区块数是否是30
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            flag=False
            if result==30:
                flag=True
            
            #最后还原之前的区块
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            #复制chain.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chain.acc", fpath+"chain.acc")
            print ("copy file chain.acc success")
            #把protocol.json文件替换为SeedList未被删除的文件
            shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(test_config.node_default) + "/protocol.json", fpath+"protocol.json")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            self.ASSERT(flag,"export blocks failed")  
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_139_export_all_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            content=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            path=Config.NODES[test_config.node_default]["walletname"]
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            
            #导出0to30的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_blocks(start="0",count="30",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to30.acc")
            print ("export 0to30.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            
            #导入0to30区块
            #把protocol.json文件替换为SeedList被删除的文件
            shutil.copyfile(test_config.copypath+"protocol_deleted.json", fpath+"protocol.json")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #复制0to30.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to30.acc", fpath+"chain.0.acc")
            print ("copy file 0to30.acc success")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()

            #导出所有区块(0to30)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_all_blocks(path="chainAll.acc",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chainAll.acc", test_config.copypath+"chainAll.acc")
            print ("export chainAll.acc success")
            if os.path.exists(fpath+"chainAll.acc"):
                os.remove(fpath+"chainAll.acc")
            #复制chainAll.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chainAll.acc", fpath+"chainAll.acc")
            print ("copy file chainAll.acc success")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #启动节点，判断区块数是否是30
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            flag=False
            if result==30:
                flag=True
            
            #最后还原之前的区块
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            #复制chain.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chain.acc", fpath+"chain.acc")
            print ("copy file chain.acc success")
            #把protocol.json文件替换为SeedList未被删除的文件
            shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(test_config.node_default) + "/protocol.json", fpath+"protocol.json")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            self.ASSERT(flag,"export blocks failed")  
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_140_export_all_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            content=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            path=Config.NODES[test_config.node_default]["walletname"]
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            
            #导出0to30的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_blocks(start="0",count="30",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to30.acc")
            print ("export 0to30.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            
            #导入0to30区块
            #把protocol.json文件替换为SeedList被删除的文件
            shutil.copyfile(test_config.copypath+"protocol_deleted.json", fpath+"protocol.json")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #复制0to30.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to30.acc", fpath+"chain.0.acc")
            print ("copy file 0to30.acc success")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            
            #导出所有区块(0to30)
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_all_blocks(timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.acc", test_config.copypath+"chainAll.acc")
            print ("export chainAll.acc success")
            if os.path.exists(fpath+"chain.acc"):
                os.remove(fpath+"chain.acc")
            #复制chainAll.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chainAll.acc", fpath+"chain.acc")
            print ("copy file chainAll.acc success")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #启动节点，判断区块数是否是30
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            flag=False
            if result==30:
                flag=True
            
            #最后还原之前的区块
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            #复制chain.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chain.acc", fpath+"chain.acc")
            print ("copy file chain.acc success")
            #把protocol.json文件替换为SeedList未被删除的文件
            shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(test_config.node_default) + "/protocol.json", fpath+"protocol.json")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            self.ASSERT(flag,"export blocks failed")  
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_141_export_all_blocks(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().export_all_blocks("wrongpath/chain.acc",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_142_export_all_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            content=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            if os.path.exists(fpath+"chain.abc"):
                os.remove(fpath+"chain.abc")
                print ("file deleted")
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            filename=test_config.filename2
            API.cli().export_all_blocks(fpath+"chain.abc")
            (result, stepname, msg) = API.cli().exec()
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            logger.print(msg)
            flag=os.path.exists(fpath+"chain.abc")
            if os.path.exists(fpath+"chain.abc"):
                os.remove(fpath+"chain.abc")
                print ("file deleted")
            self.ASSERT(flag,"export blocks failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    #ok
    def test_144_export_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            content=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            path=Config.NODES[test_config.node_default]["walletname"]
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            
            #导出0to29的区块
            API.cli().export_blocks(start="0",count="29",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            ##copy 时候的路径需要获取了进行split再拼接
            ##SAMPLE:testpath=NODES["path"].split("/")xxxxxxx
            
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to29.acc")
            print ("export 0to29.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            #导出0to30的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_blocks(start="0",count="30",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to30.acc")
            print ("export 0to30.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            #导出30to50的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_blocks(start="30",count="20",timeout=30)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.30.acc", test_config.copypath+"30to50.acc")
            print ("export 30to50.acc success")
            if os.path.exists(fpath+"chain.30.acc"):
                os.remove(fpath+"chain.30.acc")
            
            #把protocol.json文件替换为SeedList被删除的文件
            shutil.copyfile(test_config.copypath+"protocol_deleted.json", fpath+"protocol.json")
            print ("change protocol.json success")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            
            
            #复制0to29.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to29.acc", fpath+"chain.0.acc")
            print ("copy file 0to29.acc success")
            
            #启动节点，判断区块数是否为29
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            a=0
            if result==29:
                print("blocks count:29")
                a=1
            
            #删除0to29.acc
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
                print ("delete file:0to29.acc")
            #复制30to50.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"30to50.acc", fpath+"chain.30.acc")
            print ("copy file 30to50.acc success")
            #启动节点，判断区块数是否还是29
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            b=0
            if result==29:
                b=1
            
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #复制0to30.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to30.acc", fpath+"chain.0.acc")
            print ("copy file 0to30.acc success")
            #启动节点，判断区块数是否是50
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            c=0
            if result==50:
                c=1
            
            
            #最后还原之前的区块
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            #复制chain.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chain.acc", fpath+"chain.acc")
            print ("copy file chain.acc success")
            #把protocol.json文件替换为SeedList未被删除的文件
            shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(test_config.node_default) + "/protocol.json", fpath+"protocol.json")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            sum=a+b+c
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            self.ASSERT(sum==3,"export blocks failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
    def test_146_export_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            #API.cli().export_blocks(start="0",count="31",timeout=35)
            API.cli().export_blocks(start="abc",count="10",timeout=5,exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

    def test_147_export_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            API.cli().export_blocks("100000000","10",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            #删除所有.acc的文件
            if os.path.exists(fpath+"chain.100000000.acc"):
                os.system("rm -rf "+fpath+"*.acc")
                self.ASSERT(False, "error:can generate .acc file")
            print ("Delete ALL ACC FILE")
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_148_export_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            content=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            path=Config.NODES[test_config.node_default]["walletname"]
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            
            #导出0to29的区块
            API.cli().export_blocks(start="0",count="29",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            ##copy 时候的路径需要获取了进行split再拼接
            ##SAMPLE:testpath=NODES["path"].split("/")xxxxxxx
            
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to29.acc")
            print ("export 0to29.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            #导出0to30的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_blocks(start="0",count="30",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to30.acc")
            print ("export 0to30.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            #导出30to50的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().export_blocks(start="30",count="20",timeout=30)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            shutil.copyfile(fpath+"chain.30.acc", test_config.copypath+"30to50.acc")
            print ("export 30to50.acc success")
            if os.path.exists(fpath+"chain.30.acc"):
                os.remove(fpath+"chain.30.acc")
            
            #把protocol.json文件替换为SeedList被删除的文件
            shutil.copyfile(test_config.copypath+"protocol_deleted.json", fpath+"protocol.json")
            print ("change protocol.json success")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            
            
            #复制0to29.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to29.acc", fpath+"chain.0.acc")
            print ("copy file 0to29.acc success")
            
            #启动节点，判断区块数是否为29
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            a=0
            if result==29:
                print("blocks count:29")
                a=1
            
            #删除0to29.acc
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
                print ("delete file:0to29.acc")
            #复制30to50.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"30to50.acc", fpath+"chain.30.acc")
            print ("copy file 30to50.acc success")
            #启动节点，判断区块数是否还是29
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            b=0
            if result==29:
                b=1
            
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #复制0to30.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to30.acc", fpath+"chain.0.acc")
            print ("copy file 0to30.acc success")
            #启动节点，判断区块数是否是50
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            c=0
            if result==50:
                c=1
            
            
            #最后还原之前的区块
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            #复制chain.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chain.acc", fpath+"chain.acc")
            print ("copy file chain.acc success")
            #把protocol.json文件替换为SeedList未被删除的文件
            shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(test_config.node_default) + "/protocol.json", fpath+"protocol.json")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            sum=a+b+c
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            self.ASSERT(sum==3,"export blocks failed")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_149_export_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            path=Config.NODES[test_config.node_default]["walletname"]
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")

            #导出0to101的区块
            API.cli().export_blocks(start="0",count="101",timeout=150)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            ##copy 时候的路径需要获取了进行split再拼接
            ##SAMPLE:testpath=NODES["path"].split("/")xxxxxxx
            
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to101.acc")
            print ("export 0to101.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            
            #把protocol.json文件替换为SeedList被删除的文件
            shutil.copyfile(test_config.copypath+"protocol_deleted.json", fpath+"protocol.json")
            print ("change protocol.json success")
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            

            #复制0to101.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to101.acc", fpath+"chain.0.acc")
            print ("copy file 0to101.acc success")
            
            #启动节点，判断区块数是否为101
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            a=0
            if result==101:
                print("blocks count:101")
                a=1
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            #导出0to29的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().export_blocks(start="0",count="29",timeout=35)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            #复制0to29.acc到外部文件夹
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to29.acc")
            print ("export 0to29.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            #导出0to30的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().export_blocks(start="0",count="30",timeout=40)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            #复制0to30.acc到外部文件夹
            shutil.copyfile(fpath+"chain.0.acc", test_config.copypath+"0to30.acc")
            print ("export 0to30.acc success")
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
            ##测试重点
            #导出30toall的区块
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().export_blocks(start="30",count=None,timeout=100)
            (result, stepname, msg) = API.cli().exec()
            API.cli().terminate()
            #复制30toall.acc到外部文件夹
            shutil.copyfile(fpath+"chain.30.acc", test_config.copypath+"30toall.acc")
            print ("export 30toall.acc success")
            if os.path.exists(fpath+"chain.30.acc"):
                os.remove(fpath+"chain.30.acc")
            ##导出结束，开始导入    
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #复制0to29.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to29.acc", fpath+"chain.0.acc")
            print ("copy file 0to29.acc success")
            #启动节点，判断区块数是否还是29
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            d=0
            if result==29:
                d=1
            #删除0to29.acc
            if os.path.exists(fpath+"chain.0.acc"):
                os.remove(fpath+"chain.0.acc")
                print ("delete file:0to29.acc")
            #复制30toall.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"30toall.acc", fpath+"chain.30.acc")
            print ("copy file 30toall.acc success")
            #启动节点，判断区块数是否还是29
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            b=0
            if result==29:
                b=1
            
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #复制0to30.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"0to30.acc", fpath+"chain.0.acc")
            print ("copy file 0to30.acc success")
            #启动节点，判断区块数是否是101
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            (result, stepname, msg) = API.cli().exec(False)
            result = API.rpc(test_config.node_default).getblockcount()
            API.cli().terminate()
            c=0
            if result==101:
                c=1
            
            
            #最后还原之前的区块
            #删除Chain和Index文件夹
            for root , dirs, files in os.walk(fpath):
                for name in dirs:
                    if 'Chain_' in name or 'Index_' in name:
                        print ("delete file:"+name)
                        filename=fpath+name+"/"
                        shutil.rmtree(filename)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            #复制chain.acc到当前运行节点文件夹
            shutil.copyfile(test_config.copypath+"chain.acc", fpath+"chain.acc")
            print ("copy file chain.acc success")
            #把protocol.json文件替换为SeedList未被删除的文件
            shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", fpath+"protocol.json")
            #启动节点
            API.cli().init(self._testMethodName, Config.NODES[test_config.node_default]["path"])
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().list_address()
            (result, stepname, msg) = API.cli().exec(False)
            logger.print(msg)
            result = API.rpc(test_config.node_default).getblockcount()
            sum=a+b+c+d
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            print (a)
            print (b)
            print (c)
            print (d)
            self.ASSERT(sum==4,"export blocks failed")

        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    
    def test_150_export_blocks(self):
        try:
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().export_blocks("5","abc",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            self.ASSERT(result,"message not match")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_151_export_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            if os.path.exists(fpath+"chain.5.acc"):
                os.remove(fpath+"chain.5.acc")
                print ("file deleted")
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().export_blocks("0","10000000",timeout=10,exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            #删除所有.acc的文件
            os.system("rm -rf "+fpath+"*.acc")
            print ("Delete ALL ACC FILE")
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    def test_152_export_blocks(self):
        try:
            fp = open(test_config.ConfigPath+"/config.json", 'r', encoding='utf-8')
            str=fp.read()
            fp.close()
            fp.close()
            fpath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            if os.path.exists(fpath+"chain.5.acc"):
                os.remove(fpath+"chain.5.acc")
                print ("file deleted")
            API.cli().export_blocks("5","0",exceptfunc=lambda msg: msg.find("error") >= 0)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            if os.path.exists(fpath+"chain.5.acc"):
                os.system("rm -rf "+fpath+"*.acc")
                self.ASSERT(False, "error:can generate .acc file")
            print ("Delete ALL ACC FILE")
            self.ASSERT(result,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
            
    # def test_153_start_consensus(self):
        # try: 
            # #关闭四个共识节点
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # API.clirpc(node_index).terminate()
            # time.sleep(10)
            # # delete files(需要删除区块链及所有.acc文件)
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                        # logger.info("begin clear " + str(node_index) + "\n")
                        # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"*.acc")
                        # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Chain_*")
                        # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Index_*")
            # time.sleep(10)
            # fpath=Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            # #删除Chain和Index文件夹
            # for root , dirs, files in os.walk(fpath):
                # for name in dirs:
                    # if 'Chain_' in name or 'Index_' in name:
                        # print ("delete file:"+name)
                        # filename=fpath+name+"/"
                        # shutil.rmtree(filename)
            # #删除所有.acc的文件
            # os.system("rm -rf "+fpath+"*.acc")
            # # 将protocol.json copy 到所有节点内替换原有的文件
            # #从源文件中copy出需要的.acc文件放到对应根目录
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                        # API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/consensus/" + "protocol_new.json", remotenodepath + "protocol.json", node_index, "put")
                        # #API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/" + "chain.acc", remotenodepath + "chain.acc", node_index, "put")
            # #copy
            # os.system("cp "+Config.RESOURCE_PATH + "/consensus/" + "protocol_new.json"+" "+fpath+"protocol.json")
            # #os.system("cp "+Config.RESOURCE_PATH + "/nodes/" + "chain.acc"+" "+fpath+"chain.acc")
            # # 启动123节点
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # print(node_index)
                        # API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                        # API.clirpc(node_index).exec(False)
            
            # # 启动自己，open wallet,start consensus
            # API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            # API.cli().start_consensus(exceptfunc=lambda msg: msg.find("OnStart") >= 0)
            
            # # 等待一段时间（5个区块），确认是否出现 send prepare response命令
            # API.cli().waitnext(timeout=30,times=2)
            # (result, stepname, msg) = API.cli().exec()
            # #logger.print(msg)
            
            # #获取node5的打印的信息
            # node5str=API.cli().readmsg()
            # logger.print(node5str)
            
            # #恢复
            # #关闭四个共识节点
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # API.clirpc(node_index).terminate()
            # time.sleep(10)
            # # delete files(需要删除区块链及所有.acc文件)
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                        # logger.info("begin clear " + str(node_index) + "\n")
                        # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"*.acc")
                        # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Chain_*")
                        # API.node(node_index).exec_cmd("rm -rf " + remotenodepath+"Index_*")
            # time.sleep(10)
            # #删除Chain和Index文件夹

            # for root , dirs, files in os.walk(fpath):
                # for name in dirs:
                    # if 'Chain_' in name or 'Index_' in name:
                        # print ("delete file:"+name)
                        # filename=fpath+name+"/"
                        # shutil.rmtree(filename)
            # #删除所有.acc的文件
            # os.system("rm -rf "+fpath+"*.acc")
            # # 将protocol.json copy 到所有节点内替换原有的文件
            # #从源文件中copy出需要的.acc文件放到对应根目录
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # remotenodepath = Config.NODES[node_index]["path"].replace("neo-cli.dll", "")
                        # API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", remotenodepath + "protocol.json", node_index, "put")
                        # #API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", remotenodepath + "protocol.json", node_index, "put")
                        # API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/" + "chain.acc", remotenodepath + "chain.acc", node_index, "put")
            # #copy
            # os.system("cp "+Config.RESOURCE_PATH + "/nodes/node" + str(test_config.node_default+1) + "/protocol.json"+" "+fpath+"protocol.json")            # 将protocol.json copy 到所有节点内替换原有的文件
            # #把protocol.json文件替换为最初的文件
            # #nodepath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            # #shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", nodepath+"protocol.json")
            # os.system("cp "+Config.RESOURCE_PATH + "/nodes/" + "chain.acc"+" "+fpath+"chain.acc")
            # # 启动当前节点
            # for node_index in range(len(Config.NODES)):
                # if "consensusnode" in Config.NODES[node_index]:
                    # if Config.NODES[node_index]["consensusnode"]:
                        # API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                        # API.clirpc(node_index).exec(False)
            # time.sleep(10)
            # self.ASSERT(str(node5str).find("send prepare response")>=0,"start consensus node failed")
            # #判断完毕后，不论是否通过，一律需要恢复protocol.json文件，并清空区块链，将原本需要的.acc 文件 copy进去
        
        # except AssertError as e:
            # logger.error(e.msg)
            # self.ASSERT(False, "error:assert")
        # except RPCError as e:
            # logger.error(e.msg)
            # self.ASSERT(False, "error:rpc")
        # except Exception as e:
            # logger.error(traceback.format_exc())
            # self.ASSERT(False, "error:Exception")
            
    def test_153_start_consensus(self):
        try: 
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
                        API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/consensus/" + "protocol_new.json", remotenodepath + "protocol.json", node_index, "put")
                        #API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/" + "chain.acc", remotenodepath + "chain.acc", node_index, "put")
            #copy
            os.system("cp "+Config.RESOURCE_PATH + "/consensus/" + "protocol_new.json"+" "+fpath+"protocol.json")
            #os.system("cp "+Config.RESOURCE_PATH + "/nodes/" + "chain.acc"+" "+fpath+"chain.acc")
            # 启动123节点
            for node_index in range(len(Config.NODES)):
                if "consensusnode" in Config.NODES[node_index]:
                    if Config.NODES[node_index]["consensusnode"]:
                        print(node_index)
                        API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                        API.clirpc(node_index).exec(False)
            
            # 启动自己，open wallet,start consensus
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().start_consensus(exceptfunc=lambda msg: msg.find("OnStart") >= 0)
            
            # 等待一段时间（5个区块），确认是否出现 send prepare response命令
            API.cli().waitnext(timeout=30,times=2)
            (result, stepname, msg) = API.cli().exec()
            #logger.print(msg)
            
            #获取node5的打印的信息
            node5str=API.cli().readmsg()
            logger.print(node5str)
            
            #恢复
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
                        API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", remotenodepath + "protocol.json", node_index, "put")
                        API.node(node_index).sftp_transfer(Config.RESOURCE_PATH + "/nodes/" + "chain.acc", remotenodepath + "chain.acc", node_index, "put")
            #copy
            os.system("cp "+Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json"+" "+fpath+"protocol.json")            # 将protocol.json copy 到所有节点内替换原有的文件
            #把protocol.json文件替换为SeedList未被删除的文件
            nodepath = Config.NODES[test_config.node_default]["path"].replace("neo-cli.dll", "")
            shutil.copyfile(Config.RESOURCE_PATH + "/nodes/node" + str(node_index + 1) + "/protocol.json", nodepath+"protocol.json")
            os.system("cp "+Config.RESOURCE_PATH + "/nodes/" + "chain.acc"+" "+fpath+"chain.acc")
            # 启动当前节点
            for node_index in range(len(Config.NODES)):
                if "consensusnode" in Config.NODES[node_index]:
                    if Config.NODES[node_index]["consensusnode"]:
                        API.clirpc(node_index).init("start_node", Config.NODES[node_index]["path"])
                        API.clirpc(node_index).exec(False)
            time.sleep(10)
            self.ASSERT(str(node5str).find("send prepare response")>=0,"start consensus node failed")
            #判断完毕后，不论是否通过，一律需要恢复protocol.json文件，并清空区块链，将原本需要的.acc 文件 copy进去
        
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")
    
            
    def test_154_start_consensus(self):
        try:    
            #处理方法：开启共识后等待5个区块生成后，检查log里是否存在send prepare response，只要不存在就ok，存在fail
            API.cli().open_wallet(test_config.wallet_default, test_config.wallet_pwd)
            API.cli().start_consensus(exceptfunc=lambda msg: msg.find("OnStart") >= 0)
            API.cli().show_state(10)
            (result, stepname, msg) = API.cli().exec()
            logger.print(msg)
            flag=True
            if str(msg).find("send prepare response")>=0:
                flag=False
            self.ASSERT(flag,"assert not equal")
        except AssertError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:assert")
        except RPCError as e:
            logger.error(e.msg)
            self.ASSERT(False, "error:rpc")
        except Exception as e:
            logger.error(traceback.format_exc())
            self.ASSERT(False, "error:Exception")

if __name__ == '__main__':
    unittest.main()
