from flask import Flask, request, jsonify, abort
from marshmallow import Schema, fields
from marshmallow.validate import Range
from db import TaskGRUD
from utils import Status

app = Flask(__name__)

class TaskSchema(Schema):
    hostname = fields.Str(required=False)
    post_n = fields.Int(required=True, validate=Range(min=1))
    instagram_login = fields.Str(required=True)


task_schema = TaskSchema()

@app.route("/create_task", methods=['post', 'get'])
def create_task():
    data = request.get_json()
    errors = task_schema.validate(data)
    if errors:
        abort(400, str(errors))

    hostname = data.get('hostname') or 'host'
    post_n = data.get('post_n')
    instagram_login = data.get('instagram_login')

    TaskGRUD.create(profile=instagram_login, number_of_posts=post_n, hostname=hostname)
    return jsonify({'massage': 'task created'}), 201

@app.route("/tasks/<status>", methods=['get'])
def tasks(status):
    if status not in [Status.NEW, Status.IN_WORK, Status.FINISHED]:
        abort(400, 'Status is not valid')
    
    return jsonify(TaskGRUD.get_tasks_by_status(status))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)