# Repository Scaffold: app


## File: src/analysis/batch_runner.py
**Strategy:** FULL | **Reason:** Small Utility (Low Cost)
```python
import sys
import logging
from pathlib import Path
from time import perf_counter

# Import the single-repo orchestrator
try:
    from .orchestrator import ScaffoldOrchestrator
except ImportError:
    from orchestrator import ScaffoldOrchestrator

try:
    from .logger import get_logger, setup_logging
except ImportError:
    from logger import get_logger, setup_logging

# Configure logging using shared setup if running as main, else get module logger
if __name__ == "__main__":
    logger = setup_logging(__name__)
else:
    logger = get_logger(__name__)

class BatchRunner:
    """
    Phase 6: Multi-Repository Orchestration

    Iterates through the workspace 'repos/' directory and triggers
    the ScaffoldOrchestrator for every subdirectory found.
    """

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()
        self.repos_dir = self.workspace_root / "repos"

    def run_all(self):
        """
        Scans for repositories and builds scaffolds for all of them.
        """
        if not self.repos_dir.exists():
            logger.error(f"Repositories directory not found: {self.repos_dir}")
            print(f"❌ Error: Could not find '{self.repos_dir}'. Please create it and git clone your projects there.")
            return

        # Find all subdirectories in repos/
        # We assume any folder here is a target repo
        targets = [
            d for d in self.repos_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]

        if not targets:
            logger.warning("No repositories found in repos/ directory.")
            return

        print(f"\n🌍 Starting Batch Scaffolding for {len(targets)} Repositories...")
        print("=" * 60)

        total_start = perf_counter()
        success_count = 0

        for repo_path in targets:
            print(f"\n👉 Processing: {repo_path.name}")
            try:
                start_time = perf_counter()

                # Initialize and run the Orchestrator for this specific repo
                orchestrator = ScaffoldOrchestrator(str(repo_path))
                orchestrator.run_pipeline()

                duration = perf_counter() - start_time
                logger.info(f"Completed {repo_path.name} in {duration:.2f}s")
                success_count += 1

            except Exception as e:
                logger.error(f"Failed to scaffold {repo_path.name}: {e}")
                print(f"❌ Failed: {e}")

        total_duration = perf_counter() - total_start

        print("\n" + "=" * 60)
        print(f"🏁 Batch Run Complete.")
        print(f"✅ Successful: {success_count}/{len(targets)}")
        print(f"⏱️  Total Time: {total_duration:.2f}s")
        print("=" * 60)

if __name__ == "__main__":
    # Default to current directory if root not specified
    root_path = sys.argv[1] if len(sys.argv) > 1 else "."

    runner = BatchRunner(root_path)
    runner.run_all()
```

## File: schemas/__init__.py
**Strategy:** FULL | **Reason:** Small Utility (Low Cost)
```python

```

## File: src/main.py
**Strategy:** FULL | **Reason:** Small Utility (Low Cost)
```python
import sys
import argparse
import logging
from pathlib import Path

# Add 'src' to path to ensure imports work regardless of where it's run from
sys.path.append(str(Path(__file__).parent))

# Import the engines we built in Steps 5, 6, and 7
from analysis.orchestrator import ScaffoldOrchestrator
from analysis.batch_runner import BatchRunner
from analysis.static_assets import StaticAssetGenerator
from analysis.logger import setup_logging

# Configure Logging
logger = setup_logging("CLI")

def run_single(target_path: str):
    """
    Runs the full pipeline on a single repository.
    1. Generates Static Assets (Context Pack)
    2. Runs Dynamic Analysis (Scaffold)
    """
    repo_path = Path(target_path).resolve()
    if not repo_path.exists():
        logger.error(f"Target path does not exist: {repo_path}")
        return

    print(f"\n🎯 Target: {repo_path.name}")

    # 1. Ensure Static Assets exist (.llmignore, CONTRIBUTING.md, etc.)
    print("   [1/2] Initializing Context Pack...")
    static_gen = StaticAssetGenerator(str(repo_path))
    static_gen.generate_all()

    # 2. Run the Analysis Engine
    print("   [2/2] Running Analysis Engine...")
    orchestrator = ScaffoldOrchestrator(str(repo_path))
    orchestrator.run_pipeline()

def run_batch(workspace_root: str):
    """
    Runs the pipeline on ALL repositories in the 'repos/' folder.
    """
    print(f"\n🌍 Mode: Batch Processing Workspace: {workspace_root}")

    # The BatchRunner handles the iteration
    runner = BatchRunner(workspace_root)
    runner.run_all()

def main():
    parser = argparse.ArgumentParser(
        description="Unified Hybrid Scaffolding CLI",
        usage="""
    python src/main.py single ./repos/my-app    # Scaffold one repo
    python src/main.py batch .                  # Scaffold all repos in workspace
    """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: single
    single_parser = subparsers.add_parser("single", help="Process a single repository")
    single_parser.add_argument("path", help="Path to the target repository")

    # Command: batch
    batch_parser = subparsers.add_parser("batch", help="Process all repositories in 'repos/' folder")
    batch_parser.add_argument("root", nargs="?", default=".", help="Workspace root directory")

    args = parser.parse_args()

    if args.command == "single":
        run_single(args.path)
    elif args.command == "batch":
        run_batch(args.root)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

## File: src/analysis/static_assets.py
**Strategy:** SIGNATURE | **Reason:** High Complexity/Richness (API Focus)
```python
import os
import sys
import logging
from pathlib import Path
try:
    from .logger import get_logger, setup_logging
