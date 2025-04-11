from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.db.mongo import users
import bcrypt
from datetime import datetime
from bson.objectid import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if users.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400
    
    # Hash password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), salt)
    
    # Create user
    user = {
        'email': data['email'],
        'password': hashed_password,
        'name': data['name'],
        'role': 'user',
        'created_at': datetime.utcnow()
    }
    
    users.insert_one(user)
    
    # Generate token
    access_token = create_access_token(identity=str(user['_id']))
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Find user
    user = users.find_one({'email': data['email']})
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check password
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    access_token = create_access_token(identity=str(user['_id']))
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    })

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = users.find_one({'_id': ObjectId(user_id)})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': str(user['_id']),
        'email': user['email'],
        'name': user['name'],
        'role': user['role']
    }) 