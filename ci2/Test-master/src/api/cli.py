# -*- coding:utf-8 -*-
import time
import subprocess
import threading
import os
import re

# import utils.config
from utils.logger import LoggerInstance as logger

readlock = threading.Lock()


class CLIReadThread(threading.Thread):
    def __init__(self, process, name="cliprocess"):
        super(CLIReadThread, self).__init__()
        self.name = name
        self.process = process
        self.readlines = ""
        self.statefinish = False
        self.terminate = False

    def lines(self):
        return self.readlines

    def isfinish(self):
        return self.statefinish

    # attemp to read block state three times, when three times attemped is all blocked, we think it is really bolcked
    def isblock(self):
        global readlock
        if readlock.acquire(timeout=3):
            readlock.release()
            return False
        else:
            print("is blocked")
            return True

    def clear(self):
        self.readlines = ""

    def run(self):
        trycount = 0
        while True:
            if self.terminate is True:
                self.process.wait()
                self.process.stdout.close()
                self.process.stdin.close()
                logger.print("msg thread terminate success.")
                break
            global readlock
            readlock.acquire()
            line = self.process.stdout.readline()
            readlock.release()
            if line != "":
                self.readlines += re.sub('\x1b.*?m', '', line).replace("\x00", "").replace("\x1b[H\x1b[2J", "")
                logger.print(self.name + "--" + re.sub('\x1b.*?m', '', line).replace("\x00", "").replace("\x1b[H\x1b[2J", ""))
                pass
            else:
                # if trycount > 2:
                    # self.statefinish = True
                    # self.process.wait()
                    # self.process.stdout.close()
                    # self.process.stdin.close()
                    # break
                # else:
                    # trycount += 1
                if 2 < trycount:
                    self.statefinish = True
                    time.sleep(0.5)


