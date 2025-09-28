# app/config/cache_config.py
from typing import Callable, Any

from fastapi_cache import FastAPICache
from app.config.logging_config import logger

def key_builder(func: Callable, namespace: str = "", *args: Any, **kwargs: Any) -> str:
    """
    ключ для кэша:
    - игнорирует 'self' (первый позиционный аргумент)
    - игнорирует request, response и другие служебные объекты
    - формирует ключ на основе оставшихся простых аргументов
    """

    func_args = kwargs.get("args", ())

    # Пропускаем self (первый элемент)
    real_args = func_args[1:] if len(func_args) > 0 else ()

    simple_kwargs = {k: v for k, v in kwargs.get("kwargs", {}).items()
                     if k not in ("request", "response")}

    key_parts = [namespace]
    key_parts.extend(map(str, real_args))
    for k, v in sorted(simple_kwargs.items()):
        key_parts.append(f"{k}={v}")

    return ":".join(key_parts)