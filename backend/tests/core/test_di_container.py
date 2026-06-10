from app.core.di.container import RuntimeContainer
from tests.conftest import EchoTool


def test_runtime_container_wires_core_services(settings) -> None:
    container = RuntimeContainer(settings)

    assert container.memory_store is container.memory_store
    assert container.tool_registry is container.tool_registry
    assert container.conversation_service is not None
    assert container.agent_runtime is not None
    assert container.workflow_executor is not None


def test_runtime_container_registers_agents_and_tools(
    runtime_container,
    test_agent,
) -> None:
    runtime_container.register_agent(test_agent)
    runtime_container.register_tool(EchoTool())

    assert "test-agent" in runtime_container._agents
    assert "echo" in runtime_container.tool_registry
