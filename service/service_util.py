import ast
import inspect
import json
import os
import re
from string import Template
from typing import NoReturn, Dict, Any, Union

import chevron
import pytest
from jsonpath import jsonpath

from common.helper import open_file
from common.path_enum import PathEnum
from log.config_log import config_log

'''
服务层工具类
1、提供模板替换方法
2、提供断言
3、提供提取关联参数
'''
log = config_log();

''' 存在bug，如果保存的是布尔类型，数字类型，字典类型等，模板替换后获取的值都是str类型，用于下个接口传入时可能会出问题'''


# 处理用例请求前的变量替换${xxx}
def relevant_params_replace(testcase: Dict[str, Any], var_value: Dict[str, Any]) -> Dict[str, Any]:
    # ensure_ascii设置为false防止中文变为乱码
    # 只有$xxx和${}格式才会替换，如果是$.开头不会替换
    str_content = Template(json.dumps(testcase, ensure_ascii=False)).safe_substitute(var_value);
    log.debug(f"变量替换后当前接口参数为===={str_content}");
    return json.loads(str_content);


# 用例使用模板创建，返回替换变量后的模板用例
def case_replace(api_params: Dict[str, Any]) -> Dict[str, Any]:
    template_name = api_params["use_template"];
    template_path = str(PathEnum.DATA_TEMPLATE_DIR_PATH.value) + os.path.sep + template_name;
    log.debug(f"模板路径===={template_path}");
    case_str = chevron.render(open_file(template_path, "str"), api_params);
    testcase = ast.literal_eval(case_str);
    log.debug(f"引用模板后的用例内容为===={testcase}");
    return testcase;


# 解析validate和extract字段中含有jsonpath的表达式
def __parse_jsonpath(testcase_part: Dict[str, Any], resp: Dict[str, Any]) -> Dict[str, Any]:
    call_func_name = inspect.stack()[1].function;
    str_content = json.dumps(testcase_part, ensure_ascii=False)
    expr_ls = re.findall("\$\.[a-zA-z0-9.]+", str_content);
    log.debug(f"{call_func_name}字段jsonpath表达式有===={expr_ls}");
    for expr in expr_ls:
        value_ls = jsonpath(resp, expr);
        if isinstance(value_ls, list):
            # jsonpath解析出来返回一个列表，取第一个,并转为str类型
            value = str(value_ls[0]);
            # 一般只替换一个值，如果不写1会把全部内容都替换，会出问题
            str_content = str_content.replace(expr, value, 1);
        # 如果表达式没有匹配到会返回false
        elif isinstance(value_ls, bool):
            log.info(f"没有找到当前表达式对应的值===={expr}");
    log.debug(f"{call_func_name}字段替换后的内容为===={str_content}");
    return json.loads(str_content);


# 断言失败(仅限validate方法调用)
def __assert_fail(error_msg: str, resp: Union[Dict[str, Any], str]) -> NoReturn:
    log.error(error_msg);
    log.error(f"接口返回内容为===={resp}");
    pytest.fail(error_msg, pytrace=False);


# 用例断言，其中一个断言失败整个用例都失败，用例失败不会中断程序运行，只会标记该用例失败
def validate(testcase: Dict[str, Any], resp: Dict[str, Any]) -> NoReturn:
    if isinstance(resp, str):
        __assert_fail("接口返回不为json格式，请检查响应内容", resp);
        return None;
    validate_dict = testcase["validate"];
    validate_ls = __parse_jsonpath(validate_dict, resp);
    # [["2", "equals", 2], ["云宏信息科技股份有限公司", "contains", "云宏"], ["0", "len_equals", 0]];
    for validate in validate_ls:
        compare_char = validate[1];
        if "equals" == compare_char:
            actual_val, expect_val = str(validate[0]), str(validate[2]);
            if actual_val != expect_val:
                __assert_fail(f"实际值{actual_val}和期望值{expect_val}不相等，断言失败，用例不通过", resp);
                break;
            else:
                log.info(f"实际值{actual_val}和期望值{expect_val}相等，断言成功");
        elif "contains" == compare_char:
            actual_val, expect_val = str(validate[0]), str(validate[2]);
            if expect_val not in actual_val:
                __assert_fail(f"实际值{actual_val}和期望值{expect_val}没有包含关系，断言失败，用例不通过", resp);
                break;
            else:
                log.info(f"实际值{actual_val}和期望值{expect_val}有包含关系，断言成功");
        # 下面长度相关的比较，仅限于列表元组字典的长度，字符串长度比较会报错
        elif "len_equals" == compare_char:
            actual_val, expect_val = str(len(eval(validate[0]))), str(validate[2]);
            if actual_val != expect_val:
                __assert_fail(f"实际值{actual_val}和期望值{expect_val}长度不相等，断言失败，用例不通过", resp);
                break;
            else:
                log.info(f"实际值{actual_val}和期望值{expect_val}长度相等，断言成功");
        elif "len_greater_than" == compare_char:
            actual_val, expect_val = str(len(eval(validate[0]))), str(validate[2]);
            if actual_val <= expect_val:
                __assert_fail(f"实际值{actual_val}长度没有大于和期望值{expect_val}，断言失败，用例不通过", resp);
                break;
            else:
                log.info(f"实际值{actual_val}长度大于和期望值{expect_val}，断言成功");
        elif "len_less_than" == compare_char:
            actual_val, expect_val = str(len(eval(validate[0]))), str(validate[2]);
            if actual_val >= expect_val:
                __assert_fail(f"实际值{actual_val}长度没有小于期望值{expect_val}，断言失败，用例不通过", resp);
                break;
            else:
                log.info(f"实际值{actual_val}长度小于期望值{expect_val}，断言成功");
    else:
        log.info("该接口所有断言字段通过");


