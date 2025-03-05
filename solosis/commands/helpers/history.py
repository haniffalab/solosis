import functools
import os
from datetime import datetime

import pandas as pd


def history(func):
    """
    A decorator for creating history each time the command is successfully invoked
    """
    CWD = os.getcwd()  # Current Working dir
    USER = os.environ["USER"]
    LOCAL_HIST = os.environ["LOCAL_HIST"]
    GLOBAL_HIST = os.environ["GLOBAL_HIST"]
    VERSION = os.environ["VERSION"]
    RUN_TOKEN = os.environ["RUN_TOKEN"]

    @functools.wraps(
        func
    )  # Ensures the original function name is registered by click instead of registering wrapper
    def wrapper(*args, **kwargs):
        # print(f"Invocation token: {RUN_TOKEN}")
        # print("----------------------------")
        result = func(*args, **kwargs)

        # history items
        func_name = func.__name__
        invoke_time = datetime.now().strftime("%d/%m/%y, %H:%M:%S")
        x = " ,".join([str(k) + ":" + str(v) for k, v in kwargs.items()])
        h = pd.DataFrame(
            {
                "func_name": func_name,
                "time": invoke_time,
                "username": USER,
                "version": VERSION,
                "cwd": CWD,
                "args": x,
            },
            index=[RUN_TOKEN],
        )
        h.to_csv(LOCAL_HIST, mode="a", header=not os.path.exists(LOCAL_HIST))
        h.to_csv(GLOBAL_HIST, mode="a", header=not os.path.exists(GLOBAL_HIST))
        return result

    return wrapper
