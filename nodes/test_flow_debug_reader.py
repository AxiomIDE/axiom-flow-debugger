from nodes.flow_debug_reader import flow_debug_reader


def test_flow_debug_reader_imports():
    assert callable(flow_debug_reader)
