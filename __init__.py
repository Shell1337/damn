__author__ = "github.com/imvast"
__title__ = "VeilCord"
__version__ = "0.0.7.4"

from .__main__ import *
from .__solver__ import *

from os import system
from sys import executable
from terminut import printf as print
from requests import get

try:
    CURRENT_VERSION = (
        get("https://pypi.org/pypi/veilcord/json").json().get("info").get("version")
    )
except:
    CURRENT_VERSION = __version__

if __version__ < CURRENT_VERSION:
    print(
        '[VeilCord] Version Out-of-Date. Please upgrade by using: "python.exe -m pip install -U veilcord"',
        mainCol="\x1B[31m",
        showTimestamp=False,
    )
    system(f"{executable} -m pip install -U veilcord  -q")
