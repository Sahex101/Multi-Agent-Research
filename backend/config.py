import logging
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # ── Azure OpenAI (GitHub Education: $100 Azure for Students credit) ──
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""            # e.g. https://YOUR-RESOURCE.openai.azure.com/
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_deployment_name: str = "gpt-4o-mini" # your deployed model name in Azure

    # ── OpenRouter fallback (free tier) ───────────────────────────────────
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "inclusionai/ling-2.6-1t:free"

    # ── Search (Tavily primary, DuckDuckGo fallback) ─────────────────────
    tavily_api_key: str = ""

    cors_origins: list[str] = ["*"]

    # ── Rate limiting ─────────────────────────────────────────────────────
    max_sessions_per_day: int = 10
    max_sessions_per_month: int = 250

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def use_azure(self) -> bool:
        return bool(self.azure_openai_api_key and self.azure_openai_endpoint)


settings = Settings()
_azure_failed_until: float = 0.0  # timestamp — retries Azure after this time


def get_llm(_model: str | None = None) -> ChatOpenAI | AzureChatOpenAI:
    """Returns Azure OpenAI if credentials are set, otherwise falls back to OpenRouter."""
    import time
    if settings.use_azure and time.time() > _azure_failed_until:
        return AzureChatOpenAI(
            azure_deployment=settings.azure_deployment_name,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            temperature=0.7,
        )
    if _azure_failed_until > 0:
        logger.warning("Azure deployment unavailable — using OpenRouter fallback")
    return ChatOpenAI(
        model=settings.openrouter_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        temperature=0.7,
        default_headers={
            "HTTP-Referer": "https://github.com/your-username/multi-agent-research",
            "X-Title": "Multi-Agent Research Assistant",
        },
    )


def mark_azure_failed():
    """Temporarily disable Azure for 5 minutes, then auto-retry."""
    global _azure_failed_until
    import time
    _azure_failed_until = time.time() + 300  # retry after 5 min
    logger.warning("Azure DeploymentNotFound — switched to OpenRouter, will retry Azure in 5 min")