# 提取关联参数，组合成字典返回
def extract(testcase: Dict[str, Any], resp: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(resp, str):
        log.error("接口返回不为json格式，请检查响应内容");
        return {};
    # 可能存在不需要提取参数的情况，使用get会返回None
    extract_dict = testcase.get("extract");
    if extract_dict is not None:
        extract_ls = __parse_jsonpath(extract_dict, resp);
        extract_val = {k: v for d in extract_ls for k, v in d.items()};
        log.info(f"提取参数为===={extract_val}");
        return extract_val;
    else:
        log.info(f"当前接口不需要提取参数");
        return {};

# if __name__ == '__main__':
#     with open("../data/s001_login.yml", "r", encoding="utf-8") as f:
#         content = yaml.safe_load(f);
#     testcase = template_replace(content, {"account": "123@qq.com", "password": "123"});
#     resp = {'status': 200, 'msg': '', 'data': {'isReturn': '0', 'isInitialPassword': False, 'company': {'id': 'c89e95cdb488475285e26b51382f886b', 'uniqueId': 'VJALwzBI', 'logoId': 'b819e3e8696d4491a973d2ab8e0e49e6.null', 'productName': None, 'welcomeInfo': None, 'title': None, 'productImage': None, 'productIcon': None, 'ownerId': 'a364599944e74f2b9e2ccb9e07af8a89', 'name': '云宏信息科技股份有限公司', 'status': 4, 'isFree': 1, 'comboId': 'a55d4310-7dae-11e7-e074-f6d800f97fce', 'comboName': None, 'serviceEndTime': 4810982399000, 'innerNumber': 5000, 'usedInnerNumber': None, 'outNumber': 1, 'usedOutNumber': None, 'size': 8637237968896, 'availableSize': 0, 'fileVersionNumber': 1000, 'createTime': 1534903659000, 'updateTime': 1668267542000, 'ownerName': 'log', 'contantSize': 0, 'permissions': [], 'config': None, 'innerLisence': None, 'applicationId': '409f524102184bb0b594e65cea91c1b4', 'contactName': '创新产品部', 'contactEmail': 'cxcpb@winhong.com', 'contactPhone': '0', 'licenseInfo': None, 'publicKey': None, 'sn': '997d-9cd1-1794-f11a', 'publicKeyName': '公钥_0001 (1).pem', 'publicKeyVersion': '0001', 'activateStatus': 1, 'publicKeyDownloadUrl': 'https://license.zkuyun.com:9090/download_key.php', 'licDownloadUrl': 'https://license.zkuyun.com:9090', 'hotline': '400-6300-003', 'customServiceQQ': None, 'customServiceMail': None, 'edition': 'privateNetdisk', 'switchStatus': 0, 'saasHistoryVer': 0, 'waterMarkContent': None, 'waterMarkStatus': 0, 'softVersion': '1', 'nodeNumber': '2', 'oaFlag': None, 'lisence': None}, 'isPasswordExpired': False, 'applicationId': '409f524102184bb0b594e65cea91c1b4', 'keyList': [], 'userId': '4e237b9e0fc042669ada70df21b51d3b', 'token': 'NGUyMzdiOWUwZmMwNDI2NjlhZGE3MGRmMjFiNTFkM2ItcHl0aG9uLXJlcXVlc3RzLzIuMjguMS0xNjY4MjcwMjYyMTk2LWQ2MjI2NTUyNmFiNjRjODViODcyMTQwNGZjODM3OWE5'}, 'errCode': None, 'previewModel': None, 'previewForm': None, 'vedeoForm': None, 'vedeoType': None, 'waterMark': None, 'fileName': None, 'objectId': None, 'version': None, 'success': True}
#     extract(testcase, resp);
#     validate(testcase, resp);
#
#     log.info(resp)
