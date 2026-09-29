from audit.network import collect_network


def test_collect_network():
    result = collect_network()

    assert isinstance(result, dict)

    assert "adapters" in result
    assert "ip_configuration" in result
    assert "tcp_connections" in result

    assert isinstance(result["adapters"], list)
    assert isinstance(result["ip_configuration"], list)
    assert isinstance(result["tcp_connections"], list)

    for adapter in result["adapters"]:
        assert "Name" in adapter
        assert "InterfaceDescription" in adapter
        assert "Status" in adapter
        assert "MacAddress" in adapter
        assert "LinkSpeed" in adapter

    for connection in result["tcp_connections"]:
        assert "LocalAddress" in connection
        assert "LocalPort" in connection
        assert "RemoteAddress" in connection
        assert "RemotePort" in connection
        assert "State" in connection
        assert "OwningProcess" in connection