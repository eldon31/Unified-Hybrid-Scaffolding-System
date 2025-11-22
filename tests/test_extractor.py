import pytest
from pathlib import Path
from src.analysis.extractor import ContentExtractor

@pytest.fixture
def mock_file(tmp_path):
    """Creates a temporary Python file for testing."""
    f = tmp_path / "example.py"
    f.write_text("""\"\"\"
Module Docstring
\"\"\"
import os

class MyClass:
    \"\"\"Class Docstring\"\"\"
    x = 10

    def my_method(self):
        \"\"\"Method Docstring\"\"\"
        print("Hello")

def my_func():
    \"\"\"Func Docstring\"\"\"
    return True

def undocumented():
    pass
""")
    return f

def test_extract_full(mock_file):
    extractor = ContentExtractor(str(mock_file.parent))
    content = extractor.extract("example.py", "FULL")

    assert "import os" in content
    assert "print(\"Hello\")" in content
    assert "class MyClass:" in content

def test_extract_minimal(mock_file):
    extractor = ContentExtractor(str(mock_file.parent))
    content = extractor.extract("example.py", "MINIMAL")

    # Should keep docstrings
    assert "Module Docstring" in content
    assert "Class Docstring" in content
    assert "Method Docstring" in content
    assert "Func Docstring" in content

    # Should keep structure
    assert "class MyClass" in content
    assert "def my_method" in content

    # Should remove implementation
    assert "print" not in content
    assert "x = 10" not in content
    assert "import os" not in content

def test_extract_skip(mock_file):
    extractor = ContentExtractor(str(mock_file.parent))
    content = extractor.extract("example.py", "SKIP")
    assert content == ""

def test_file_not_found(tmp_path):
    extractor = ContentExtractor(str(tmp_path))
    content = extractor.extract("ghost.py", "FULL")
    assert "[Error: File ghost.py not found]" in content
