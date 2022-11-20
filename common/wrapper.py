from functools import wraps


# 单例模式
def singleton(cls):
    __instance = {};

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in __instance:
            __instance[cls] = cls(*args, **kwargs);
        return __instance[cls];

    return wrapper
