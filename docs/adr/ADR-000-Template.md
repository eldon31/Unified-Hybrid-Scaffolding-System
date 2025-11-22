# Architecture Decision Record: [ADR-XXX] - [Descriptive Title]

**Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-YYY]

## Context
When an LLM refactors code, it often lacks the historical context of why a specific pattern was chosen [3]. This section captures the architectural problem, the forces, and the constraints that necessitated a decision:

*   **The Problem:** [Describe the technical issue, business requirement, or ambiguity encountered.]
*   **Architectural Constraint:** [Example: We must maintain compatibility with Python 3.9, or latency must be under 50ms.]
*   **Historical Context:** [Example: We chose a custom serializer over Pydantic initially due to a specific memory leak in the production environment in 2023.]

## Decision
[State the proposed change or solution. The format should be brief, summarizing the core choice.]

We have decided to [Action Verb] by implementing [Solution or Pattern, e.g., using a Modular Monolith architecture for boundaries, or adopting a Trunk-Based Development Git strategy].

## Consequences
This section explicitly lists the trade-offs, which prevents the LLM from generating "optimizations" that violate the original intent [4].

### Positive Consequences (Pros)
*   [Benefit 1: e.g., Improved component isolation.]
*   [Benefit 2: e.g., Reduced token overhead in context window.]

### Negative Consequences (Cons)
*   [Drawback 1: e.g., Increased setup complexity for local development.]
*   [Drawback 2: e.g., Requires more explicit API documentation between modules.]
*   [Drawback 3: e.g., Requires explicit definition of module boundaries to avoid turning it into an unstructured "Big Ball of Mud"] [5].

---
*Reference Date: YYYY-MM-DD*
