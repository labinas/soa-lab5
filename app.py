from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import json
from json import JSONEncoder

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Person class/model
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='person', lazy=True)

    def __init__(self, name, tasks = list()):
        self.name = name
        self.tasks = tasks

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'tasks': [task.serialize for task in self.tasks]
        }

# Person Schema
class PersonSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'tasks')

# Init schema
person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)        

# Task class/model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'),
        nullable=False)

    def __init__(self, description, person_id):
        self.description = description
        self.person_id = person_id

    @property
    def serialize(self):
        return {
            'id': self.id,
            'description': self.description,
            'person_id': self.person_id
        }


# Task Schema
class TaskSchema(ma.Schema):
  class Meta:
    fields = ('id', 'description', 'person_id')

# Init schema
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# Create person
@app.route('/person', methods=['POST'])
def create_person():
    name = request.json['name']

    new_person = Person(name)

    db.session.add(new_person)
    db.session.commit()

    return person_schema.jsonify(new_person)

# Get person
@app.route('/person/<id>', methods=['GET'])
def get_person(id):
    person = Person.query.get(id)
    print(person)
    return person_schema.jsonify(person.serialize)

# Get people
@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    result = persons_schema.dump([person.serialize for person in people])
    return jsonify(result)

# Update person
@app.route('/person/<id>', methods=['PUT'])
def update_person(id):
    person = Person.query.get(id)

    name = request.json['name']
    person.name = name
    
    db.session.commit()

    return person_schema.jsonify(person.serialize)

# Delete person
@app.route('/person/<id>', methods=['DELETE'])
def delete_person(id):
    person = Person.query.get(id)
    db.session.delete(person)
    db.session.commit()

    return person_schema.jsonify(person.serialize)

# Create task
@app.route('/task', methods=['POST'])
def create_task():
    description = request.json['description']
    person_id = request.json['person_id']

    person = Person.query.get(person_id)

    new_task = Task(description, person_id)
    person.tasks.append(new_task)

    db.session.commit()

    return task_schema.jsonify(new_task)

# Get task
@app.route('/task/<id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    return task_schema.jsonify(task)

# Get tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    result = tasks_schema.dump(tasks)
    return jsonify(result)

# Update task
@app.route('/task/<id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)

    description = request.json['description']
    person_id = request.json['person_id']

    task.description = description
    task.person_id = person_id
    
    db.session.commit()

    return task_schema.jsonify(task)

#  Delete task
@app.route('/task/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()

    return task_schema.jsonify(task)


# Run Server
if __name__ == '__main__':
    app.run(debug=True)