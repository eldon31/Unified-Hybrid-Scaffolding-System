import os
import pytest
from pathlib import Path
from src.analysis.dependency_graph import DependencyGraphBuilder

@pytest.fixture
def mock_repo(tmp_path):
    """Creates a temporary mock repository structure."""
    repo_dir = tmp_path / "mock_repo"
    repo_dir.mkdir()

    # structure:
    # mock_repo/
    #   main.py
    #   utils.py
    #   core/
    #     __init__.py
    #     config.py
    #     helper.py

    (repo_dir / "core").mkdir()

    # main.py imports utils and core.config
    (repo_dir / "main.py").write_text("""
import utils
from core import config

if __name__ == "__main__":
    print("Running")
""")

    # utils.py imports core (pkg)
    (repo_dir / "utils.py").write_text("""
import core
""")

    # core/__init__.py imports helper
    (repo_dir / "core" / "__init__.py").write_text("""
from . import helper
""")

    # core/config.py imports nothing
    (repo_dir / "core" / "config.py").write_text("""
TOKEN = "123"
""")

    # core/helper.py imports nothing
    (repo_dir / "core" / "helper.py").write_text("""
def help(): pass
""")

    return repo_dir

def test_simple_dependency_build(mock_repo):
    builder = DependencyGraphBuilder(str(mock_repo))
    metrics = builder.build()

    # Check main.py
    main = metrics.get("main.py")
    assert main is not None
    assert main["is_entry_point"] is True
    assert "utils.py" in main["dependencies"]
    assert "core/config.py" in main["dependencies"]

def test_package_import_resolution(mock_repo):
    builder = DependencyGraphBuilder(str(mock_repo))
    metrics = builder.build()

    # utils.py imports 'core', which maps to 'core/__init__.py'
    utils = metrics.get("utils.py")
    assert "core/__init__.py" in utils["dependencies"]

def test_relative_import_resolution(mock_repo):
    builder = DependencyGraphBuilder(str(mock_repo))
    metrics = builder.build()

    # core/__init__.py contains 'from . import helper'
    core_init = metrics.get("core/__init__.py")
    assert "core/helper.py" in core_init["dependencies"]

def test_centrality_calculation(mock_repo):
    builder = DependencyGraphBuilder(str(mock_repo))
    metrics = builder.build()

    # core/config.py is imported by main.py
    # It imports nothing -> Out=0, In=1 -> Centrality = 1
    config = metrics.get("core/config.py")
    assert config["centrality_score"] >= 1.0

def test_ignore_logic(mock_repo):
    # Add a test file
    (mock_repo / "test_main.py").write_text("import main")

    builder = DependencyGraphBuilder(str(mock_repo))
    metrics = builder.build()

    assert "test_main.py" not in metrics