except ImportError:
    from logger import get_logger, setup_logging
if __name__ == '__main__':
    logger = setup_logging(__name__)
else:
    logger = get_logger(__name__)

class StaticAssetGenerator:
    """
    Phase 7: Static Context Generation

    Ensures every repository has the required baseline 'Context Pack' files.
    If a file is missing, it generates it with standard defaults.
    """

    def __init__(self, repo_path: str):
        ...

    def generate_all(self):
        """
        Checks and generates all static assets.
        """
        ...

    def _ensure_dirs(self):
        ...

    def _create_file(self, rel_path: str, content: str):
        ...

    def _get_llmignore_content(self) -> str:
        ...

    def _get_llmstxt_content(self) -> str:
        ...

    def _get_repomix_content(self) -> str:
        ...

    def _get_contributing_content(self) -> str:
        ...

    def _get_metrics_content(self) -> str:
        ...

    def _get_adr_template_content(self) -> str:
        ...
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python static_assets.py <repo_path>')
        sys.exit(1)
    gen = StaticAssetGenerator(sys.argv[1])
    gen.generate_all()
    print(f'✅ Static assets generated for {sys.argv[1]}')
```

## File: src/analysis/extractor.py
**Strategy:** SIGNATURE | **Reason:** High Complexity/Richness (API Focus)
```python
import ast
import logging
from pathlib import Path
from typing import Optional
import sys
try:
    from .logger import get_logger, setup_logging
except ImportError:
    sys.path.append(str(Path(__file__).parents[2]))
    from analysis.logger import get_logger, setup_logging
if __name__ == '__main__':
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
        ...

    def extract(self, file_path: str, strategy: str) -> str:
        """
        Main entry point for file extraction.
        """
        ...

    def _read_file(self, path: Path) -> str:
        ...

    def _extract_signature(self, path: Path) -> str:
        """
        Parses Python code and removes function/class bodies, keeping docstrings.
        """
        ...

    def _extract_minimal(self, path: Path) -> str:
        """
        Returns module, class, and function docstrings.
        Removes all implementation details but keeps the structure.
        """
        ...
```

## File: src/analysis/dependency_graph.py
**Strategy:** SIGNATURE | **Reason:** High Complexity/Richness (API Focus)
```python
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
    sys.path.append(str(Path(__file__).parents[2]))
    from schemas.extraction_config import DependencyMetrics
try:
    from .logger import get_logger, setup_logging
except ImportError:
    from logger import get_logger, setup_logging
if __name__ == '__main__':
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
        ...

    def build(self) -> Dict[str, Dict]:
        """
        Orchestrates the graph generation process.
        """
        ...

    def _should_ignore(self, file_path: Path) -> bool:
        """
        Basic exclusion logic (pre-cursor to .llmignore integration).
        Skips tests, virtual environments, and hidden directories.
        """
        ...

    def _analyze_file(self, file_path: Path):
        """
        Parses a single Python file to extract import statements and detect entry points.
        """
        ...

    def _is_entry_point(self, tree: ast.AST) -> bool:
        """
        Scans the AST for 'if __name__ == "__main__":' block.
        """
        ...

    def _resolve_import(self, module_name: str, source_file: Path) -> bool:
        """
        Determines if an import is Internal (part of the repo) or External (pip lib).
        Maps module names (src.core.utils) to file paths (src/core/utils.py).
        Returns True if it was resolved to an internal file.
        """
        ...

    def _resolve_relative_import(self, module_name: str, level: int, source_file: Path):
        """
        Resolves relative imports (e.g., 'from ..utils import helper').
        """
        ...

    def _add_edge(self, source: Path, target: Path):
        """
        Records a dependency: Source depends on Target.
        """
        ...

    def _calculate_metrics(self):
        """
        Derived metric calculation after graph is built.
        Stores the result in self.file_metrics.
        """
        ...

    def get_metrics(self) -> Dict[str, Dict]:
        """
        Returns the final metrics dictionary for Phase 3 (Routing).
        """
        ...
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python dependency_graph.py <path_to_repo>')
        sys.exit(1)
    builder = DependencyGraphBuilder(sys.argv[1])
    stats = builder.build()
    print(f'\n--- Analysis Complete for {sys.argv[1]} ---')
    sorted_files = sorted(stats.items(), key=lambda x: x[1]['centrality_score'], reverse=True)
    print('\n🏆 Top 5 Core Modules (Highest Centrality):')
    for f, m in sorted_files[:5]:
        print(f"  [{m['centrality_score']}] {f} (Imported by {m['in_degree']} files)")
```

## File: src/analysis/complexity.py
**Strategy:** SIGNATURE | **Reason:** High Complexity/Richness (API Focus)
```python
import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging
try:
    from schemas.extraction_config import ContextMetrics
