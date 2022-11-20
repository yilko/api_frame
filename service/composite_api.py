from typing import Dict, Any, NoReturn, List

from service.single_api import SingleApi;

'''
复合场景服务层：
1、按照用例顺序接收对应用例参数
2、调用对应单接口层方法组合成场景
3、供用例层调用
'''


class CompositeApi(SingleApi):

    def test_entire_doc_composite(self, many_params: List[Dict[str, Any]]) -> NoReturn:
        self.object_list_service(many_params[0]);
        self.person_root_service(many_params[1]);
