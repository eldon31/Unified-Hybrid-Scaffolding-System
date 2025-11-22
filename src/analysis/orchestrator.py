import sys
import json
import logging
from pathlib import Path
import tiktoken
from tqdm import tqdm

# Import our modules
from dependency_graph import DependencyGraphBuilder
from complexity import CodeComplexityAnalyzer
from adaptive_routing import AdaptiveRoutingEngine
from extractor import ContentExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"level": "%(levelname)s", "module": "orchestrator", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

class ScaffoldOrchestrator:
    """
    Phase 5: Orchestration & Token Budgeting
    
    Runs the full pipeline and generates the final Context Pack.
    """
    
    def __init__(self, repo_path: str, token_limit: int = 500000, model: str = "gpt-4o"):
        self.repo_path = Path(repo_path).resolve()
        self.token_limit = token_limit
        self.encoding = tiktoken.encoding_for_model(model)
        
        # Initialize Components
        self.dep_builder = DependencyGraphBuilder(repo_path)
        self.comp_analyzer = CodeComplexityAnalyzer(repo_path)
        self.extractor = ContentExtractor(repo_path)
        
        self.decisions = []
        self.stats = {}

    def run_pipeline(self):
        print(f"🚀 Starting Hybrid Scaffolding for: {self.repo_path.name}")
        
        # --- Phase 1: Static Analysis ---
        print("🔍 [1/5] Building Dependency Graph...")
        dep_metrics = self.dep_builder.build()
        
        # --- Phase 2: Dynamic Analysis ---
        print("🧠 [2/5] Analyzing Complexity...")
        comp_metrics = self.comp_analyzer.analyze_repo()
        
        # --- Phase 3: Adaptive Routing ---
        print("🔀 [3/5] Determining Extraction Strategies...")
        router = AdaptiveRoutingEngine(dep_metrics, comp_metrics)
        self.decisions = router.route_all()
        
        # --- Phase 4: Extraction & Budgeting ---
        print("📦 [4/5] Extracting Content & Managing Budget...")
        final_content = self._extract_with_budget()
        
        # --- Phase 5: Artifact Generation ---
        print("📝 [5/5] Generating Context Pack...")
        self._generate_artifacts(final_content, dep_metrics, comp_metrics)
        
        print("\n✅ Scaffolding Complete!")

    def _extract_with_budget(self) -> str:
        """
        Extracts content, counting tokens. If limit reached, downgrades strategies.
        """
        markdown_buffer = []
        current_tokens = 0
        
        # Header
        header = f"# Repository Scaffold: {self.repo_path.name}\n\n"
        markdown_buffer.append(header)
        current_tokens += len(self.encoding.encode(header))
        
        # Process high priority first (FULL -> SIGNATURE -> MINIMAL)
        # The router already sorted them by priority.
        
        progress_bar = tqdm(self.decisions, desc="Extracting", unit="file")
        
        for decision in progress_bar:
            if decision.strategy == "SKIP":
                continue
            
            # Extract content based on strategy
            content = self.extractor.extract(decision.file_path, decision.strategy)
            
            # Markdown Wrapper
            file_block = (
                f"\n## File: {decision.file_path}\n"
                f"**Strategy:** {decision.strategy} | **Reason:** {decision.reason}\n"
                f"```python\n{content}\n```\n"
            )
            
            # Check Budget
            block_tokens = len(self.encoding.encode(file_block))
            
            if current_tokens + block_tokens > self.token_limit:
                logger.warning(f"Token limit reached ({current_tokens}). Skipping remaining files.")
                break
            
            markdown_buffer.append(file_block)
            current_tokens += block_tokens
            
        self.stats['total_tokens'] = current_tokens
        return "".join(markdown_buffer)

    def _generate_artifacts(self, scaffold_content: str, dep_metrics: dict, comp_metrics: dict):
        """
        Writes the physical .md files to disk.
        """
        output_dir = self.repo_path
        
        # 1. scaffold.md (The Code)
        with open(output_dir / "scaffold.md", "w", encoding="utf-8") as f:
            f.write(scaffold_content)
            
        # 2. blueprint.md (The Domain Map)
        self._generate_blueprint(output_dir, dep_metrics, comp_metrics)
        
        # 3. architecture.md (The Overview)
        self._generate_architecture_doc(output_dir, dep_metrics)

    def _generate_blueprint(self, output_dir: Path, dep_metrics: dict, comp_metrics: dict):
        """
        Generates the Domain Blueprint based on analysis data.
        """
        # Identify Core Modules (High Centrality)
        core_modules = sorted(
            dep_metrics.items(), 
            key=lambda x: x[1]['centrality'], 
            reverse=True
        )[:5]
        
        # Identify Complex Modules (High CC)
        complex_modules = sorted(
            comp_metrics.items(), 
            key=lambda x: x[1]['cyclomatic_complexity'], 
            reverse=True
        )[:5]
        
        content = f"""# 📘 Domain Blueprint: {self.repo_path.name}

## 1. Core Entities (High Centrality)
These modules are the structural foundation of the codebase.
"""
        for path, m in core_modules:
            content += f"* **{path}** (Centrality: {m['centrality']})\n"
            
        content += "\n## 2. Complexity Hotspots (High Difficulty)\nThese modules contain the densest logic.\n"
        for path, m in complex_modules:
            content += f"* **{path}** (Cyclomatic Complexity: {m['cyclomatic_complexity']})\n"
            
        with open(output_dir / "blueprint.md", "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_architecture_doc(self, output_dir: Path, dep_metrics: dict):
        """
        Generates the Architecture Overview.
        """
        content = f"""# 🏗️ Architecture Overview: {self.repo_path.name}

## Analysis Stats
* **Total Files Analyzed:** {len(dep_metrics)}
* **Total Tokens Generated:** {self.stats.get('total_tokens', 0)}
* **Token Budget:** {self.token_limit}

## Context Strategy
This scaffold was generated using an **Architecture-First** approach.
* **Core Modules** were extracted fully.
* **Complex Logic** was summarized via signatures.
* **Utilities** were minimized.
"""
        with open(output_dir / "architecture.md", "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <path_to_repo>")
        sys.exit(1)
        
    target_repo = sys.argv[1]
    
    orchestrator = ScaffoldOrchestrator(target_repo)
    orchestrator.run_pipeline()