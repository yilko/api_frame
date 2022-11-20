import json
import os
from typing import Dict, Any, NoReturn
from filelock import FileLock
import pytest
from _pytest.fixtures import FixtureRequest

from common.helper import open_file
from common.path_enum import PathEnum
from log.config_log import config_log
from service.composite_api import CompositeApi

log = config_log();

'''或者可以考虑把文件内容的case_name作为key，这样用例层获取用例时一眼就了解用例内容，目前做法是yml名字作为key'''


# 获取data下所有用例，并且拼接成{"s001_login.yml":"001yml内容","002_xx.yml":""002yml内容"}
# @pytest.fixture(scope="session")
def get_testcase() -> Dict[str, Any]:
    all_testcases: Dict[str, dict] = {};
    testcase_path = str(PathEnum.DATA_SUCCESS_DIR_PATH.value);
    log.debug(f"yml用例有===={os.listdir(testcase_path)}");
    for testcase in os.listdir(testcase_path):
        path = testcase_path + os.path.sep + testcase;
        all_testcases[testcase] = open_file(path);
    else:
        log.info(f"所有的testcases为===={all_testcases}");
        return all_testcases;


# 添加文件锁，使xdist多进程运行时只会运行一次(该地方参考xdist官方文档)
@pytest.fixture(scope="session", name="get_testcase")
def get_case(tmp_path_factory, worker_id):
    # 单线程运行
    if worker_id == "master":
        return get_testcase();
    root_tmp_dir = tmp_path_factory.getbasetemp().parent;
    fn = root_tmp_dir / "data.json";
    # 多线程运行
    with FileLock(str(fn) + ".lock"):
        # 已经执行过fixture
        if fn.is_file():
            data = json.loads(fn.read_text());
        # 第一次执行fixture
        else:
            data = get_testcase();
            fn.write_text(json.dumps(data))
    return data;

# if __name__ == '__main__':
#     save_login_params()
