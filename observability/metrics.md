# **📊 Operational Context & Observability Standards**

**Purpose:** This specification defines the runtime behavior standards for the Unified Scaffolding System. The LLM must adhere to these patterns when generating code to ensure consistency in logging, tracing, and metric collection [1].

## **1. Logging Standards (Structured JSON)**

To ensure logs are machine-parsable by downstream tools (e.g., Datadog, Splunk), all logs must follow the **Structured JSON** format [2]. The LLM should not use print statements or unstructured text logging.

### **Standard Log Schema**

```json
{
  "level": "INFO | WARN | ERROR",
  "timestamp": "ISO-8601",
  "service": "scaffold-engine",
  "module": "dependency_graph",
  "trace_id": "<correlation_id>",
  "message": "Human readable event description",
  "context": {
    "file_path": "src/core/parser.py",
    "metric_value": 450
  }
}
```

### **LLM Implementation Rule**

* **DO:** `logger.info("Parsing complete", extra={"files_processed": count})`
* **DON'T:** `print(f"Parsing complete: {count} files")`

## **2. Key Performance Indicators (KPIs)**

The LLM should be aware of the following critical metrics when suggesting optimizations or refactoring code [3]:

| Metric | Definition | Threshold (SLA) |
| :---- | :---- | :---- |
| **Extraction Latency** | Time taken to parse and extract a single file. | < 200ms per file |
| **Token Budget Utilization** | % of the 500,000 token limit consumed. | Warn at 80%, Critical at 95% |
| **Graph Build Time** | Time to construct the full dependency graph. | < 5 seconds for 10k LOC |
| **Memory Footprint** | Peak RAM usage during AST parsing. | < 512MB |

## **3. Tracing and Correlation**

To debug issues across the hybrid pipeline (Python Engine → CLI → VS Code), context must be propagated.

* **Trace ID:** Every execution of the CLI must generate a unique `trace_id`.
* **Propagation:** If the Python engine calls a subprocess or external tool (like git), the `trace_id` must be passed via environment variables (`TRACE_ID`) [4].

## **4. Error Handling Protocol**

When the LLM generates error handling blocks, it must follow this categorization:

1. **Retryable Errors:** (e.g., Network timeout, API rate limit) -> Implement Exponential Backoff.
2. **Fatal Errors:** (e.g., Missing configuration, Syntax Error) -> Fail fast and log stack trace with level: ERROR.
3. **Soft Failures:** (e.g., A single file fails parsing) -> Log as WARN, skip file, and continue execution (Partial Success) [5].

*References:*

* [1] OpenTelemetry Standards
* [2] 12-Factor App: Treat logs as event streams
* [3] Site Reliability Engineering (SRE) Handbook
