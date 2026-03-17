from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext, AgentProgress
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def flow_fix_applier(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> AgentProgress:
    """Route fix instructions to the FlowDesigner to rebuild the problematic graph portion."""
    if not input.has_error:
        return AgentProgress(
            stage="complete",
            message="Flow debug complete — no errors found.",
            complete=True,
            success=True,
            artifact_id=input.artifact_id,
        )

    return AgentProgress(
        stage="fix_required",
        message=f"Flow fix required after {input.iteration} iteration(s): {input.error_summary}\n\n{input.fix_instructions}",
        complete=False,
        success=False,
    )
