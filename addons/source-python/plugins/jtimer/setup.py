"""Setup script for installing jtimer requirements."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
import sys
import platform
from pip._internal import main as pipmain

if __name__ == "__main__":
    # make sure we're running same python version as SP
    assert sys.version_info.major == 3
    assert platform.architecture()[0] == "32bit"

    with open("requirements.txt") as requirements:
        pipmain(
            [
                "install",
                "-t",
                "../../packages/site-packages/",
                *requirements.readlines(),
            ]
        )
