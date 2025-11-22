# 📘 Domain Blueprint: app

## 1. Core Entities (High Centrality)
These modules are the structural foundation of the codebase.
* **schemas/extraction_config.py** (Centrality: 3.0)
* **src/analysis/logger.py** (Centrality: 0.0)
* **src/analysis/extractor.py** (Centrality: 0.0)
* **src/analysis/orchestrator.py** (Centrality: 0.0)
* **src/analysis/batch_runner.py** (Centrality: 0.0)

## 2. Complexity Hotspots (High Difficulty)
These modules contain the densest logic.
* **src/analysis/dependency_graph.py** (Cyclomatic Complexity: 47)
* **src/analysis/extractor.py** (Cyclomatic Complexity: 34)
* **src/analysis/complexity.py** (Cyclomatic Complexity: 22)
* **src/analysis/adaptive_routing.py** (Cyclomatic Complexity: 18)
* **src/analysis/orchestrator.py** (Cyclomatic Complexity: 14)
