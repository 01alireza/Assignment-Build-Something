from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps

app = Flask(__name__)
CORS(app)

# Config
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'tasksdb')

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'user-service'}), 200


def create_token(user):
    return jwt.encode(
        {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        },
        SECRET_KEY,
        algorithm='HS256'
    )


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


# POST register
@app.route('/api/users/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not isinstance(data.get('username'), str) or not isinstance(data.get('password'), str):
        return jsonify({'error': 'Username and password required'}), 400

    username = data['username'].strip()
    password = data['password']
    if len(username) < 3 or len(username) > 80 or len(password) < 8:
        return jsonify({'error': 'Username must be 3-80 characters and password at least 8 characters'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_pw)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User created',
        'user': new_user.to_dict(),
        'token': create_token(new_user)
    }), 201


# POST login
@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'token': create_token(user),
        'username': user.username,
        'user_id': user.id
    }), 200


# GET user profile (protected)
@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    if current_user.get('user_id') != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
