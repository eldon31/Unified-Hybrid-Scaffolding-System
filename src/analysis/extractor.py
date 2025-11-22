import ast
import logging
from pathlib import Path
from typing import Optional
import sys

try:
    from .logger import get_logger, setup_logging
except ImportError:
    # Fallback
    sys.path.append(str(Path(__file__).parents[2]))
    from analysis.logger import get_logger, setup_logging

# Configure logging using shared setup if running as main, else get module logger
if __name__ == "__main__":
    logger = setup_logging(__name__)
else:
    logger = get_logger(__name__)

class ContentExtractor:
    """
    Phase 4: Intelligent Extraction Layer
    
    Executes the extraction strategy determined by the Routing Engine.
    Surgically modifies source code to fit within context windows.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def extract(self, file_path: str, strategy: str) -> str:
        """
        Main entry point for file extraction.
        """
        full_path = self.repo_path / file_path
        
        if not full_path.exists():
            logger.error(f"File not found: {full_path}")
            return f"[Error: File {file_path} not found]"

        try:
            # 1. FULL Strategy: Return raw content
            if strategy == "FULL":
                return self._read_file(full_path)
            
            # 2. SIGNATURE Strategy: Parse and strip bodies
            elif strategy == "SIGNATURE":
                return self._extract_signature(full_path)
            
            # 3. MINIMAL Strategy: Docstrings only
            elif strategy == "MINIMAL":
                return self._extract_minimal(full_path)
            
            # 4. SKIP Strategy
            elif strategy == "SKIP":
                return ""
            
            else:
                logger.warning(f"Unknown strategy '{strategy}' for {file_path}, defaulting to MINIMAL")
                return self._extract_minimal(full_path)

        except Exception as e:
            logger.error(f"Failed to extract {file_path}: {e}")
            return f"[Error extracting {file_path}: {e}]"

    def _read_file(self, path: Path) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _extract_signature(self, path: Path) -> str:
        """
        Parses Python code and removes function/class bodies, keeping docstrings.
        """
        source_code = self._read_file(path)
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return source_code # Fallback if syntax is invalid

        transformed_lines = []
        lines = source_code.splitlines()
        
        class SignatureVisitor(ast.NodeVisitor):
            def __init__(self):
                self.keep_lines = set()
            
            def visit_Module(self, node):
                # Keep module docstrings
                if ast.get_docstring(node):
                    self.keep_lines.add(node.body[0].lineno)
                    # End line approximation (not perfect in stdlib ast)
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.keep_lines.add(node.lineno)
                # Keep decorators
                for dec in node.decorator_list:
                    self.keep_lines.add(dec.lineno)
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                self.keep_lines.add(node.lineno)
                # Keep decorators
                for dec in node.decorator_list:
                    self.keep_lines.add(dec.lineno)
                # Keep docstrings
                if ast.get_docstring(node):
                    # This is heuristic; precise docstring extraction requires more complex logic
                    pass 
                
                # We don't visit children logic blocks
        
        # Note: A robust AST-to-Source regenerator is complex. 
        # For this simplified engine, we will use a structural reconstruction approach 
        # or fall back to a specialized AST unparser if available (Python 3.9+).
        
        # Alternative: Use ast.unparse() (Python 3.9+) after modifying the tree
        
        for node in ast.walk(tree):
            # Replace function bodies with '...'
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if ast.get_docstring(node):
                    doc_node = node.body[0]
                    node.body = [doc_node, ast.Expr(value=ast.Constant(value=...))]
                else:
                    node.body = [ast.Expr(value=ast.Constant(value=...))]
            
            # Remove assignments inside classes if they are not type hints? 
            # For now, keep class bodies to show attributes, but strip methods as above.

        return ast.unparse(tree)

    def _extract_minimal(self, path: Path) -> str:
        """
        Returns module, class, and function docstrings.
        Removes all implementation details but keeps the structure.
        """
        source_code = self._read_file(path)
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return "# Parsing failed."

        # We want to keep:
        # 1. Module docstring
        # 2. Class definitions + docstrings
        # 3. Function definitions + docstrings
        # Everything else becomes ... or is removed.

        for node in ast.walk(tree):
            # Remove imports (optional, but keeps it minimal)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                continue # We can't easily remove from walk, so we modify the tree directly below

            # Handle Functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc_node = None
                if ast.get_docstring(node):
                    doc_node = node.body[0]

                # Replace body with docstring (if exists) or nothing
                if doc_node:
                     node.body = [doc_node]
                else:
                     # If no docstring, we might remove the function entirely in a true minimal view,
                     # but to show API surface, we keep it with pass
                     node.body = [ast.Pass()]

            # Handle Classes - we want to keep the class structure but filter its body
            # The walk will visit methods inside the class, so they get handled by the function logic above.
            # But we need to remove assignments/other statements in the class body.
            if isinstance(node, ast.ClassDef):
                new_body = []
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        new_body.append(child)
                    elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                        # Keep class docstring
                        new_body.append(child)
                    # We drop attributes (Assign, AnnAssign) in Minimal mode

                if not new_body:
                    new_body = [ast.Pass()]

                node.body = new_body

        # Remove top-level imports and code that isn't def/class
        # We do this by creating a new module body
        new_module_body = []

        # 1. Check for Module Docstring (usually the first expression)
        if ast.get_docstring(tree):
             # The first node is the docstring expression
             new_module_body.append(tree.body[0])

        # 2. Keep Classes and Functions
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                new_module_body.append(node)

        tree.body = new_module_body

        return ast.unparse(tree)