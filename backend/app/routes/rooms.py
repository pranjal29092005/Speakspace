from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db.mongo import rooms, sessions, users
from bson.objectid import ObjectId
from datetime import datetime

bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')

@bp.route('', methods=['POST'])
@jwt_required()
def create_room():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Create room
    room = {
        'name': data['name'],
        'created_by': ObjectId(user_id),
        'created_at': datetime.utcnow(),
        'participants': [],
        'status': 'waiting'  # waiting, active, completed
    }
    
    result = rooms.insert_one(room)
    
    return jsonify({
        'id': str(result.inserted_id),
        'name': room['name'],
        'status': room['status']
    }), 201

@bp.route('', methods=['GET'])
@jwt_required()
def get_rooms():
    user_id = get_jwt_identity()
    
    # Get rooms where user is a participant
    user_rooms = rooms.find({
        'participants.user_id': ObjectId(user_id)
    })
    
    return jsonify([{
        'id': str(room['_id']),
        'name': room['name'],
        'status': room['status'],
        'participants': room['participants']
    } for room in user_rooms])

@bp.route('/<room_id>/join', methods=['POST'])
@jwt_required()
def join_room(room_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get room
    room = rooms.find_one({'_id': ObjectId(room_id)})
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    # Get user
    user = users.find_one({'_id': ObjectId(user_id)})
    
    # Add participant
    participant = {
        'user_id': ObjectId(user_id),
        'name': user['name'],
        'role': data['role'],  # moderator, participant, evaluator
        'joined_at': datetime.utcnow()
    }
    
    rooms.update_one(
        {'_id': ObjectId(room_id)},
        {'$push': {'participants': participant}}
    )
    
    return jsonify({
        'message': 'Joined room successfully',
        'participant': participant
    })

@bp.route('/<room_id>/leave', methods=['POST'])
@jwt_required()
def leave_room(room_id):
    user_id = get_jwt_identity()
    
    # Remove participant
    rooms.update_one(
        {'_id': ObjectId(room_id)},
        {'$pull': {'participants': {'user_id': ObjectId(user_id)}}}
    )
    
    return jsonify({'message': 'Left room successfully'})

@bp.route('/<room_id>/start', methods=['POST'])
@jwt_required()
def start_room(room_id):
    user_id = get_jwt_identity()
    
    # Get room
    room = rooms.find_one({'_id': ObjectId(room_id)})
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    # Check if user is moderator
    moderator = next(
        (p for p in room['participants'] if p['user_id'] == ObjectId(user_id) and p['role'] == 'moderator'),
        None
    )
    if not moderator:
        return jsonify({'error': 'Only moderator can start the room'}), 403
    
    # Update room status
    rooms.update_one(
        {'_id': ObjectId(room_id)},
        {'$set': {'status': 'active'}}
    )
    
    # Create session
    session = {
        'room_id': ObjectId(room_id),
        'started_at': datetime.utcnow(),
        'participants': room['participants'],
        'status': 'active'
    }
    
    sessions.insert_one(session)
    
    return jsonify({'message': 'Room started successfully'}) 