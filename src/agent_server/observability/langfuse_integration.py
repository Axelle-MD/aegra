import os
from typing import Any

import structlog

from .base import ObservabilityProvider

logger = structlog.getLogger(__name__)

_LANGFUSE_LOGGING_ENABLED = os.getenv("LANGFUSE_LOGGING", "false").lower() == "true"


class LangfuseProvider(ObservabilityProvider):
    """Langfuse observability provider."""

    def get_callbacks(self) -> list[Any]:
        """Return Langfuse callbacks."""
        callbacks = []
        if self.is_enabled():
            try:
                from langfuse.langchain import CallbackHandler

                # Handler is now stateless, metadata will be passed in config
                handler = CallbackHandler()
                callbacks.append(handler)
                logger.info("Langfuse tracing enabled, handler created.")
            except ImportError:
                logger.warning(
                    "LANGFUSE_LOGGING is true, but 'langfuse' is not installed. "
                    "Please run 'pip install langfuse' to enable tracing."
                )
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse CallbackHandler: {e}")

        return callbacks

    def get_metadata(
        self, run_id: str, thread_id: str, user_identity: str | None = None
    ) -> dict[str, Any]:
        """Return Langfuse-specific metadata."""
        metadata: dict[str, Any] = {
            "langfuse_session_id": thread_id,
        }

        if user_identity:
            metadata["langfuse_user_id"] = user_identity
            metadata["langfuse_tags"] = [
                "aegra_run",
                f"run:{run_id}",
                f"thread:{thread_id}",
                f"user:{user_identity}",
            ]
        else:
            metadata["langfuse_tags"] = [
                "aegra_run",
                f"run:{run_id}",
                f"thread:{thread_id}",
            ]

        return metadata

    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled."""
        return _LANGFUSE_LOGGING_ENABLED


# Create and register the Langfuse provider
_langfuse_provider = LangfuseProvider()


def get_tracing_callbacks() -> list[Any]:
    """
    Backward compatibility function - delegates to the new observability system.
    """
    from .base import get_observability_manager

    # Register the Langfuse provider unconditionally; registration should be idempotent
    manager = get_observability_manager()
    manager.register_provider(_langfuse_provider)

    return manager.get_all_callbacks()


def _get_langfuse_client():
    """Lazily create and return the Langfuse client instance."""
    if not _LANGFUSE_LOGGING_ENABLED:
        raise RuntimeError("Langfuse logging is not enabled (LANGFUSE_LOGGING != true)")
    try:
        from langfuse import Langfuse

        return Langfuse()
    except ImportError:
        raise RuntimeError(
            "langfuse package is not installed. Run 'pip install langfuse'."
        )


def send_score(
    trace_id: str,
    name: str,
    value: float,
    comment: str | None = None,
    user_id: str | None = None,
) -> str | None:
    """Send a score to Langfuse for a given trace.

    Returns the score ID if successful, None otherwise.
    """
    client = _get_langfuse_client()
    score = client.score(
        trace_id=trace_id,
        name=name,
        value=value,
        comment=comment,
        data_type="NUMERIC",
    )
    client.flush()  # Ensure the score is sent immediately
    logger.info(
        "langfuse_score_sent",
        trace_id=trace_id,
        name=name,
        value=value,
    )
    return getattr(score, "id", None)
