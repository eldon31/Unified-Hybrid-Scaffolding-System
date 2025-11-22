import logging
import sys
from pathlib import Path
from typing import Dict, List, Literal

try:
    from schemas.extraction_config import FileExtractionPlan, DependencyMetrics, ContextMetrics
except ImportError:
    # Fallback if run as script without package context
    sys.path.append(str(Path(__file__).parents[2]))
    from schemas.extraction_config import FileExtractionPlan, DependencyMetrics, ContextMetrics

try:
    from .logger import get_logger, setup_logging
except ImportError:
    from logger import get_logger, setup_logging

# Configure logging using shared setup if running as main, else get module logger
if __name__ == "__main__":
    logger = setup_logging(__name__)
else:
    logger = get_logger(__name__)

# Define Extraction Strategies
StrategyType = Literal["FULL", "SIGNATURE", "MINIMAL", "SKIP"]

class AdaptiveRoutingEngine:
    """
    Phase 3: Adaptive Routing Layer
    
    Combines Static (Centrality) and Dynamic (Complexity) metrics to determine
    the optimal extraction strategy for each file to maximize token efficiency.
    """
    
    def __init__(self, dependency_metrics: Dict[str, dict], complexity_metrics: Dict[str, dict]):
        self.dependency_metrics = dependency_metrics
        self.complexity_metrics = complexity_metrics
        
        # Thresholds (can be tuned via config later)
        self.HIGH_CENTRALITY_THRESHOLD = 5.0  # Core infrastructure
        self.HIGH_COMPLEXITY_THRESHOLD = 20   # Hard to understand logic
        self.RICHNESS_THRESHOLD = 50.0        # API dense

    def route_all(self) -> List[FileExtractionPlan]:
        """
        Process all files and assign strategies.
        """
        decisions = []
        # Get all unique files from both analysis sets
        all_files = set(self.dependency_metrics.keys()) | set(self.complexity_metrics.keys())
        
        logger.info(f"Routing extraction strategies for {len(all_files)} files...")
        
        for file_path in all_files:
            decision = self._decide_strategy(file_path)
            decisions.append(decision)
            
        # Sort by priority: FULL > SIGNATURE > MINIMAL
        # Within strategy, sort by Centrality (Importance)
        decisions.sort(key=lambda x: (
            0 if x.extraction_strategy == "FULL" else 1 if x.extraction_strategy == "SIGNATURE" else 2,
            -x.dependencies.centrality_score
        ))
        
        logger.info("Routing complete.")
        return decisions

    def _decide_strategy(self, file_path: str) -> FileExtractionPlan:
        """
        The core logic matrix for a single file.
        """
        # 1. Get Metrics (default to 0 if missing)
        dep = self.dependency_metrics.get(file_path, {})
        comp = self.complexity_metrics.get(file_path, {})
        
        # Safe access via dict keys, matching the keys produced by model_dump()
        centrality = dep.get('centrality_score', 0)
        in_degree = dep.get('in_degree', 0)
        complexity = comp.get('cyclomatic_complexity', 0)
        richness = comp.get('context_richness_score', 0)
        doc_coverage = comp.get('documentation_coverage', 0)

        # 2. Apply Decision Logic
        strategy: StrategyType = "MINIMAL"
        reason = "Default utility"

        # Rule 1: Core Infrastructure -> FULL
        # High Centrality means many files depend on this. We need full context.
        if centrality >= self.HIGH_CENTRALITY_THRESHOLD or in_degree >= 5:
            if complexity < self.HIGH_COMPLEXITY_THRESHOLD:
                strategy = "FULL"
                reason = "Core Infrastructure (High Centrality)"
            else:
                # It's core but VERY complex. Full extraction might waste tokens.
                # If it's well documented, use Signatures.
                if doc_coverage > 50.0:
                    strategy = "SIGNATURE"
                    reason = "Core but Complex (High CC + Good Docs)"
                else:
                    strategy = "FULL"
                    reason = "Core & Complex (Needs Implementation for Context)"

        # Rule 2: Complex Logic -> SIGNATURE
        # Not central, but hard to understand. LLM needs the API contract, not the messy internals.
        elif complexity >= self.HIGH_COMPLEXITY_THRESHOLD or richness >= self.RICHNESS_THRESHOLD:
            strategy = "SIGNATURE"
            reason = "High Complexity/Richness (API Focus)"

        # Rule 3: Small/Low-Cost Utility -> FULL
        # Neither central nor complex, but small enough to include fully without budget impact.
        # Typically these are simple utilities, DTOs, or config files.
        elif richness < 20:
            strategy = "FULL"
            reason = "Small Utility (Low Cost)"

        # Rule 4: Tests and Boilerplate -> SKIP (Handled by .llmignore usually, but safety net here)
        if "test" in file_path.lower() or "mock" in file_path.lower():
            strategy = "SKIP"
            reason = "Test/Mock file"

        # Priority Rank: Higher is better
        # 4 = FULL, 3 = SIGNATURE, 2 = MINIMAL, 1 = SKIP
        rank = 4 if strategy == "FULL" else 3 if strategy == "SIGNATURE" else 2 if strategy == "MINIMAL" else 1

        # Handle missing data gracefully for schema validation
        if not comp:
             comp = {"loc": 0, "api_count": 0, "cyclomatic_complexity": 1, "documentation_coverage": 0.0, "context_richness_score": 0.0}
        if not dep:
             dep = {"in_degree": 0, "out_degree": 0, "centrality_score": 0.0, "dependencies": [], "is_entry_point": False}

        return FileExtractionPlan(
            file_path=file_path,
            metrics=ContextMetrics(**comp),
            dependencies=DependencyMetrics(**dep),
            extraction_strategy=strategy,
            reason=reason,
            priority_rank=rank
        )

if __name__ == "__main__":
    # CLI Test Usage with Mock Data
    print("\n--- Testing Adaptive Routing Logic ---")
    
    mock_deps = {
        "src/core/config.py": {"centrality_score": 15, "in_degree": 20, "out_degree": 5, "dependencies": [], "is_entry_point": False}, # Core
        "src/utils/string_helpers.py": {"centrality_score": 2, "in_degree": 5, "out_degree": 3, "dependencies": [], "is_entry_point": False}, # Utility
        "src/algo/complex_logic.py": {"centrality_score": 4, "in_degree": 3, "out_degree": 1, "dependencies": [], "is_entry_point": False} # Complex logic
    }
    
    mock_comp = {
        "src/core/config.py": {"cyclomatic_complexity": 5, "context_richness_score": 30, "loc": 100, "api_count": 10, "documentation_coverage": 80},
        "src/utils/string_helpers.py": {"cyclomatic_complexity": 3, "context_richness_score": 10, "loc": 50, "api_count": 5, "documentation_coverage": 20},
        "src/algo/complex_logic.py": {"cyclomatic_complexity": 50, "context_richness_score": 80, "loc": 500, "api_count": 20, "documentation_coverage": 90}
    }
    
    engine = AdaptiveRoutingEngine(mock_deps, mock_comp)
    decisions = engine.route_all()
    
    for d in decisions:
        print(f"File: {d.file_path}")
        print(f"  Strategy: {d.extraction_strategy}")
        print(f"  Metrics:  Cent={d.dependencies.centrality_score}, Comp={d.metrics.cyclomatic_complexity}")
        print("-" * 40)
