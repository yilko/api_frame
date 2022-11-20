# -*- coding: utf-8 -*-
# Author: Yilko Lin
# Date:2022/11/20 1:55
# File: test_login.PY
from typing import Dict, Any

import allure
import pytest

from common.helper import open_parametrize_file
from log.config_log import config_log
from service.composite_api import CompositeApi

log = config_log();


@allure.feature("登录模块")
class TestLogin:

    @allure.story("测试登录")
    @pytest.mark.run(order=0)
    @pytest.mark.parametrize("testcases", open_parametrize_file("f001_login.yml"))
    def test_logins(self, testcases: Dict[str, Any]):
        run = CompositeApi();
        run.login_service(testcases);
