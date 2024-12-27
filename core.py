""" This is the entry point used for pyinstaller to know how to execute the main module """

import sys
from core_automation.core import core_module


if __name__ == "__main__":
    core_module(sys.argv[1:])
