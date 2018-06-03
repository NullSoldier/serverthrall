import sys

is_python_version_correct = (
    sys.version_info.major == 3 and
    sys.version_info.minor == 6)

if not is_python_version_correct:
    print('Must run with Python v3.6')
    sys.exit(1)

from serverthrall import run_server_thrall # noqa
import os # noqa

VERSION = '2.1.6'
run_server_thrall(VERSION)
