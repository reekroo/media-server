
import subprocess
import json

class DockerProvider:

    def get_stats(self):
        stats = {
            "status": "N/A",
            "is_running": False,
            "restarts": 0,
            "total_containers": 0,
            "running_containers": 0,
            "unhealthy_containers": 0
        }
        try:
            cmd = ["docker", "ps", "-a", "--format", "{{json .}}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            total_containers = 0
            running_containers = 0
            unhealthy_containers = 0
            
            for line in result.stdout.strip().split('\n'):
                if not line: continue
                total_containers += 1
                container = json.loads(line)
                if "running" in container.get("Status", "").lower():
                    running_containers += 1
                if "unhealthy" in container.get("Status", "").lower():
                    unhealthy_containers += 1
            
            stats["total_containers"] = total_containers
            stats["running_containers"] = running_containers
            stats["unhealthy_containers"] = unhealthy_containers
            stats["is_running"] = unhealthy_containers == 0 and running_containers > 0

        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, IndexError):
            pass
        return stats