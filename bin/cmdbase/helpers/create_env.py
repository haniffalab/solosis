import os
from pathlib import Path

def create_env():
    CWD = os.getcwd() # Current Working dir
    GLOBAL_DIR=os.environ['GLOBAL_DIR']
    Path(".pap/lsf/").mkdir(parents=True, exist_ok=True)
    Path(".pap/scripts/").mkdir(parents=True, exist_ok=True)
    Path(GLOBAL_DIR+"/lsf/").mkdir(parents=True, exist_ok=True)
    Path(GLOBAL_DIR+"/scripts/").mkdir(parents=True, exist_ok=True)
    return CWD


