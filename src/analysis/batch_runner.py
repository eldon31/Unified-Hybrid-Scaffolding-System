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