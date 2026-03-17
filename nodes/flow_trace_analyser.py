import json
import logging
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import TestResult, AnalysisResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at diagnosing Axiom flow graph failures.
Analyse the debug trace to identify: graph topology errors, edge adapter mismatches, node panics, or data type errors.
Return specific fix instructions for the GraphAssembler to apply."""


def handle(result: TestResult, context) -> AnalysisResult:
    if result.success:
        return AnalysisResult(has_error=False, error_summary="Flow executed successfully")

    api_key = context.secrets.get("ANTHROPIC_API_KEY") if hasattr(context, 'secrets') else os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    debug_trace = ""
    if result.output_json:
        try:
            data = json.loads(result.output_json)
            debug_trace = json.dumps(data.get("debug_events", data), indent=2)[:5000]
        except Exception:
            debug_trace = result.output_json[:5000]

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Flow execution failed:

Error: {result.error}

Debug trace:
{debug_trace or "(no trace available)"}

Identify root cause and provide fix instructions for the graph assembler."""
        }]
    )

    return AnalysisResult(
        has_error=True,
        fix_instructions=message.content[0].text,
        error_summary=result.error[:200] if result.error else "Flow execution failed",
        iteration=1,
    )
