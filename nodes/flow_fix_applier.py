from gen.axiom_official_axiom_agent_messages_messages_pb2 import AnalysisResult, AgentProgress


def handle(analysis: AnalysisResult, context) -> AgentProgress:
    """Route fix instructions to the FlowDesigner to rebuild the problematic graph portion."""
    if not analysis.has_error:
        return AgentProgress(
            stage="complete",
            message="Flow debug analysis complete — no errors found.",
            complete=True,
            success=True,
        )

    return AgentProgress(
        stage="fix_required",
        message=f"Flow fix required: {analysis.error_summary}\n\n{analysis.fix_instructions}",
        complete=False,
        success=False,
    )
