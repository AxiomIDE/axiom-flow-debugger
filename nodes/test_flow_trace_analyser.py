def test_flow_trace_analyser_imports():
    import nodes.flow_trace_analyser as m
    assert hasattr(m, "handle")
