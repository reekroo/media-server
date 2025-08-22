#!/usr/bin/env python3

import subprocess
import json

class DockerProvider:
    def __init__(self, container_name='organizr'):
        self.container_name = container_name

    def get_stats(self):
        stats = {
            "status": "N/A",
            "is_running": False,
            "restarts": 0,
            "exit_code": -1
        }
        try:
            cmd = ["docker", "inspect", self.container_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)[0]
            
            stats["status"] = data["State"]["Status"]
            stats["is_running"] = data["State"]["Running"]
            stats["restarts"] = data["HostConfig"]["RestartPolicy"].get("MaximumRetryCount", 0)
            stats["exit_code"] = data["State"]["ExitCode"]

        except (FileNotFoundError, json.JSONDecodeError, IndexError):
            pass
        return stats

    def get_raw_status(self):
        try:
            command = ["docker", "inspect", "-f", "{{.State.Status}}", self.container_name]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "N/A"