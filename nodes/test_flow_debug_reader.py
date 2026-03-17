def test_flow_debug_reader_imports():
    import nodes.flow_debug_reader as m
    assert hasattr(m, "handle")
