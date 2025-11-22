import ast
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"level": "%(levelname)s", "module": "extractor", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

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
        Returns only the module-level docstring.
        """
        source_code = self._read_file(path)
        try:
            tree = ast.parse(source_code)
            docstring = ast.get_docstring(tree)
            if docstring:
                return f'"""\n{docstring}\n"""'
            return "# No documentation available."
        except SyntaxError:
            return "# Parsing failed."