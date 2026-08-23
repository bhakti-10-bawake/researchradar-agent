import json
import time
from datetime import datetime
from pathlib import Path


TRACE_FILE = Path("observability_trace.json")


class ObservabilityTracer:

    def __init__(self):
        self.events = []
        self.started_at = time.perf_counter()

    def start(self, agent, action, details="", prompt=None):
        event = {
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "agent": agent,
            "action": action,
            "status": "started",
            "details": details,
            "prompt": prompt or "",
            "start_time": time.perf_counter(),
        }

        self.events.append(event)
        return len(self.events) - 1

    def finish(
        self,
        event_id,
        status="success",
        details="",
        token_usage=None,
        error=None,
    ):
        event = self.events[event_id]

        event["status"] = status
        event["details"] = details
        event["latency_ms"] = round(
            (time.perf_counter() - event["start_time"]) * 1000,
            2,
        )

        event.pop("start_time", None)

        if token_usage:
            event["token_usage"] = token_usage

        if error:
            event["error"] = str(error)

    def record(
        self,
        agent,
        action,
        status="info",
        details="",
        latency_ms=0,
        token_usage=None,
        error=None,
    ):
        self.events.append({
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "agent": agent,
            "action": action,
            "status": status,
            "details": details,
            "latency_ms": latency_ms,
            "token_usage": token_usage or {},
            "error": str(error) if error else "",
        })

    def diagnose(self):
        failures = [
            e for e in self.events
            if e.get("status") in ("error", "failed")
        ]

        if not failures:
            diagnosis = {
                "status": "healthy",
                "root_cause": "No execution failure detected",
                "recovery": "No recovery required",
            }
        else:
            failed = failures[-1]

            diagnosis = {
                "status": "failure_detected",
                "root_cause": (
                    f"{failed.get('agent')} / "
                    f"{failed.get('action')} failed: "
                    f"{failed.get('error') or failed.get('details')}"
                ),
                "recovery": (
                    "Fallback tool selection and evidence-grounded "
                    "continuation activated."
                ),
            }

        self.record(
            "Observability Agent",
            "Root-cause diagnosis",
            "success",
            diagnosis["root_cause"],
        )

        return diagnosis

    def metrics(self):
        completed = [
            e for e in self.events
            if "latency_ms" in e
        ]

        failures = [
            e for e in self.events
            if e.get("status") in ("error", "failed")
        ]

        total_tokens = 0

        for event in self.events:
            usage = event.get("token_usage", {})

            total_tokens += (
                usage.get("total_token_count", 0)
                or usage.get("total_tokens", 0)
                or 0
            )

        total_latency = round(
            (time.perf_counter() - self.started_at) * 1000,
            2,
        )

        return {
            "total_latency_ms": total_latency,
            "traced_events": len(self.events),
            "completed_events": len(completed),
            "errors": len(failures),
            "total_tokens": total_tokens,
            "tool_calls": sum(
                1 for e in self.events
                if "tool" in e.get("action", "").lower()
                or "api" in e.get("action", "").lower()
            ),
        }

    def save(self, diagnosis=None, before=None, after=None):
        output = {
            "timestamp": datetime.now().isoformat(),
            "diagnosis": diagnosis or {},
            "before": before or {},
            "after": after or self.metrics(),
            "events": self.events,
        }

        TRACE_FILE.write_text(
            json.dumps(output, indent=2, default=str),
            encoding="utf-8",
        )

        return output
    