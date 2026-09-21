from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from functools import wraps
import jwt


SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')


def token_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get('Authorization', '')
        if not authorization.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401

        try:
            payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=['HS256'])
        except jwt.PyJWTError:
            return jsonify({'error': 'Invalid or expired token'}), 401

        return view(payload, *args, **kwargs)

    return wrapped

app = Flask(__name__)
CORS(app)

# Database config from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'tasksdb')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Task Model
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }


# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'task-service'}), 200


# GET all tasks
@app.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    tasks = Task.query.filter_by(user_id=current_user['user_id']).order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200


# GET single task
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user['user_id']).first_or_404()
    return jsonify(task.to_dict()), 200


# POST create task
@app.route('/api/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    data = request.get_json()

    if not data or not isinstance(data.get('title'), str) or not data['title'].strip():
        return jsonify({'error': 'Title is required'}), 400

    new_task = Task(
        title=data['title'].strip(),
        description=data.get('description', ''),
        user_id=current_user['user_id']
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201


# PUT update task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user['user_id']).first_or_404()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    task.title = data.get('title', task.title).strip()
    if not task.title:
        return jsonify({'error': 'Title is required'}), 400
    task.description = data.get('description', task.description)

    db.session.commit()
    return jsonify(task.to_dict()), 200


# DELETE task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted', 'id': task_id}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
