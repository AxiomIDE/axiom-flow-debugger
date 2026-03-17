import json
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at diagnosing Axiom flow graph failures.
Analyse the debug trace to identify: graph topology errors, edge adapter mismatches, node panics, or data type errors.
Return specific fix instructions for the GraphAssembler to apply."""


def flow_trace_analyser(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    if input.test_success:
        input.has_error = False
        input.error_summary = "Flow executed successfully"
        return input

    api_key = secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    debug_trace = ""
    if input.fix_instructions:
        try:
            data = json.loads(input.fix_instructions)
            debug_trace = json.dumps(data.get("debug_events", data), indent=2)[:5000]
        except Exception:
            debug_trace = input.fix_instructions[:5000]

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Flow execution failed:

Error: {input.test_error}

Debug trace:
{debug_trace or "(no trace available)"}

Identify root cause and provide fix instructions for the graph assembler."""
        }]
    )

    input.has_error = True
    input.fix_instructions = message.content[0].text
    input.error_summary = (input.test_error or "Flow execution failed")[:200]
    input.iteration = input.iteration + 1

    return input
