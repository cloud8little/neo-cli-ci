import json
import time

import utils.connect
from utils.config import Config
from utils.common import Common
from utils.logger import LoggerInstance as logger
from utils.error import RuntimeError
import numpy as np
np.set_printoptions(suppress=True)


class TaskRunner:
    # 执行单个webapi
    # task: 需要执行的task
    # judge: 是否需要结果判断
    # process_log： 是否需要记录运行log
    # 返回值: (result: True or False, response: 网络请求)
    @staticmethod
    def run_single_task(task, judge=True, process_log=False):
        connecttype = task.type()
        name = task.name()
        start_time = time.time()

        if process_log:
            logger.print("[-------------------------------]")
            logger.print("[ CONNECT  ] " + str(connecttype) + "." + str(name))

        cfg_content = task.data()
        cfg_request = cfg_content["REQUEST"]
        cfg_response = cfg_content["RESPONSE"]
        if process_log:
            logger.print("[ REQUEST  ]" + json.dumps(cfg_content, indent=4, sort_keys=True).replace("\"num#!#start-", "").replace("-num#!#end\"", ""))

        # (result, response) = self.multithread_run(logger, cfg_request, cfg_response)
        node_index = task.node_index()
        node_ip = None
        if node_index is None:
            node_index = 0

        if connecttype.lower() == "rpc":
            node_ip = Config.NODES[int(node_index)]["ip"] + ":" + str(Config.NODES[int(node_index)]["rpcport"])
        if connecttype.lower() == "st":
            node_ip = Config.NODES[int(node_index)]["ip"] + ":" + str(Config.NODES[int(node_index)]["stport"])
        if process_log:
            logger.print("run on service(" + str(node_index) + "):  " + node_ip)

        response = utils.connect.con(connecttype, node_ip, cfg_request)
        if process_log:
            logger.print("[ RESPONSE ]" + json.dumps(response, indent=4))

        end_time = time.time()
        time_consumed = (end_time - start_time) * 1000

        result = True
        if judge:
            result = Common.cmp(cfg_response, response)
            if process_log:
                if result:
                    logger.print("[ OK       ] " + connecttype + "." + name + " (%d ms)" % (time_consumed))
                else:
                    logger.print("[ Failed   ] " + connecttype + "." + name + " (%d ms)" % (time_consumed))
                logger.print("[-------------------------------]")
                logger.print("")

        return (result, response)

    # 运行两个task
    # 假设 task1生成reponse1， task2得到reponse2， compare_src_key为 key1|key2, compare_dist_key为 key3|key4
    # 最终会比较reponse1["key1"]["key2"]和reponse2["key3"]["key4"]
    # result: 比较结果 True or False
    @staticmethod
    def run_pair_task(task1, task2, compare_src_key=None, compare_dist_key=None):
        result = True

        (result1, response1) = TaskRunner.run_single_task(task1)
        if not result1:
            return result1

        (result2, response2) = TaskRunner.run_single_task(task2)
        if not result2:
            return result2

        compare_src_data = response1
        if compare_src_key:
            compare_src_keys = compare_src_key.split('/')
            for key in compare_src_keys:
                if compare_src_data:
                    compare_src_data = compare_src_data[key]
                else:
                    break

            # split dist key
            compare_dist_data = response2
            if compare_dist_key:
                compare_dist_keys = compare_dist_key.split('/')
                for key in compare_dist_keys:
                    if compare_dist_data:
                        compare_dist_data = compare_dist_data[key]
                    else:
                        break
            result = Common.cmp(compare_src_data, compare_dist_data)
        else:
            result = True

        return result
