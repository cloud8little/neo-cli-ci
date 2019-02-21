# -*- coding:utf-8 -*-

import socket
import json
import setproctitle
import sys
import os
import getopt

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher
from config import Configure as config

sys.path.append('../src/api')
sys.path.append('../src')
from cli import CLIApi


cli = CLIApi()


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def eval_exceptfunc(funcstr):
    if funcstr is None:
        return None
    else:
        return eval(funcstr)


@dispatcher.add_method
def exec_cmd(**kwargs):
    return os.system(kwargs["cmd"])


@dispatcher.add_method
def cli_init(**kwargs):
    return cli.init(kwargs["scriptname"], kwargs["neopath"])


@dispatcher.add_method
def cli_readmsg(**kwargs):
    return cli.readmsg()


@dispatcher.add_method
def cli_clearmsg(**kwargs):
    return cli.clearmsg()


@dispatcher.add_method
def cli_terminate(**kwargs):
    return cli.terminate()


@dispatcher.add_method
def cli_exec(**kwargs):
    return cli.exec(kwargs["exitatlast"])


@dispatcher.add_method
def cli_version(**kwargs):
    return cli.version()


@dispatcher.add_method
def cli_help(**kwargs):
    return cli.help()


@dispatcher.add_method
def cli_clear(**kwargs):
    return cli.clear()


@dispatcher.add_method
def cli_exit(**kwargs):
    return cli.exit()


@dispatcher.add_method
def cli_create_wallet(**kwargs):
    return cli.create_wallet(kwargs["filepath"], kwargs["password"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_open_wallet(**kwargs):
    return cli.open_wallet(kwargs["filepath"], kwargs["password"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_upgrade_wallet(**kwargs):
    return cli.upgrade_wallet(kwargs["filepath"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_rebuild_index(**kwargs):
    return cli.rebuild_index(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_list_address(**kwargs):
    return cli.list_address(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_list_asset(**kwargs):
    return cli.list_asset(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_list_key(**kwargs):
    return cli.list_key(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_show_utxo(**kwargs):
    return cli.show_utxo(kwargs["id_alias"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_show_gas(**kwargs):
    return cli.show_gas(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_claim_gas(**kwargs):
    return cli.claim_gas(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_create_address(**kwargs):
    return cli.create_address(kwargs["n"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_import_key(**kwargs):
    return cli.create_address(kwargs["wif_path"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_export_key(**kwargs):
    return cli.create_address(kwargs["password"], kwargs["address"], kwargs["path"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_send(**kwargs):
    return cli.create_address(kwargs["password"], kwargs["id_alias"], kwargs["address"], kwargs["value"], kwargs["fee"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_import_multisigaddress(**kwargs):
    return cli.import_multisigaddress(kwargs["m"], kwargs["pubkeys"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_sign(**kwargs):
    return cli.sign(kwargs["jsonobj"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_relay(**kwargs):
    return cli.relay(kwargs["jsonobj"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_show_state(**kwargs):
    return cli.show_state(kwargs["times"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_show_node(**kwargs):
    return cli.show_node(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_show_pool(**kwargs):
    return cli.show_pool(eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_export_all_blocks(**kwargs):
    return cli.export_all_blocks(kwargs["path"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_export_blocks(**kwargs):
    return cli.export_all_blocks(kwargs["start"], kwargs["count"], eval_exceptfunc(kwargs["exceptfunc"]))


@dispatcher.add_method
def cli_start_consensus(**kwargs):
    return cli.start_consensus(eval_exceptfunc(kwargs["exceptfunc"]))

@dispatcher.add_method
def cli_install_plugin(**kwargs):
    return cli.install_plugin(kwargs["plugin"], eval_exceptfunc(kwargs["exceptfunc"]))

@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["exec_cmd"] = exec_cmd
    dispatcher["cli_init"] = cli_init
    dispatcher["cli_readmsg"] = cli_readmsg
    dispatcher["cli_clearmsg"] = cli_clearmsg
    dispatcher["cli_terminate"] = cli_terminate
    dispatcher["cli_exec"] = cli_exec
    dispatcher["cli_version"] = cli_version
    dispatcher["cli_help"] = cli_help
    dispatcher["cli_clear"] = cli_clear
    dispatcher["cli_exit"] = cli_exit
    dispatcher["cli_create_wallet"] = cli_create_wallet
    dispatcher["cli_open_wallet"] = cli_open_wallet
    dispatcher["cli_upgrade_wallet"] = cli_upgrade_wallet
    dispatcher["cli_rebuild_index"] = cli_rebuild_index
    dispatcher["cli_list_address"] = cli_list_address
    dispatcher["cli_list_asset"] = cli_list_asset
    dispatcher["cli_list_key"] = cli_list_key
    dispatcher["cli_show_utxo"] = cli_show_utxo
    dispatcher["cli_show_gas"] = cli_show_gas
    dispatcher["cli_claim_gas"] = cli_claim_gas
    dispatcher["cli_create_address"] = cli_create_address
    dispatcher["cli_import_key"] = cli_import_key
    dispatcher["cli_export_key"] = cli_export_key
    dispatcher["cli_send"] = cli_send
    dispatcher["cli_import_multisigaddress"] = cli_import_multisigaddress
    dispatcher["cli_sign"] = cli_sign
    dispatcher["cli_relay"] = cli_relay
    dispatcher["cli_show_state"] = cli_show_state
    dispatcher["cli_show_node"] = cli_show_node
    dispatcher["cli_show_pool"] = cli_show_pool
    dispatcher["cli_export_all_blocks"] = cli_export_all_blocks
    dispatcher["cli_export_blocks"] = cli_export_blocks
    dispatcher["cli_start_consensus"] = cli_start_consensus
    dispatcher["cli_install_plugin"] = cli_install_plugin

    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    responseobj = json.loads(response.json)
    if "error" not in responseobj:
        responseobj["error"] = 0
    else:
        if "message" in responseobj["error"]:
            responseobj["desc"] = responseobj["error"]["message"]
        if "code" in responseobj["error"]:
            responseobj["error"] = responseobj["error"]["code"]
    print(json.dumps(responseobj))
    return Response(json.dumps(responseobj), mimetype='application/json')


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "p:n:")
    name = "test_service"
    port = config.PORT
    for op, value in opts:
        if op == "-p":
            port = value
        elif op == "-n":
            name = value
    setproctitle.setproctitle(name)

    run_simple("0.0.0.0", int(port), application)
