import functools
import logging
from typing import Callable

def debug_decorator(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug(f"{func.__name__} が呼び出されました。引数: {args}, キーワード引数: {kwargs}")
        result = func(*args, **kwargs)
        logging.debug(f"{func.__name__} が終了しました。戻り値: {result}")
        return result
    return wrapper
