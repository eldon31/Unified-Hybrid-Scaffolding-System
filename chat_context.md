# **Project Design Journal: Unified Hybrid Scaffolding System**

Date: November 22, 2025  
Topic: Context Engineering for NotebookLM  
Goal: Create a system to transform raw code repositories into high-signal AI context.

## **📖 Table of Contents**

1. [Chapter 1: The Ambiguity Problem & Context Boundaries](https://www.google.com/search?q=%23chapter-1-the-ambiguity-problem--context-boundaries)  
2. [Chapter 2: The Tooling Strategy (VS Code & Python)](https://www.google.com/search?q=%23chapter-2-the-tooling-strategy-vs-code--python)  
3. [Chapter 3: Strategy Evolution (Git vs. Architecture)](https://www.google.com/search?q=%23chapter-3-strategy-evolution-git-vs-architecture)  
4. [Chapter 4: The Hybrid Solution (Static \+ Dynamic)](https://www.google.com/search?q=%23chapter-4-the-hybrid-solution-static--dynamic)  
5. [Chapter 5: The System Architecture (The 6 Phases)](https://www.google.com/search?q=%23chapter-5-the-system-architecture-the-6-phases)  
6. [Chapter 6: Operational Excellence](https://www.google.com/search?q=%23chapter-6-operational-excellence)

## **Chapter 1: The Ambiguity Problem & Context Boundaries**

### **The Core Challenge**

The integration of Large Language Models (LLMs) into software development represents a shift from human-readable documentation to **machine-readable context**. A human developer intuitively knows that a utils folder is less important than core, but an LLM treats them as equal tokens. This leads to "Context Drift" and "Hallucinations."

To solve this, we defined the discipline of **Context Engineering**: structuring, formatting, and curating repository information to maximize the signal-to-noise ratio.

### **The Solution: The Context Pack**

We established that a repository needs a standard set of files to guide the AI. We scaffolded these critical artifacts:

1. **.llmignore (The Boundary):**  
   * *Purpose:* Acts as an exclusionary specification. It filters out lock files, test fixtures, and binary data that waste tokens and dilute the LLM's attention.  
   * *Key Decision:* Strictly exclude \*.lock, node\_modules, and large data files to preserve the 500k token budget for logic.  
2. **llms.txt (The Sitemap):**  
   * *Purpose:* Modeled after robots.txt, this provides a deterministic path for knowledge acquisition. It tells the AI explicitly: "Read architecture.md first, then blueprint.md."  
3. **repomix.config.json (The Configuration):**  
   * *Purpose:* Ensures that any automated ingestion tool uses our curated view of the code, rather than default settings. It enforces Markdown output (which performs 25% better than PDF) and comment stripping.

## **Chapter 2: The Tooling Strategy (VS Code & Python)**

### **The "IDE-Native" Approach**

We moved away from creating a standalone CLI tool or a Docker container in favor of an **Integrated VS Code Workflow**.

* **Why VS Code?** It is the developer's native environment. Context generation should not require context switching.  
* **Why Python?** It offers the strongest libraries for AST parsing (ast) and token counting (tiktoken), which are essential for the "Brain" of our system.

### **The Workflow Design**

1. **Trigger:** The user presses Ctrl+Shift+B in VS Code.  
2. **Execution:** This triggers a Python script in a virtual environment.  
3. **Output:** The script generates the Markdown artifacts directly in the repo root.  
4. **Feedback:** Real-time logs with emoji indicators (✅, ⚠️) appear in the integrated terminal.

## **Chapter 3: Strategy Evolution (Git vs. Architecture)**

This was the most critical pivot in our design process. We explored two distinct methodologies for deciding *what* to extract.

### **Attempt 1: The Git-First Hypothesis**

* **The Idea:** Use git log to find "Hotspots" (frequently modified files) and "Temporal Coupling" (files that change together).  
* **The Logic:** If a file changes often, it must be important.  
* **The Flaw:** High modification frequency often indicates instability, not architectural importance. Conversely, a core configuration file might never change but is critical for understanding the system.  
* **The Decision:** We discarded modification frequency as a primary signal for *context*, though we kept "Knowledge Silo" analysis as a secondary risk metric.

### **Attempt 2: The Architecture-First Mapping**

* **The Idea:** Ignore activity and look at **Structure**. Map the code based on Import Dependencies.  
* **The Logic:** Files that are imported by many other files (High In-Degree) are the "Spine" of the application.  
* **The Result:** This provided a much truer map of the system's foundation (e.g., config.py, base\_models.py) regardless of how often they were edited.

## **Chapter 4: The Hybrid Solution (Static \+ Dynamic)**

We realized that neither Static Analysis (Dependencies) nor Dynamic Analysis (Complexity) was perfect on its own. We merged them into a **Unified Hybrid System**.

### **The 3-Layer Decision Engine**

We designed an engine that combines signals to make "Adaptive Routing" decisions for every file:

1. **Static Layer (Dependency Graph):**  
   * Calculates **Centrality**.  
   * *Question:* "Is this file a dependency for others?"  
2. **Dynamic Layer (Complexity Metrics):**  
   * Calculates **Cyclomatic Complexity** and **API Density**.  
   * *Question:* "Is this file hard to understand?"  
3. **Adaptive Routing (The Decision):**  
   * *Logic:* If a file is **Central** (Important) but **Simple**, extract it FULLY.  
   * *Logic:* If a file is **Complex** (Hard), extract only the **SIGNATURES** to save tokens while preserving the API contract.  
   * *Logic:* If a file is **Peripheral** (Utility), extract **MINIMALLY** (docstrings).

## **Chapter 5: The System Architecture (The 6 Phases)**

We formalized the execution flow into a 6-phase pipeline orchestrated by Python:

* **Phase 1: Static Analysis (dependency\_graph.py)**  
  * Scans raw source code.  
  * Builds an Import Graph.  
  * Identifies "Core Modules" (High In-Degree).  
* **Phase 2: Dynamic Analysis (complexity.py)**  
  * Parses AST to count Functions, Classes, and Logic Branches.  
  * Assigns a "Richness Score."  
* **Phase 3: Adaptive Routing (adaptive\_routing.py)**  
  * The traffic controller. It assigns a strategy (FULL, SIGNATURE, MINIMAL, SKIP) to every file based on the metrics from Phases 1 & 2\.  
* **Phase 4: Orchestration (orchestrator.py)**  
  * The budget manager. It uses tiktoken to count tokens in real-time.  
  * It enforces the 500,000-word limit by prioritizing high-value content.  
* **Phase 5: Extraction (extractor.py)**  
  * The surgeon. It reads files and, if the strategy dictates, surgically removes function bodies using AST manipulation to leave only the signatures.  
* **Phase 6: Assembly & Output**  
  * Generates the final Markdown artifacts:  
    * scaffold.md: The extract code.  
    * architecture.md: The high-level map.  
    * blueprint.md: The domain entity analysis.

## **Chapter 6: Operational Excellence**

We concluded by ensuring the system is robust, observable, and automated.

### **1\. Observability (observability/metrics.md)**

We defined standards for runtime behavior. The LLM/System must use **Structured JSON Logging** so that failures (like a file parsing error) are machine-readable. We defined SLAs (e.g., extraction must take \<200ms per file).

### **2\. Workflow Context (CONTRIBUTING.md)**

We created a guide that explains the Git Branching Strategy (Feature Branches) and Commit Standards (Conventional Commits). This helps the LLM understand *how* to modify the code it has just analyzed.

### **3\. Automation (CI/CD)**

We added a GitHub Actions workflow (.github/workflows/scaffold.yml) to close the loop. Now, whenever code is pushed, the Scaffolding System runs automatically in the cloud, regenerating the scaffold.md file and committing it back. This ensures the documentation never drifts from the reality of the code.

### **Conclusion**

We have moved from a simple "file dumper" to a **Semantic-Aware Context Engine**. This system doesn't just read code; it *understands* architectural importance and complexity, ensuring that the context provided to NotebookLM is the highest possible signal with the lowest possible noise.