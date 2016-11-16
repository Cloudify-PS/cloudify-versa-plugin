from requests import codes
import time
from cloudify import exceptions as cfy_exc

MAX_RETRY = 30
SLEEP_TIME = 3
COMPLETED = 'COMPLETED'
FAILED = 'FAILED'


def get_all_tasks(client):
    url = "/api/operational/tasks/task?deep=true"
    return client.get(url, None, None, codes.ok)


def get_task_info(client, task):
    url = "/api/operational/tasks/task/" + task
    return client.get(url, None, None, codes.ok)


def wait_for_task(client, task, ctx):
    for retry in range(MAX_RETRY):
        ctx.logger.info("Waiting for task. Try {}/{}".format(retry + 1,
                                                             MAX_RETRY))
        task_info = get_task_info(client, task)
        status = task_info['task']['task-status']
        if status == FAILED:
            raise cfy_exc.NonRecoverableError(
                "Task FAILED: {}".format(task_info))
        if status == COMPLETED:
            return
        time.sleep(SLEEP_TIME)
    raise cfy_exc.NonRecoverableError("Task taimeout error")
