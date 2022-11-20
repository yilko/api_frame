from typing import Dict, Any

import allure
import pytest

from common.helper import open_parametrize_file
from log.config_log import config_log
from service.composite_api import CompositeApi

'''
一个py文件代表某个模块的所有用例
一个方法代表一条测试用例，每条测试用例可单独运行，不依赖其他用例(能进行多进程的基础)
'''

'''
用例统一只有三步
1、实例化服务层接口
2、获取用例
3、执行用例(场景层+单接口层)
'''

log = config_log();


@allure.feature("文档模块")
class TestModule:

    @allure.story("测试个人文档")
    @pytest.mark.parametrize("testcases", open_parametrize_file("f002_person_list.yml"))
    def test_person_list(self, testcases: Dict[str, Any]):
        run = CompositeApi();
        run.object_list_service(testcases);

    @allure.story("测试文档属性")
    def test_entire_doc(self, get_testcase: Dict[str, Any]):
        run = CompositeApi();
        testcase2, testcase3 = get_testcase["s002_person_list.yml"], get_testcase["s003_person_root.yml"];
        testcase4 = get_testcase["s004_view_attribute.yml"];
        run.test_entire_doc_composite([testcase2, testcase3]);
        run.view_attribute_service(testcase4);
