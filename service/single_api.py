from typing import NoReturn, Dict, Any

import allure
import yaml

from common.helper import write_token
from service.base_service import BaseService

'''
单接口服务层
1、接收用例层的参数，调用对应接口名字
'''


class SingleApi(BaseService):

    def login_service(self, testcase_params: Dict[str, Any]) -> NoReturn:
        self.service_steps(testcase_params);
        write_token(testcase_params, self.relevant_params);

    def object_list_service(self, testcase_params: Dict[str, Any]) -> NoReturn:
        self.service_steps(testcase_params);

    def person_root_service(self, testcase_params: Dict[str, Any]) -> NoReturn:
        self.service_steps(testcase_params);

    def view_attribute_service(self, testcase_params: Dict[str, Any]) -> NoReturn:
        self.service_steps(testcase_params);

# if __name__ == '__main__':
# login_params = {"json": {"account": "${account}", "password": "abc"}};
# SingleApi.login_service(login_params)

# func_name = inspect.stack()[0].function[:-8]
# print("object_list_service"[:-8])
