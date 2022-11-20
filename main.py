# -*- coding: utf-8 -*-

import os
import pytest
import requests

from common.helper import clear_token

'''
优化点：
1、(已解决)多进程下频繁登录一个账号导致403(原因是同个账号获取token间隔太短，导致上一次获取token无效)
2、除了反例支持参数化，正例有时候也需要参数化，需要支持
3、反例参数化是会带上正例yml的内容，如果没有正例的话，参数化会报错
4、参数替换默认都是字符串类型，如果提取参数是布尔，数字，字典等类型，发起请求会出问题
5、(已去掉)多进程下单例模式会无作用，考虑去掉
6、除了支持http协议，考虑再支持dubbo等协议
7、断言的规则还可以再完善(增加断言)
8、文件上传用例可能要定制化
9、反例中没用模板的情况没验证
'''

if __name__ == '__main__':
    pytest.main();
    clear_token();
    os.system("allure generate ./report/xml -o ./report/html --clean");
    os.system(f"allure open {os.path.dirname(__file__)}/report/html");