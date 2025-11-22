# 🗺️ System Context Diagram (C4 Level 1)

> This diagram defines the high-level system boundaries and interfaces for the combined architecture derived from the four repositories. This is designed to be machine-readable by LLMs.

## Architecture Visualization (Mermaid)

```mermaid
C4Container
    title Combined Repository Architecture (High Level)

    System_Boundary(core_sys, "Hybrid Scaffolding Core") {
        Container(parser, "AST/Tree-sitter Parser", "Python/Multi-Language", "Extracts signatures and builds dependency graph.")
        Container(router, "Adaptive Routing Engine", "Python", "Combines Centrality and Complexity scores to decide extraction strategy.")
        Container(orchestrator, "Context Orchestrator", "Python", "Manages token budget (tiktoken) and structural scaffolding.")
    }

    System(target_repos, "4 Target Repositories", "GitHub/Git Sources")
    System(notebook_lm, "NotebookLM Target", "AI Reasoning Platform")

    Rel(target_repos, parser, "Clones and Ingests Source Code")
    Rel(parser, router, "Sends Centrality/Complexity Scores")
    Rel(router, orchestrator, "Determines Extraction Plan (FULL/SIGNATURE)")
    Rel_R(orchestrator, notebook_lm, "Outputs Final context-scaffold.md", "Markdown (.md)")
    Rel_Back(notebook_lm, orchestrator, "Retrieval/Reasoning Feedback Loop")
```
