def test_package_import() -> None:
    import requirements_agent

    assert requirements_agent.__version__ == "0.1.0"


def test_core_dependencies_import() -> None:
    import langgraph
    import pydantic
    from langchain_aws import ChatBedrockConverse

    assert langgraph is not None
    assert pydantic is not None
    assert ChatBedrockConverse is not None