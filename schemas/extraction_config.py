# File: schemas/extraction_config.py
from pydantic import BaseModel, Field, conint
from typing import Dict, List, Literal, Optional

# --- Enums and Definitions ---

# Defines the Extraction Strategies used by the Adaptive Routing Decision Engine (Phase 3) [9].
ExtractionStrategy = Literal["FULL", "SIGNATURE", "MINIMAL", "SKIP"] 

# --- Data Models ---

class ContextMetrics(BaseModel):
    """
    Dynamic Analysis Metrics (Phase 2) used to measure Context Richness and Understanding Difficulty [8, 10].
    """
    loc: conint(ge=0) = Field(description="Lines of Code (LOC) in the file.")
    api_count: conint(ge=0) = Field(description="Number of public APIs (functions/classes) provided by the module.")
    cyclomatic_complexity: conint(ge=1) = Field(description="Cyclomatic Complexity (CC) score, indicating branching logic and understanding difficulty [10].")
    documentation_coverage: float = Field(description="Percentage of code covered by docstrings/comments.")
    context_richness_score: float = Field(description="Combined score for explanation value.")

class DependencyMetrics(BaseModel):
    """
    Static Analysis Metrics (Phase 1) used to measure architectural importance [8, 10].
    """
    in_degree: conint(ge=0) = Field(description="Number of other files importing this module (Core Importance) [10].")
    out_degree: conint(ge=0) = Field(description="Number of external/internal modules this file imports (Dependency Weight) [10].")
    centrality_score: float = Field(description="Calculated score (In-Degree - Out-Degree) indicating 'Essential for others' [10].")
    dependencies: List[str] = Field(description="List of other modules this file directly depends on.")
    is_entry_point: bool = Field(description="True if this is a detected main executable or service entry point.")

class FileExtractionPlan(BaseModel):
    """
    The output schema for the Adaptive Routing Engine (Phase 3), defining the final strategy per file [8, 9].
    """
    file_path: str = Field(description="The relative path of the source file.")
    metrics: ContextMetrics = Field(description="The complexity and context richness scores.")
    dependencies: DependencyMetrics = Field(description="The dependency centrality scores.")
    
    # Adaptive Routing Decisions
    extraction_strategy: ExtractionStrategy = Field(description="The chosen strategy: FULL, SIGNATURE, MINIMAL, or SKIP [9].")
    priority_rank: conint(ge=1) = Field(description="The file's final ranking for token allocation (higher is more critical).")

class ScaffoldingOutput(BaseModel):
    """
    The final manifest for the entire repository analysis, used by the Token Budget Manager [11].
    """
    repository_url: str
    total_token_budget: conint(ge=0) = Field(description="The maximum allowed tokens (e.g., 500,000 words per source) [12].")
    total_token_used: conint(ge=0) = Field(description="Real-time tokens consumed by the extraction process.")
    extraction_manifest: List[FileExtractionPlan] = Field(description="The complete list of files and their determined extraction plan.")
    architecture_summary_link: str = Field(description="Link to the final generated architecture.md.")
