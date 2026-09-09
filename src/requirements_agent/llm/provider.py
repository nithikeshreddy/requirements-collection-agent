"""LLM provider factory."""

from langchain_aws import ChatBedrockConverse
from langchain_core.language_models.chat_models import BaseChatModel

from requirements_agent.config import get_settings


def get_chat_model() -> BaseChatModel:
    """Create the configured chat model."""

    settings = get_settings()

    if settings.llm_provider != "bedrock":
        raise ValueError(
            f"Unsupported LLM provider: {settings.llm_provider}"
        )

    if not settings.bedrock_model_id:
        raise ValueError(
            "BEDROCK_MODEL_ID must be configured."
        )

    return ChatBedrockConverse(
        model_id=settings.bedrock_model_id,
        region_name=settings.aws_region,
        temperature=0,
        max_tokens=2000,
    )
