import json
import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import TestResult
from gen.axiom_logger import AxiomLogger, AxiomSecrets



def flow_debug_reader(log: AxiomLogger, secrets: AxiomSecrets, input: TestResult) -> TestResult:
    """Fetch the debug event stream for a flow execution."""

    if not input.session_id and not input.execution_id:
        return input

    ingress_url = os.environ.get("INGRESS_URL", "http://axiom-ingress:80")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")
    tenant_id = os.environ.get("TENANT_ID", "01AXIOMOFFICIAL000000000000")

    session_id = input.session_id or input.execution_id

    try:
        resp = httpx.get(
            f"{ingress_url}/v1/debug-events",
            params={"session_id": session_id, "limit": "200"},
            headers={
                "Authorization": f"Bearer {axiom_api_key}",
                "X-Tenant-Id": tenant_id,
            },
            timeout=15.0,
        )
        if resp.status_code == 200:
            events = resp.json()
            enriched = TestResult()
            enriched.CopyFrom(input)
            enriched.output_json = json.dumps({"debug_events": events, "session_id": session_id})
            return enriched
    except Exception as e:
        log.warning(f"Failed to fetch flow debug events: {e}")

    return input
