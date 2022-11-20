import inspect
import time
from typing import Dict, Any, NoReturn

import allure

from api_def.front_api_def import FrontApiDef
from common.helper import open_file, get_token
from log.config_log import config_log
from service.service_util import relevant_params_replace, validate, extract, case_replace

'''
服务层基类
1、通过服务层方法反射获取api层接口
2、非login接口给relevant_params字典添加token
3、处理用例模板(如果有)
4、处理发起请求前的参数变量替换
5、接口发起请求
6、断言接口内容
7、提取关联参数
'''
log = config_log();


class BaseService:

    def __init__(self):
        self.api = FrontApiDef();
        # 该实例下所有的关联参数都保存到这里(因为子类CompositeApi为单例，所以所有用例共用该字典)
        self.relevant_params = {};

    # 单接口的服务层步骤
    # 反例在获取文件内容时已添加case_num和case_name，并且参数化时除了获取反例内容，正例也加了进去
    def service_steps(self, api_params: Dict[str, Any]) -> NoReturn:
        # 截取SingleApi方法中的_service前面名字，截取出来的名字与api层方法一致
        api_func_name = inspect.stack()[1].function[:-8];
        func = getattr(self.api, api_func_name);
        # 非login接口需要等待login接口写入token后再获取参数列表
        token_dict = get_token(api_func_name);
        if token_dict:
            self.relevant_params.update(token_dict);
        # 有use_template字段需要进行模板用例替换
        if "use_template" in api_params:
            api_params = case_replace(api_params);
        # 进行用例中关联参数的变量替换
        testcase = relevant_params_replace(api_params, self.relevant_params);
        case_num, case_name = testcase['case_num'], testcase['case_name'];
        case_desc, req_params = testcase['desc'], testcase['requests'];
        # 多场景下，case_desc会一直被覆盖，直到覆盖到最后一个desc内容
        allure.dynamic.title(case_desc);
        # 多场景下每个接口的名字就是一个前置的步骤
        with allure.step(case_name):
            log.debug(f"service二次处理请求参数为===={req_params}");
            # 2、发起请求
            resp = func(req_params);
            log.debug(f"接口返回内容为===={resp}")
            allure.dynamic.description(f"测试用例内容为===={testcase}\n\n接口返回内容为===={resp}");
            # 3、返回实际值与用例期望值进行断言
            validate(testcase, resp);
            # 4、提取并保存关联参数
            self.relevant_params.update(extract(testcase, resp));
            log.info(f"-----用例编号：{case_num}-----用例名：{case_name}-----用例描述：{case_desc}-----执行完毕！-----");
