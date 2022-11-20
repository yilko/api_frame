import os
import time
import yaml
from typing import Union, Dict, Any, TextIO, List
from common.path_enum import PathEnum
from log.config_log import config_log

'''公用方法'''
log = config_log();


# 打开文件
def open_file(path: str, style: str = "dict") -> Union[Dict[str, Any], str, TextIO]:
    with open(path, "r", encoding="utf-8") as f:
        if style == "dict":
            return yaml.safe_load(f);
        elif style == "str":
            return f.read();


'''正例和反例的yml文件都要有，如果只有正例或反例会报错，以后优化'''


# 接收反例名字，并且反例中增加case_name和case_num两个字段
# 反例和正例都获取内容，返回一个列表供用例层参数化parametrize调用
def open_parametrize_file(fail_case_name: str) -> List[Dict[str, Any]]:
    fail_case_path = str(PathEnum.DATA_FAIL_DIR_PATH.value) + os.path.sep + fail_case_name;
    fail_case = open_file(fail_case_path);
    fail_testcase_ls = fail_case["testcases"];
    for case in fail_testcase_ls:
        case["case_name"] = fail_case["case_name"];
        case["case_num"] = fail_case["case_num"];
    success_case_path = str(PathEnum.DATA_SUCCESS_DIR_PATH.value) + os.path.sep + "s" + fail_case_name[1:];
    # 正例放最前面
    fail_testcase_ls.insert(0, open_file(success_case_path))
    return fail_testcase_ls;


# 只有登录接口并且是s001_login.yml文件才会提取token写到文件中
def write_token(testcase_params: Dict[str, Any], token: Dict[str, str]):
    if testcase_params["case_num"] == "s001":
        # allow_unicode支持中文
        with open(str(PathEnum.TOKEN_PATH.value), "w") as f:
            yaml.dump(token, f, allow_unicode=True);


# 非login接口获取token
def get_token(func_name: str) -> Union[Dict[str, str], None]:
    if func_name != "login":
        params = open_file(str(PathEnum.TOKEN_PATH.value));
        while params is None:
            params = open_file(str(PathEnum.TOKEN_PATH.value));
            log.info("---------------正在等待登录的token----------------");
            time.sleep(0.5);
        return params;
    else:
        return None;


# 清空login_params.yml文件内容
# 文件不能删除只能清空,否则get_token打开文件会出现FileNotFound异常
def clear_token():
    with open(str(PathEnum.TOKEN_PATH.value), "w") as f:
        f.truncate();
    log.info("---------------正在清理login_params.yml文件数据----------------");

# if __name__ == '__main__':
#     print(open_parametrize_file("f001_login.yml"))