class CLIApi:
    # version   显示当前软件的版本
    def __init__(self, scriptname="", neopath=""):
        # step index
        self.logfile = None
        self.readthread = None
        self.process = None
        self.init(scriptname, neopath)

    def init(self, scriptname, neopath):
        # step index
        self.stepindex = 0
        # step except functions
        self.stepexceptfuncs = {}
        # scripts folder
        self.prefixful = "cliscripts"
        self.scriptname = scriptname
        self.neopath = neopath
        self.scriptpath = ""

        if self.scriptname == "":
            return
        self.scriptpath = self.prefixful + "/" + scriptname + ".sh"
        if not os.path.exists(self.prefixful):
            os.makedirs(self.prefixful)

        if self.logfile is not None:
            self.logfile.close()
        self.logfile = open(self.scriptpath, "w")  # 打开文件
        self.logfile.write("#!/usr/bin/expect\n")
        self.logfile.write("cd " + neopath.replace("neo-cli.dll", "") + "\n")
        self.logfile.write("set timeout 5\n")
        self.logfile.write("spawn dotnet " + self.neopath + " --rpc\n")
        self.waitnext()
        os.system("chmod 777 " + self.scriptpath)

    def readmsg(self):
        return self.readthread.lines()

    def clearmsg(self):
        self.readthread.clear()

    def begincmd(self, cmd):
        self.writeline("send_user \\nSTART_CLI_COMMAND-" + cmd + "-" + str(self.stepindex) + "\\n")

    def endcmd(self, cmd):
        self.writeline("send_user \\nFINISH_CLI_COMMAND-" + cmd + "-" + str(self.stepindex) + "\\n")
        self.stepindex += 1

    def writeline(self, str):
        self.logfile.write(str + "\n")

    def writesend(self, str):
        self.logfile.write("send \"" + str + "\\r\"" + "\n")
        pass

    def writeexcept(self, str):
        self.logfile.write("expect \"" + str + "\"" + "\n")
        pass

    def terminate(self):
        try:
            self.readthread.terminate = True
            os.system("kill -9 " + str(self.process_pid))
        except Exception as e:
            print(e)

    def waitnext(self, timeout=5, times=1):
        self.writeline("set timeout " + str(timeout))
        for index in range(times):
            self.writeexcept("*neo>")

    def waitgenblock(self):
        self.waitnext(timeout=5, times=4)

    def waitsync(self, timeoout=30):
        logger.print("send show state...")
        self.process.stdin.write("show state\n")
        self.process.stdin.flush()
        timeoutflag = 0
        while True:
            if timeoutflag > timeoout:
                self.process.stdin.write("\n")
                self.process.stdin.flush()
                return False
            time.sleep(1)
            timeoutflag += 1
            if self.readthread is not None or (self.readthread.isfinish() or self.readthread.isblock()):
                msg = self.readthread.lines()
                if msg is None:
                    logger.print("no msg readout...")
                    continue
                msglist = msg.split("\n")
                lastline = None
                if msglist is not None:
                    for msgline in msglist:
                        reresult = re.match(r'block: (\d+)/(\d+)/(\d+)  connected: (\d+)  unconnected: (\d+)', msgline)
                        if reresult is not None:
                            lastline = msgline
                    
                if lastline is None:
                    logger.print("no msg lastline readout...")
                    continue
                else:
                    logger.print("wait sync: " + lastline)

                reresult = re.match(r'block: (\d+)/(\d+)/(\d+)  connected: (\d+)  unconnected: (\d+)', lastline)
                group = None
                if reresult is None:
                    continue
                else:
                    logger.print("valid state infomation...")
                    group = reresult.group()

                if group is not None:
                    block1 = int(re.match(r'block: (\d+)/(\d+)/(\d+)  connected: (\d+)  unconnected: (\d+)', lastline).group(1))
                    block2 = int(re.match(r'block: (\d+)/(\d+)/(\d+)  connected: (\d+)  unconnected: (\d+)', lastline).group(2))
                    block3 = int(re.match(r'block: (\d+)/(\d+)/(\d+)  connected: (\d+)  unconnected: (\d+)', lastline).group(3))
                    connected = int(re.match(r'block: (\d+)/(\d+)/(\d+)  connected: (\d+)  unconnected: (\d+)', lastline).group(4))
                    if block1 > 0 and block1 == block2 and block1 == block3 and connected > 0:
                        self.process.stdin.write("\n")
                        self.process.stdin.flush()
                        return True
    def showScript(self):
        if self.logfile is not None:
            logger.info("showScript: logfile is not None")
            return
        f = open("./" + self.scriptpath)
        script = f.read()
        f.close()
        logger.info("[showScript] script: {0}".format(script))
    def exec(self, exitatlast=True):
        if exitatlast:
            self.writeline("set timeout 5\n")
            self.waitnext()
            self.exit()
        else:
            self.writeline("interact")

        msg = ""
        self.logfile.close()
        self.logfile = None
        self.showScript()
        self.process = subprocess.Popen("./" + self.scriptpath, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.process_pid = self.process.pid
        print("PID:", self.process_pid)
        self.readthread = CLIReadThread(self.process, self.scriptname)
        self.readthread.start()
        while True:
            if exitatlast:
                if self.readthread.isfinish():
                    msg = self.readthread.lines()
                    break
                else:
                    time.sleep(0.5)
            else:
                if self.readthread.isfinish() or self.readthread.isblock():
                    msg = self.readthread.lines()
                    break
                else:
                    time.sleep(0.5)

        msgblocks = {}
        logger.info("[exec] lines: {0}".format(msg))
        lines = msg.split('\n')
        newblockindex = -1
        newblockname = ""
        for line in lines:
            if line.find("START_CLI_COMMAND") != -1:
                newblockindex = line.split('-')[2]
                newblockname = line.split('-')[1]
                continue
            elif line.find("FINISH_CLI_COMMAND") != -1:
                newblockindex = -1
            else:
                if newblockindex != -1:
                    if newblockname + "-" + newblockindex in msgblocks.keys():
                        msgblock = msgblocks[newblockname + "-" + newblockindex]
                        msgblock += line + "\n"
                        msgblocks[newblockname + "-" + newblockindex] = msgblock
                    else:
                        msgblocks[newblockname + "-" + newblockindex] = ""

        print(self.stepexceptfuncs)
        for key in self.stepexceptfuncs.keys():
            exceptfunc = self.stepexceptfuncs[key]
            if exceptfunc is None:
                pass
            else:
                exceptret = False
                if key in msgblocks.keys():
                    print("compare step result: ", key, "   ", type(msgblocks[key]))
                    print("exceptfunc", msgblocks)
                    exceptret = exceptfunc(msgblocks[key])
                    print("compare step result end")
                else:
                    exceptret = exceptfunc("")
                if not exceptret:
                    return (False, key, msg)

        return (True, "", msg)

    def version(self, exceptfunc=None):
        self.writesend("version")
        self.stepexceptfuncs["[version]-" + str(self.stepindex)] = exceptfunc
        self.stepindex += 1

    # help  帮助菜单
    def help(self, exceptfunc=None):
        self.writesend("help")
        self.stepexceptfuncs["[help]-" + str(self.stepindex)] = exceptfunc
        self.stepindex += 1

    # clear 清除屏幕
    def clear(self):
        self.writesend("clear")

    # exit  退出程序
    def exit(self):
        self.writesend("exit")

    # create wallet <path>  创建钱包文件
    def create_wallet(self, filepath=None, password=None, password2=None, clearfirst=True, exceptfunc=None):
        name = "create_wallet"
        if filepath is not None:
            if clearfirst and os.path.exists(filepath):
                os.system("rm " + filepath)

        self.begincmd(name)
        if filepath is not None:
            self.writesend("create wallet " + filepath)
        else:
            self.writesend("create wallet")
        # input password
        self.writeexcept("*password:")
        if password is not None:
            self.writesend(password)
        else:
            self.writesend("")
        # confirm password
        self.writeexcept("*password:")
        if password2 is not None:
            self.writesend(password2)
        else:
            self.writesend("")
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # open wallet <path>    打开钱包文件
    def open_wallet(self, filepath=None, password=None, exceptfunc=None):
        name = "open_wallet"
        self.begincmd(name)
        if filepath is not None:
            self.writesend("open wallet " + filepath)
        else:
            self.writesend("open wallet")
        # input password
        self.writeexcept("*password:")
        if password is not None:
            self.writesend(password)
        else:
            self.writesend("")
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # upgrade wallet <path> 升级旧版钱包文件
    def upgrade_wallet(self, filepath=None, password=None, exceptfunc=None):
        name = "upgrade_wallet"
        self.begincmd(name)
        if filepath is not None:
            self.writesend("upgrade wallet " + filepath)
        else:
            self.writesend("upgrade wallet")
        self.writeexcept("*password:")
        if password is not None:
            self.writesend(password)
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

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
        name = "rebuild_index"
        self.begincmd(name)
        self.writesend("rebuild index")
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # list address  列出钱包中的所有账户  需要打开钱包
    def list_address(self, exceptfunc=None):
        name = "list_address"
        self.begincmd(name)
        self.writesend("list address")
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # list asset    列出钱包中的所有资产  需要打开钱包
    def list_asset(self, exceptfunc=None):
        name = "list_asset"
        self.begincmd(name)
        self.writesend("list asset")
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # list key  列出钱包中的所有公钥  需要打开钱包
    def list_key(self, exceptfunc=None):
        name = "list_key"
        self.begincmd(name)
        self.writesend("list key")
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

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
        name = "show_utxo"
        self.begincmd(name)
        if id_alias is None:
            self.writesend("show utxo")
        else:
            self.writesend("show utxo " + id_alias)
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # show gas  列出钱包中的所有可提取及不可提取的 GAS   需要打开钱包
    # examples:
    # unavailable: 133.024
    # available: 10.123
    def show_gas(self, exceptfunc=None):
        name = "show_gas"
        self.begincmd(name)
        self.writesend("show gas")
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # claim gas 提取钱包中的所有可提取的 GAS    需要打开钱包
    def claim_gas(self, exceptfunc=None):
        name = "claim_gas"
        self.begincmd(name)
        self.writesend("claim gas")
        # register except function
        self.waitnext()
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # create address [n=1]  创建地址 / 批量创建地址   需要打开钱包
    def create_address(self, n=None, exceptfunc=None, timeout=30):
        name = "create_address"
        self.begincmd(name)
        if n is None:
            self.writesend("create address")
        else:
            self.writesend("create address " + str(n))
        self.waitnext(timeout=timeout)
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # import key <wif|path> 导入私钥 / 批量导入私钥   需要打开钱包
    # examples:
    # import key L4zRFphDJpLzXZzYrYKvUoz1LkhZprS5pTYywFqTJT2EcmWPPpPH
    # import key key.txt
    def import_key(self, wif_path=None, exceptfunc=None, timeout=30):
        name = "import_key"
        self.begincmd(name)
        if wif_path is not None:
            self.writesend("import key " + str(wif_path))
        else:
            self.writesend("import key")
        # register except function
        self.waitnext(timeout=timeout)
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # export key [address] [path]   导出私钥    需要打开钱包
    # examples:
    # export key
    # export key AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b
    # export key key.txt
    # export key AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b key.txt
    def export_key(self, password=None, address=None, path=None, exceptfunc=None):
        name = "export_key"
        self.begincmd(name)
        addressstr = ""
        pathstr = ""
        if address is not None:
            addressstr = address
        if path is not None:
            pathstr = path
        self.writesend("export key " + str(addressstr) + " " + str(pathstr))
        self.writeexcept("*password:")
        if password is not None:
            self.writesend(password)
        else:
            self.writesend("")
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # send <id|alias> <address> <value>|all [fee=0] 向指定地址转账 参数分别为：资产 ID，对方地址，转账金额，手续费   需要打开钱包
    # examples:
    # 1. send c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b 100
    # 2. send neo AeSHyuirtXbfZbFik6SiBW2BEj7GK3N62b 100
    def send(self, password=None, id_alias=None, address=None, value=None, fee=0, exceptfunc=None):
        name = "send"
        self.begincmd(name)
        params = []
        if id_alias is not None:
            params.append(str(id_alias))
        if address is not None:
            params.append(str(address))
        if value is not None:
            params.append(str(value))
        if fee is not None:
            params.append(str(fee))

        self.writesend("send " + " ".join(params))
        self.writeexcept("*password:")
        if password is not None:
            self.writesend(password)
        else:
            self.writesend("")
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # import multisigaddress m pubkeys...   创建多方签名合约    需要打开钱包
    # examples:
    # import multisigaddress 1 037ebe29fff57d8c177870e9d9eecb046b27fc290ccbac88a0e3da8bac5daa630d 03b34a4be80db4a38f62bb41d63f9b1cb664e5e0416c1ac39db605a8e30ef270cc
    def import_multisigaddress(self, m=None, pubkeys=None, exceptfunc=None):
        name = "import_multisigaddress"
        self.begincmd(name)
        params = []
        if m is not None:
            params.append(str(m))
        if pubkeys is not None:
            params.append(" ".join(pubkeys))

        self.writesend("import multisigaddress " + " ".join(params))
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # sign <jsonObjectToSign>   签名 参数为：记录交易内容的 json 字符串 需要打开钱包
    def sign(self, jsonobj=None, exceptfunc=None):
        name = "sign"
        self.begincmd(name)
        if jsonobj is not None:
            self.writesend("sign " + jsonobj.replace("\"", "\\\"").replace(" ", "").replace("[", "\[").replace("}", "\}"))
        else:
            self.writesend("sign")

        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # relay <jsonObjectToSign>  广播 参数为：记录交易内容的 json 字符串 需要打开钱包
    def relay(self, jsonobj=None, exceptfunc=None):
        name = "relay"
        self.begincmd(name)
        if jsonobj is not None:
            self.writesend("relay " + jsonobj.replace("\"", "\\\"").replace(" ", "").replace("[", "\[").replace("}", "\}"))
        else:
            self.writesend("relay")
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # show state    显示当前区块链同步状态
    def show_state(self, times=1, exceptfunc=None):
        name = "show_state"
        self.begincmd(name)
        self.writesend("show state")
        for index in range(times):
            self.writeexcept("block:*")
        self.writesend("\n")
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # show node 显示当前已连接的节点地址和端口
    def show_node(self, exceptfunc=None):
        name = "show_node"
        self.begincmd(name)
        self.writesend("show node")
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # show pool 显示内存池中的交易（这些交易处于零确认的状态）
    def show_pool(self, exceptfunc=None):
        name = "show_pool"
        self.begincmd(name)
        self.writesend("show pool")
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # export blocks [path=chain.acc]    导出全部区块数据，导出的结果可以用作离线同步
    def export_all_blocks(self, path=None, exceptfunc=None, timeout=30):
        name = "export_all_blocks"
        self.begincmd(name)
        if path is None:
            self.writesend("export blocks")
        else:
            self.writesend("export blocks " + path)
        self.waitnext(timeout=timeout)
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # export blocks <start> [count] 从指定区块高度导出指定数量的区块数据，导出的结果可以用作离线同步
    def export_blocks(self, start=None, count=None, exceptfunc=None, timeout=30):
        name = "export_blocks"
        self.begincmd(name)
        params = []
        if start is not None:
            params.append(str(start))
        if count is not None:
            params.append(str(count))
        self.writesend("export blocks " + " ".join(params))
        self.waitnext(timeout=timeout)
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # start consensus   启动共识
    def start_consensus(self, exceptfunc=None):
        name = "start_consensus"
        self.begincmd(name)
        self.writesend("start consensus")
        self.waitnext()
        # register except function
        self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
        self.endcmd(name)

    # install plugin   安装插件
    def install_plugin(self, plugin=None, exceptfunc=None):
        name = "install_plugin"
        if plugin is not None:
            self.begincmd(name)
            self.writesend("install " + plugin)
            self.waitnext()
            # register except function
            self.stepexceptfuncs[name + "-" + str(self.stepindex)] = exceptfunc
            self.endcmd(name)