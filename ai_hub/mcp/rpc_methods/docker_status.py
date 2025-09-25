from mcp.context import AppContext
from functions.docker_status.collector import DockerCollector
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

DOCKER_DISABLED = "🟥 Docker status digest is disabled or not configured."

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building docker_status digest for config '{config_name}'")
    cfg = app.settings.docker_status
    if not cfg or not cfg.enabled:
        return DOCKER_DISABLED

    collector = DockerCollector()
    problem_reports = collector.analyze_containers(
        ignore_list=cfg.ignore_containers
    )

    reports_payload = [res.model_dump() for res in (problem_reports or [])]

    summary_text: str = await app.ai_service.digest(
        kind="docker_status",
        params={
            "reports": reports_payload,
            "meta": {
                "ignored": list(cfg.ignore_containers or []),
                "ignored_count": len(cfg.ignore_containers or []),
            },
        },
    )

    return cfg.render_template.format(summary=summary_text)
