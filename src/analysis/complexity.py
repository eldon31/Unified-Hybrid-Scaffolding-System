import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging
try:
    from schemas.extraction_config import ContextMetrics
except ImportError:
    # Fallback if run as script without package context
    sys.path.append(str(Path(__file__).parents[2]))
    from schemas.extraction_config import ContextMetrics

try:
    from .logger import get_logger, setup_logging
except ImportError:
    from logger import get_logger, setup_logging

# Configure logging using shared setup if running as main, else get module logger
if __name__ == "__main__":
    logger = setup_logging(__name__)
else:
    logger = get_logger(__name__)

class CodeComplexityAnalyzer:
    """
    Phase 2: Dynamic Analysis Layer
    
    Analyzes Python source code to measure 'Understanding Difficulty' and 'Context Richness'.
    Used to determine the Extraction Strategy (Signature vs Full vs Minimal).
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    def analyze_file(self, file_path: Path) -> Optional[ContextMetrics]:
        """
        Performs comprehensive AST analysis on a single file.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 1. Lines of Code (LOC) - excluding empty lines and comments
            loc = self._count_loc(content)
            
            # 2. API Counts (Functions & Classes)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            total_apis = len(functions) + len(classes)
            
            # 3. Cyclomatic Complexity (Branching logic)
            complexity = self._calculate_cyclomatic_complexity(tree)
            
            # 4. Documentation Coverage
            doc_coverage = self._calculate_doc_coverage(tree, total_apis)
            
            # 5. Context Richness Score (Heuristic)
            # A combination of API density and code size.
            # High score = dense, API-heavy file (likely needs SIGNATURE extraction)
            # Low score = simple script or utility
            context_richness = min(100.0, (total_apis * 5.0) + (loc / 50.0))

            return ContextMetrics(
                loc=loc,
                api_count=total_apis,
                cyclomatic_complexity=complexity,
                documentation_coverage=doc_coverage,
                context_richness_score=round(context_richness, 2)
            )

        except SyntaxError:
            logger.warning(f"Syntax error parsing {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
            return None

    def _count_loc(self, content: str) -> int:
        """
        Counts non-empty, non-comment lines.
        """
        lines = content.splitlines()
        valid_lines = [
            line for line in lines 
            if line.strip() and not line.strip().startswith('#')
        ]
        return len(valid_lines)

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """
        Calculates McCabe's Cyclomatic Complexity.
        Base complexity is 1. Adds 1 for every control flow statement.
        """
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # Boolean operators (and, or) add decision points
                complexity += len(node.values) - 1
        return complexity

    def _calculate_doc_coverage(self, tree: ast.AST, total_apis: int) -> float:
        """
        Calculates percentage of functions/classes that have docstrings.
        """
        if total_apis == 0:
            return 100.0 # No APIs to document implies full coverage trivially

        documented_apis = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if ast.get_docstring(node):
                    documented_apis += 1
        
        return round((documented_apis / total_apis) * 100, 2)

    def analyze_repo(self) -> Dict[str, dict]:
        """
        Runs analysis on the entire repository.
        """
        results = {}
        python_files = list(self.repo_path.rglob("*.py"))
        
        logger.info(f"Starting complexity analysis for {len(python_files)} files...")
        
        for file_path in python_files:
            # Simple ignore logic (can be expanded with .llmignore later)
            if any(p in file_path.parts for p in ['.venv', 'venv', '__pycache__', 'tests']):
                continue
                
            metrics = self.analyze_file(file_path)
            if metrics:
                # Map file_path to metrics object
                rel_path = str(file_path.relative_to(self.repo_path))
                results[rel_path] = metrics.model_dump()
                
        logger.info("Complexity analysis complete.")
        return results

if __name__ == "__main__":
    # CLI Test Usage
    if len(sys.argv) < 2:
        print("Usage: python complexity.py <path_to_repo>")
        sys.exit(1)
    
    analyzer = CodeComplexityAnalyzer(sys.argv[1])
    repo_metrics = analyzer.analyze_repo()
    
    print(f"\n--- Complexity Analysis for {sys.argv[1]} ---")
    
    # Sort by Context Richness (Highest First)
    sorted_files = sorted(repo_metrics.items(), key=lambda x: x[1]['context_richness_score'], reverse=True)
    
    print("\n🔥 Top 5 Most Complex/Rich Files:")
    for f_path, m in sorted_files[:5]:
        print(f"  {f_path}")
        print(f"    - Complexity (CC): {m['cyclomatic_complexity']}")
        print(f"    - APIs: {m['api_count']}")
        print(f"    - Richness Score: {m['context_richness_score']}")
        print(f"    - Doc Coverage: {m['documentation_coverage']}%")
        print("-" * 30)