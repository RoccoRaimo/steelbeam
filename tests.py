import os, pathlib
import pytest

os.chdir( pathlib.Path.cwd() / 'Tests' )

pytest.main()