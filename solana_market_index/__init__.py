import os
from pathlib import Path

def get_package_dir() -> os.PathLike:
    return Path(__file__).resolve().parent
