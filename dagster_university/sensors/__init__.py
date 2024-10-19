from dagster import RunRequest, sensor, SensorResult, SensorEvaluationContext
from ..jobs import adhoc_request_job
import os
import json


@sensor(job=adhoc_request_job)
def adhoc_request_sensor(context: SensorEvaluationContext):
    dir_path = os.path.join(os.path.dirname(__file__), "../../", "data/requests")
    files_and_dirs = os.listdir(dir_path)
    files = [
        file
        for file in files_and_dirs
        if file.endswith(".json") and os.path.isfile(os.path.join(dir_path, file))
    ]
    cursor = context.cursor if context.cursor else {}
    run_requests = []
    new_state = {}
    for file in files:
        file_path = os.path.join(dir_path, file)
        last_modified = os.path.getmtime(file_path)
        new_state[file] = last_modified
        if file not in cursor or cursor[file] != last_modified:
            with open(file_path, "r") as f:
                request_config = json.load(f)
            run_requests.append(
                RunRequest(
                    run_key=f"adhoc_request_{file}_{last_modified}",
                    run_config={
                        "ops":{
                            "adhoc_request":{
                                "config":{
                                    "filename": file,
                                    **request_config
                                }
                            }
                        }
                    }
                )
            )
            return SensorResult(
                run_requests=run_requests,
                cursor=json.dumps(new_state)
            )
