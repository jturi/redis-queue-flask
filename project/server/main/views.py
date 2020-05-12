# project/server/main/views.py


import redis
from rq import Queue, Connection
from flask import render_template, Blueprint, jsonify, request, current_app

from project.server.main.tasks import create_task

main_blueprint = Blueprint("main", __name__,)


@main_blueprint.route("/", methods=["GET"])
def home():
    return render_template("main/home.html")


@main_blueprint.route("/tasks", methods=["POST"])
def run_task():
    task_type = request.form["type"]
    print('*** task_type: {}'.format(task_type))
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()
        task = q.enqueue(create_task, task_type)
        response_object = {
            "status": "success",
            "data": {
                "task_id": task.get_id()
            }
        }
        return jsonify(response_object), 202


@main_blueprint.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()
        task = q.fetch_job(task_id)
        task_result = task.result
        if not task_result:
            task_result = "pending"
        print('*** task.get_id(): {} result: {}'.format(task.get_id(), task.result))
        if task:
            response_object = {
                "status": "success",
                "data": {
                    "task_id": task.get_id(),
                    "task_status": task.get_status(),
                    "task_result": task_result,
                },
            }
        else:
            response_object = {"status": "error"}
        return jsonify(response_object)

