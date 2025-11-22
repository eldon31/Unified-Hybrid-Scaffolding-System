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

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CLI")

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