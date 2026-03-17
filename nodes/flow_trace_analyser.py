import json
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import TestResult, AnalysisResult
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at diagnosing Axiom flow graph failures.
Analyse the debug trace to identify: graph topology errors, edge adapter mismatches, node panics, or data type errors.
Return specific fix instructions for the GraphAssembler to apply."""


def flow_trace_analyser(log: AxiomLogger, secrets: AxiomSecrets, input: TestResult) -> AnalysisResult:
    if input.success:
        return AnalysisResult(has_error=False, error_summary="Flow executed successfully")

    api_key = secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    debug_trace = ""
    if input.output_json:
        try:
            data = json.loads(input.output_json)
            debug_trace = json.dumps(data.get("debug_events", data), indent=2)[:5000]
        except Exception:
            debug_trace = input.output_json[:5000]

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Flow execution failed:

Error: {input.error}

Debug trace:
{debug_trace or "(no trace available)"}

Identify root cause and provide fix instructions for the graph assembler."""
        }]
    )

    return AnalysisResult(
        has_error=True,
        fix_instructions=message.content[0].text,
        error_summary=input.error[:200] if input.error else "Flow execution failed",
        iteration=1,
    )
