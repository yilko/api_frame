from common.helper import open_file
from common.path_enum import PathEnum
from log.config_log import config_log

'''获取当前运行环境及拼接域名'''

log = config_log();


# 读取env.yml文件并返回拼接好的域名
def read_env() -> str:
    content: dict = open_file(str(PathEnum.ENV_PATH.value));
    try:
        env_key = content["choose_env"];
        env_content = content[env_key];
        host = f"{env_content['protocol']}://{env_content['domain_name']}:{env_content['port']}";
        log.debug(f"拼接后的域名为==={host}");
        return host;
    except KeyError as e:
        raise Exception(f"choose_env的value与各个环境的key没有匹配上===={e}");

# if __name__ == '__main__':
#     read_env();
