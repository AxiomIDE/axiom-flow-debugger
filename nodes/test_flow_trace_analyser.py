from nodes.flow_trace_analyser import flow_trace_analyser


def test_flow_trace_analyser_imports():
    assert callable(flow_trace_analyser)
