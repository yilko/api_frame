import os
from enum import Enum

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)));

'''枚举文件路径'''


class PathEnum(Enum):
    ENV_PATH = project_path + r"\config\env.yml";
    INTERFACE_PATH = project_path + r"\config\interface.yml";
    TOKEN_PATH = project_path + r"\config\login_params.yml";
    DATA_SUCCESS_DIR_PATH = project_path + r"\data\success_case";
    DATA_FAIL_DIR_PATH = project_path + r"\data\fail_case";
    DATA_TEMPLATE_DIR_PATH = project_path + r"\data_template";

# if __name__ == '__main__':
#     print(PathEnum.ENV_PATH.value)
