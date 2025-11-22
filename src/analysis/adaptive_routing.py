import logging
from typing import Dict, List, Literal
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"level": "%(levelname)s", "module": "adaptive_routing", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

# Define Extraction Strategies
StrategyType = Literal["FULL", "SIGNATURE", "MINIMAL", "SKIP"]

@dataclass
class FileRoutingDecision:
    """
    The final decision for a single file.
    """
    file_path: str
    centrality_score: float
    complexity_score: int
    context_richness: float
    strategy: StrategyType
    reason: str

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

    def route_all(self) -> List[FileRoutingDecision]:
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
            0 if x.strategy == "FULL" else 1 if x.strategy == "SIGNATURE" else 2,
            -x.centrality_score
        ))
        
        logger.info("Routing complete.")
        return decisions

    def _decide_strategy(self, file_path: str) -> FileRoutingDecision:
        """
        The core logic matrix for a single file.
        """
        # 1. Get Metrics (default to 0 if missing)
        dep = self.dependency_metrics.get(file_path, {})
        comp = self.complexity_metrics.get(file_path, {})
        
        centrality = dep.get('centrality', 0)
        in_degree = dep.get('in_degree', 0)
        complexity = comp.get('cyclomatic_complexity', 0)
        richness = comp.get('context_richness', 0)
        doc_coverage = comp.get('docstring_coverage', 0)

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

        # Rule 3: Tests and Boilerplate -> SKIP (Handled by .llmignore usually, but safety net here)
        if "test" in file_path.lower() or "mock" in file_path.lower():
            strategy = "SKIP"
            reason = "Test/Mock file"

        return FileRoutingDecision(
            file_path=file_path,
            centrality_score=centrality,
            complexity_score=complexity,
            context_richness=richness,
            strategy=strategy,
            reason=reason
        )

if __name__ == "__main__":
    # CLI Test Usage with Mock Data
    print("\n--- Testing Adaptive Routing Logic ---")
    
    mock_deps = {
        "src/core/config.py": {"centrality": 15, "in_degree": 20}, # Core
        "src/utils/string_helpers.py": {"centrality": 2, "in_degree": 5}, # Utility
        "src/algo/complex_logic.py": {"centrality": 4, "in_degree": 3} # Complex logic
    }
    
    mock_comp = {
        "src/core/config.py": {"cyclomatic_complexity": 5, "context_richness": 30},
        "src/utils/string_helpers.py": {"cyclomatic_complexity": 3, "context_richness": 10},
        "src/algo/complex_logic.py": {"cyclomatic_complexity": 50, "context_richness": 80, "docstring_coverage": 90}
    }
    
    engine = AdaptiveRoutingEngine(mock_deps, mock_comp)
    decisions = engine.route_all()
    
    for d in decisions:
        print(f"File: {d.file_path}")
        print(f"  Strategy: {d.strategy}")
        print(f"  Reason:   {d.reason}")
        print(f"  Metrics:  Cent={d.centrality_score}, Comp={d.complexity_score}")
        print("-" * 40)