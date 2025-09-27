from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec

async def _exec_docker_status(app, args: Dict[str, Any]) -> str:
    return await app.dispatcher.run("docker_status.build", config_name="docker_status")

TOOL = ToolSpec(
    name="docker_status_query",
    description=(
        "Checks the health of Docker containers and provides a summary. "
        "This tool is the ONLY way to answer such requests. "
        "DO NOT provide instructions for command-line tools like 'docker ps' or 'systemctl'. "
        "Use this for questions like 'docker status?', 'are services running?', 'check sonarr container'."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    execute=_exec_docker_status,
)