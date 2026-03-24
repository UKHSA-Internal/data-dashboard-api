# public_api/telemetry/views.py

import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .metrics import SEMANTIC_EVENTS, SEMANTIC_LATENCY


@csrf_exempt
def events(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body)
        events = payload if isinstance(payload, list) else [payload]

        for event in events:

            name = event.get("name", "unknown")
            service = event.get("service", "unknown")
            metadata = event.get("metadata", {})

            status = metadata.get("status", "success")

            # increment counter
            SEMANTIC_EVENTS.labels(
                event_name=name,
                service=service,
                status=status
            ).inc()

            # handle duration metrics (from your SDK)
            if event.get("type") == "metric":
                value = event.get("value")
                if value is not None:
                    SEMANTIC_LATENCY.labels(
                        event_name=name,
                        service=service
                    ).observe(value)

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def metrics(request):
    return HttpResponse(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST
    )


def health(request):
    return JsonResponse({"status": "ok"})