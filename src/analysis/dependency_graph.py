import ast
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Optional
import logging

try:
    from schemas.extraction_config import DependencyMetrics
except ImportError:
    # Fallback if run as script without package context
    sys.path.append(str(Path(__file__).parents[2]))
    from schemas.extraction_config import DependencyMetrics

try:
    from .logger import get_logger, setup_logging
except ImportError:
    from logger import get_logger, setup_logging

# Configure logging using shared setup if running as main, else get module logger
if __name__ == "__main__":
    logger = setup_logging(__name__)
else:
    logger = get_logger(__name__)

class DependencyGraphBuilder:
    """
    Phase 1: Static Analysis Layer
    
    Builds a directed graph of internal module dependencies to calculate 
    architectural centrality.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        # Graph: Key = File Path, Value = Set of imported File Paths
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        # Reverse Graph: Key = File Path, Value = Set of files that import Key
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        # External imports (e.g., 'numpy', 'fastapi')
        self.external_imports: Set[str] = set()
        # Track which files we have successfully analyzed
        self.analyzed_files: Set[str] = set()
        # Store pre-calculated metrics
        self.file_metrics: Dict[str, DependencyMetrics] = {}
        # Track entry points
        self.entry_points: Set[str] = set()

    def build(self) -> Dict[str, Dict]:
        """
        Orchestrates the graph generation process.
        """
        logger.info(f"Starting dependency analysis for: {self.repo_path}")
        
        python_files = list(self.repo_path.rglob("*.py"))
        filtered_files = [f for f in python_files if not self._should_ignore(f)]
        
        logger.info(f"Found {len(filtered_files)} Python files to analyze.")

        for file_path in filtered_files:
            self._analyze_file(file_path)

        self._calculate_metrics()
        logger.info("Dependency graph build complete.")
        return self.get_metrics()

    def _should_ignore(self, file_path: Path) -> bool:
        """
        Basic exclusion logic (pre-cursor to .llmignore integration).
        Skips tests, virtual environments, and hidden directories.
        """
        parts = file_path.parts
        ignore_terms = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', 'tests', 'docs'}
        
        # Check if any part of the path is in the ignore list
        if any(part in ignore_terms for part in parts):
            return True
        
        # Skip test files specifically
        if file_path.name.startswith('test_') or file_path.name.endswith('_test.py'):
            return True
            
        return False

    def _analyze_file(self, file_path: Path):
        """
        Parses a single Python file to extract import statements and detect entry points.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            tree = ast.parse(content)
            self.analyzed_files.add(str(file_path))
            
            # Check for Entry Point (if __name__ == "__main__":)
            if self._is_entry_point(tree):
                try:
                    rel_path = str(file_path.relative_to(self.repo_path))
                    self.entry_points.add(rel_path)
                except ValueError:
                    pass # Should not happen if file is in repo

            # Extract Imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._resolve_import(alias.name, file_path)
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module if node.module else ""
                    level = node.level

                    for alias in node.names:
                        if level > 0:
                            # Relative import
                            target_name = f"{module_name}.{alias.name}" if module_name else alias.name
                            self._resolve_relative_import(target_name, level, file_path)
                        else:
                            # Absolute import
                            # Try full module path (e.g., core.config)
                            full_name = f"{module_name}.{alias.name}"
                            if not self._resolve_import(full_name, file_path):
                                # Fallback: maybe alias is just a member of module
                                self._resolve_import(module_name, file_path)
                            
        except SyntaxError:
            logger.warning(f"Syntax error parsing {file_path}, skipping.")
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {str(e)}")

    def _is_entry_point(self, tree: ast.AST) -> bool:
        """
        Scans the AST for 'if __name__ == "__main__":' block.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check if it is a comparison
                if isinstance(node.test, ast.Compare):
                    # Check left side (should be __name__)
                    left = node.test.left
                    if isinstance(left, ast.Name) and left.id == "__name__":
                        # Check comparators (should be "__main__")
                        if len(node.test.comparators) > 0:
                            comp = node.test.comparators[0]
                            if isinstance(comp, ast.Constant) and comp.value == "__main__":
                                return True
        return False

    def _resolve_import(self, module_name: str, source_file: Path) -> bool:
        """
        Determines if an import is Internal (part of the repo) or External (pip lib).
        Maps module names (src.core.utils) to file paths (src/core/utils.py).
        Returns True if it was resolved to an internal file.
        """
        # Convert dot notation to path
        potential_path = module_name.replace(".", os.sep)
        
        # 1. Check if it refers to a file directly (module.py)
        candidate_1 = self.repo_path / f"{potential_path}.py"
        # 2. Check if it refers to a package (__init__.py)
        candidate_2 = self.repo_path / potential_path / "__init__.py"
        
        target = None
        if candidate_1.exists():
            target = candidate_1
        elif candidate_2.exists():
            target = candidate_2
            
        if target:
            # It is an INTERNAL dependency
            self._add_edge(source_file, target)
            return True
        else:
            # It is an EXTERNAL dependency (e.g., 'os', 'pandas')
            root_pkg = module_name.split(".")[0]
            self.external_imports.add(root_pkg)
            return False

    def _resolve_relative_import(self, module_name: str, level: int, source_file: Path):
        """
        Resolves relative imports (e.g., 'from ..utils import helper').
        """
        # Start from the source file's directory
        current_dir = source_file.parent
        
        # Move up 'level' directories
        # level 1 = same dir, level 2 = parent, etc.
        for _ in range(level - 1):
            current_dir = current_dir.parent
            
        # Construct the target path
        if module_name:
            target_path = current_dir / f"{module_name.replace('.', os.sep)}.py"
            target_pkg = current_dir / module_name.replace('.', os.sep) / "__init__.py"
        else:
            # Case: from . import X (module_name is None)
            # This usually imports from __init__.py of current dir
            target_path = current_dir / "__init__.py"
            target_pkg = None

        if target_path and target_path.exists():
            self._add_edge(source_file, target_path)
        elif target_pkg and target_pkg.exists():
            self._add_edge(source_file, target_pkg)

    def _add_edge(self, source: Path, target: Path):
        """
        Records a dependency: Source depends on Target.
        """
        # Normalize to relative paths for cleaner graph keys
        try:
            src_rel = str(source.relative_to(self.repo_path))
            tgt_rel = str(target.relative_to(self.repo_path))
            
            if src_rel == tgt_rel:
                return # Ignore self-imports

            self.graph[src_rel].add(tgt_rel)
            self.reverse_graph[tgt_rel].add(src_rel)
        except ValueError:
            pass # Paths outside repo scope

    def _calculate_metrics(self):
        """
        Derived metric calculation after graph is built.
        Stores the result in self.file_metrics.
        """
        all_files = self.analyzed_files | set(self.reverse_graph.keys())
        
        # Normalize paths in analyzed_files to relative for consistency
        rel_files = set()
        for f in all_files:
            try:
                rel = str(Path(f).relative_to(self.repo_path))
            except ValueError: 
                rel = f # Already relative
            rel_files.add(rel)

        for file_path in rel_files:
            in_degree = len(self.reverse_graph.get(file_path, []))
            out_degree = len(self.graph.get(file_path, []))
            centrality = in_degree - out_degree
            
            is_entry = file_path in self.entry_points

            self.file_metrics[file_path] = DependencyMetrics(
                in_degree=in_degree,
                out_degree=out_degree,
                centrality_score=float(centrality),
                dependencies=list(self.graph.get(file_path, [])),
                is_entry_point=is_entry
            )

    def get_metrics(self) -> Dict[str, Dict]:
        """
        Returns the final metrics dictionary for Phase 3 (Routing).
        """
        if not self.file_metrics and self.analyzed_files:
            self._calculate_metrics()
            
        return {
            k: v.model_dump() for k, v in self.file_metrics.items()
        }

if __name__ == "__main__":
    # CLI Test Usage
    if len(sys.argv) < 2:
        print("Usage: python dependency_graph.py <path_to_repo>")
        sys.exit(1)
        
    builder = DependencyGraphBuilder(sys.argv[1])
    stats = builder.build()
    
    print(f"\n--- Analysis Complete for {sys.argv[1]} ---")
    
    # Sort by Centrality (Highest first) to show Core Modules
    sorted_files = sorted(stats.items(), key=lambda x: x[1]['centrality_score'], reverse=True)
    
    print("\n🏆 Top 5 Core Modules (Highest Centrality):")
    for f, m in sorted_files[:5]:
        print(f"  [{m['centrality_score']}] {f} (Imported by {m['in_degree']} files)")
