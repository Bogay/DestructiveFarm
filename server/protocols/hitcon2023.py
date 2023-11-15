from typing import Dict, Any, List

import requests

from server import app
from server.models import Flag, SubmitResult, FlagStatus


put_to_queue = {"reject flag submission at round pending", "Limit exceeded"}


def submit_flags(flags: List[Flag], config: Dict[str, Any]):
    system_url = config["SYSTEM_URL"]
    token = config["SYSTEM_TOKEN"]

    for flag in flags:
        resp = requests.post(
            system_url,
            headers={
                "Authorization": token,
            },
            json={"flag": flag.flag},
        )

        status = FlagStatus.QUEUED
        if resp.ok:
            status = FlagStatus.ACCEPTED
        elif 400 <= resp.status_code <= 499:
            status = FlagStatus.REJECTED
            try:
                rjson = resp.json()
                err = rjson["error"]
                if err in put_to_queue:
                    status = FlagStatus.QUEUED
            except Exception as e:
                app.logger.warning(f"failed to parse check system response: {e}")

        yield SubmitResult(flag.flag, status, resp.text)
