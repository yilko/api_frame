from typing import Any, Dict

from api_def.base_api import BaseApi
from common.wrapper import singleton

'''
接口层
1、定义接口url和请求方式
2、从service层接收请求参数，拼接url和method发送请求
3、获取到响应返回给service层
'''


# 避免服务层多次实例化FrontApiDef类(对于xdist多进程无用)
# @singleton
class FrontApiDef(BaseApi):

    def login(self, modify_params: Dict[str, Any]):
        return self.send(self.address_request(modify_params));

    def object_list(self, modify_params: Dict[str, Any]):
        return self.send(self.address_request(modify_params));

    def person_root(self, modify_params: Dict[str, Any]):
        return self.send(self.address_request(modify_params));

    def view_attribute(self, modify_params: Dict[str, Any]):
        return self.send(self.address_request(modify_params));

# if __name__ == '__main__':
#     params = {"json": {"account": "abc@abc.com", "password": "abc"}};
#     print(FrontApiDef().login(params));