except ImportError:
    sys.path.append(str(Path(__file__).parents[2]))
    from schemas.extraction_config import ContextMetrics
try:
    from .logger import get_logger, setup_logging
except ImportError:
    from logger import get_logger, setup_logging
if __name__ == '__main__':
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
        ...

    def analyze_file(self, file_path: Path) -> Optional[ContextMetrics]:
        """
        Performs comprehensive AST analysis on a single file.
        """
        ...

    def _count_loc(self, content: str) -> int:
        """
        Counts non-empty, non-comment lines.
        """
        ...

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """
        Calculates McCabe's Cyclomatic Complexity.
        Base complexity is 1. Adds 1 for every control flow statement.
        """
        ...

    def _calculate_doc_coverage(self, tree: ast.AST, total_apis: int) -> float:
        """
        Calculates percentage of functions/classes that have docstrings.
        """
        ...

    def analyze_repo(self) -> Dict[str, dict]:
        """
        Runs analysis on the entire repository.
        """
        ...
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python complexity.py <path_to_repo>')
        sys.exit(1)
    analyzer = CodeComplexityAnalyzer(sys.argv[1])
    repo_metrics = analyzer.analyze_repo()
    print(f'\n--- Complexity Analysis for {sys.argv[1]} ---')
    sorted_files = sorted(repo_metrics.items(), key=lambda x: x[1]['context_richness_score'], reverse=True)
    print('\n🔥 Top 5 Most Complex/Rich Files:')
    for f_path, m in sorted_files[:5]:
        print(f'  {f_path}')
        print(f"    - Complexity (CC): {m['cyclomatic_complexity']}")
        print(f"    - APIs: {m['api_count']}")
        print(f"    - Richness Score: {m['context_richness_score']}")
        print(f"    - Doc Coverage: {m['documentation_coverage']}%")
        print('-' * 30)
```

## File: schemas/extraction_config.py
**Strategy:** MINIMAL | **Reason:** Default utility
```python
class ContextMetrics(BaseModel):
    """
    Dynamic Analysis Metrics (Phase 2) used to measure Context Richness and Understanding Difficulty [8, 10].
    """

class DependencyMetrics(BaseModel):
    """
    Static Analysis Metrics (Phase 1) used to measure architectural importance [8, 10].
    """

class FileExtractionPlan(BaseModel):
    """
    The output schema for the Adaptive Routing Engine (Phase 3), defining the final strategy per file [8, 9].
    """

class ScaffoldingOutput(BaseModel):
    """
    The final manifest for the entire repository analysis, used by the Token Budget Manager [11].
    """
```

## File: src/analysis/logger.py
**Strategy:** MINIMAL | **Reason:** Default utility
```python
class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings fitting the observability/metrics.md spec.
    Schema:
    {
      "level": "INFO | WARN | ERROR",
      "timestamp": "ISO-8601",
      "service": "scaffold-engine",
      "module": "dependency_graph",
      "trace_id": "<correlation_id>",
      "message": "Human readable event description",
      "context": { ... }
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        pass

def setup_logging(module_name: str='root', level: int=logging.INFO):
    """
    Sets up the root logger with JSON formatter.
    This should be called once at the entry point.
    """

def get_logger(module_name: str):
    """
    Returns a logger with the given name.
    """
```

## File: src/analysis/orchestrator.py
**Strategy:** MINIMAL | **Reason:** Default utility
```python
class ScaffoldOrchestrator:
    """
    Phase 5: Orchestration & Token Budgeting

    Runs the full pipeline and generates the final Context Pack.
    """

    def __init__(self, repo_path: str, token_limit: int=500000, model: str='gpt-4o'):
        pass

    def run_pipeline(self):
        pass

    def _extract_with_budget(self) -> str:
        """
        Extracts content, counting tokens. If limit reached, downgrades strategies.
        """

    def _generate_artifacts(self, scaffold_content: str, dep_metrics: dict, comp_metrics: dict):
        """
        Writes the physical .md files to disk.
        """

    def _generate_blueprint(self, output_dir: Path, dep_metrics: dict, comp_metrics: dict):
        """
        Generates the Domain Blueprint based on analysis data.
        """

    def _generate_architecture_doc(self, output_dir: Path, dep_metrics: dict):
        """
        Generates the Architecture Overview.
        """
```

## File: src/analysis/adaptive_routing.py
**Strategy:** MINIMAL | **Reason:** Default utility
```python
class AdaptiveRoutingEngine:
    """
    Phase 3: Adaptive Routing Layer

    Combines Static (Centrality) and Dynamic (Complexity) metrics to determine
    the optimal extraction strategy for each file to maximize token efficiency.
    """

    def __init__(self, dependency_metrics: Dict[str, dict], complexity_metrics: Dict[str, dict]):
        pass

    def route_all(self) -> List[FileExtractionPlan]:
        """
        Process all files and assign strategies.
        """

    def _decide_strategy(self, file_path: str) -> FileExtractionPlan:
        """
        The core logic matrix for a single file.
        """
```
