import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests"