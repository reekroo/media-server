import docker
from docker.models.containers import Container

class DockerReport:
    def __init__(self, name: str, container_id: str, status: str, state: dict):
        self.name = name
        self.container_id = container_id
        self.status = status
        self.state = state

    def model_dump(self) -> dict:
        return {
            "name": self.name,
            "id": self.container_id[:12],
            "status": self.status,
            "exit_code": self.state.get("ExitCode", 0),
            "error": self.state.get("Error", "")
        }

class DockerCollector:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException:
            print("Error: Docker daemon is not running or accessible.")
            self.client = None

    def analyze_containers(self, ignore_list: list[str] | None = None) -> list[DockerReport]:
        if not self.client:
            return []

        ignore_list = ignore_list or []
        problem_containers = []
        
        containers: list[Container] = self.client.containers.list(all=True)

        for container in containers:
            if container.name in ignore_list:
                continue

            is_error_exit = (container.status == 'exited' and container.attrs['State'].get('ExitCode', 0) != 0)
            is_restarting = container.status == 'restarting'
            is_abnormal_state = container.status in ['dead', 'paused']

            if is_error_exit or is_restarting or is_abnormal_state:
                report = DockerReport(
                    name=container.name,
                    container_id=container.id,
                    status=container.status,
                    state=container.attrs.get('State', {})
                )
                problem_containers.append(report)
                
        return problem_containers