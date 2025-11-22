# **Unified Hybrid Scaffolding System 🏗️**

A context-aware documentation engine that transforms raw code repositories into high-signal "Context Packs" optimized for Google NotebookLM.

## **🚀 Quick Start**

### **1\. Installation**

Run the setup script to create the virtual environment and install dependencies:

./setup\_workspace.sh

### **2\. Setup Repositories**

Clone your target repositories into the repos/ folder:

cd repos  
git clone \[https://github.com/your-org/mcp-server.git\](https://github.com/your-org/mcp-server.git)  
git clone \[https://github.com/your-org/rag-pipeline.git\](https://github.com/your-org/rag-pipeline.git)

### **3\. Run Scaffolding**

Open this folder in VS Code (code multi-repo-scaffold.code-workspace).

* **Option A (Batch):** Press Ctrl+Shift+B. This scaffolds **ALL** repositories in repos/.  
* **Option B (Single):** Press Ctrl+Shift+P, type Tasks: Run Task, select 🎯 Scaffold Specific Repository, and enter the folder name.

## **📂 Output: The Context Pack**

After running the system, each repository will contain these AI-ready files:

| File | Purpose | Strategy |
| :---- | :---- | :---- |
| scaffold.md | **The Code.** Contains the extracted source code. | **Hybrid:** Core modules are full; complex modules are signatures. |
| architecture.md | **The Map.** High-level architecture overview. | **Static:** Derived from dependency graph centrality. |
| blueprint.md | **The Domain.** Entity relationships and hotspots. | **Dynamic:** Derived from complexity analysis. |
| llms.txt | **The Index.** Sitemap for the AI. | **Static:** Auto-generated template. |
| observability/metrics.md | **The Rules.** Runtime logging standards. | **Static:** Auto-generated template. |

## **🧠 System Architecture**

The engine runs in **6 Phases**:

1. **Static Analysis (dependency\_graph.py)**: Maps imports to find "Centrality".  
2. **Dynamic Analysis (complexity.py)**: Counts LOC/CC to find "Difficulty".  
3. **Adaptive Routing (adaptive\_routing.py)**: Decides FULL vs SIGNATURE extraction.  
4. **Orchestration (orchestrator.py)**: Manages the 500k token budget.  
5. **Extraction (extractor.py)**: Surgically processes the text.  
6. **Batching (batch\_runner.py)**: Scales to multi-repo setups.

## **🛠️ Troubleshooting**

* **Logs:** Check the VS Code terminal for emoji-coded logs (✅ Success, ⚠️ Warning, ❌ Error).  
* **Token Limits:** If scaffold.md is truncated, check the logs for "Token limit reached".