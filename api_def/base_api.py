import inspect

import requests
from json import JSONDecodeError
from typing import Dict, Any, Union

from common.helper import open_file
from common.path_enum import PathEnum
from config.config_env import read_env
from log.config_log import config_log;

'''
接口层基类
1、负责获取域名和接口信息
2、负责拼接参数和发送请求
'''

log = config_log();


class BaseApi:

    def __init__(self):
        self.host: str = read_env();
        # 获取interface.yml所有的接口
        self.interfaces: Dict[str, list] = open_file(str(PathEnum.INTERFACE_PATH.value));

    # 封装request请求，param_dict包含所有请求内容
    # 最好判定是json格式还是html格式
    @staticmethod
    def send(param_dict: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        resp = requests.request(**param_dict);
        try:
            resp_json = resp.json();
            log.debug(f'返回json格式===={resp.headers["Content-Type"]}');
            return resp_json;
        except JSONDecodeError:
            log.debug(f'不为json格式，返回html格式===={resp.headers["Content-Type"]}');
            return resp.text;

    # 处理请求，传进来的参数、url，请求方式，整合成字典并返回
    # 只负责把params加入url和method字段，其他字段的处理不在该方法上
    def address_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # 获取到对应接口名字
        interface_key = inspect.stack()[1].function;
        log.debug(f"发起请求的接口名字为===={interface_key}");
        interface_val_ls = self.interfaces[interface_key];
        params["url"] = self.host + interface_val_ls[0];
        params["method"] = interface_val_ls[1];
        log.info(f"拼接url和method的请求参数为===={params}");
        return params;
