def test_flow_fix_applier_imports():
    import nodes.flow_fix_applier as m
    assert hasattr(m, "handle")
