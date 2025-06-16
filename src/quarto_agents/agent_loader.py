import importlib
import json
import logging
import os
from typing import Any, Dict

from quarto_lib import QuartoAgent

logger = logging.getLogger(__name__)


def _parse_value(value: str) -> Any:
    """Convert a string to the appropriate Python type using json.loads."""
    value = value.strip()
    if not value:
        return None

    if "," in value:
        return [_parse_value(v) for v in value.split(",")]

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _get_agent_kwargs() -> Dict[str, Any]:
    """Extract all env variables with AGENT_ARG_ prefix and parse them."""
    prefix = "AGENT_ARG_"
    logger.debug(
        f"Agent argument environment variables: {[f'{k}={v}' for k, v in os.environ.items() if k.startswith(prefix)]}"
    )
    return {key[len(prefix) :]: _parse_value(value) for key, value in os.environ.items() if key.startswith(prefix)}


def get_agent() -> QuartoAgent:
    module_path = os.getenv("AGENT_MODULE", "quarto_agents.minimax.agent")
    class_name = os.getenv("AGENT_CLASS", "Agent")

    module = importlib.import_module(module_path)
    agent_cls = getattr(module, class_name)

    if not issubclass(agent_cls, QuartoAgent):
        raise TypeError(f"{class_name} is not a subclass of QuartoAgent")

    try:
        version_module = importlib.import_module(f"{module_path.rsplit('.', 1)[0]}.__version__")
        agent_version = getattr(version_module, "__version__", "unknown")
    except ModuleNotFoundError:
        agent_version = "unknown"
    identifier = f"{module_path.rsplit('.', 1)[0]}:v{agent_version}"

    agent_kwargs = _get_agent_kwargs()
    logger.info(f"Creating agent {identifier} with arguments: {agent_kwargs}")
    return agent_cls(identifier=identifier, **agent_kwargs)
