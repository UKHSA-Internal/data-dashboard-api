# public_api/telemetry/metrics.py

from prometheus_client import Counter, Histogram

SEMANTIC_EVENTS = Counter(
    "semantic_events_total",
    "Semantic events received",
    ["event_name", "service", "status"]
)

SEMANTIC_LATENCY = Histogram(
    "semantic_event_duration_seconds",
    "Duration of semantic operations",
    ["event_name", "service"]
)