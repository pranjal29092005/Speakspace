from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.db.mongo import rooms, sessions
from bson.objectid import ObjectId
from datetime import datetime

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    room_id = data['room_id']
    user_id = data['user_id']
    user_name = data['user_name']
    
    # Join room
    join_room(room_id)
    
    # Emit join message
    emit('user_joined', {
        'user_id': user_id,
        'user_name': user_name,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('leave')
def handle_leave(data):
    room_id = data['room_id']
    user_id = data['user_id']
    user_name = data['user_name']
    
    # Leave room
    leave_room(room_id)
    
    # Emit leave message
    emit('user_left', {
        'user_id': user_id,
        'user_name': user_name,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('message')
def handle_message(data):
    room_id = data['room_id']
    user_id = data['user_id']
    user_name = data['user_name']
    message = data['message']
    
    # Emit message
    emit('new_message', {
        'user_id': user_id,
        'user_name': user_name,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('voice_data')
def handle_voice_data(data):
    room_id = data['room_id']
    user_id = data['user_id']
    voice_data = data['voice_data']
    
    # Emit voice data to other participants
    emit('voice_data', {
        'user_id': user_id,
        'voice_data': voice_data
    }, room=room_id, include_self=False)

@socketio.on('start_recording')
def handle_start_recording(data):
    room_id = data['room_id']
    user_id = data['user_id']
    
    # Emit recording start
    emit('recording_started', {
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('stop_recording')
def handle_stop_recording(data):
    room_id = data['room_id']
    user_id = data['user_id']
    
    # Emit recording stop
    emit('recording_stopped', {
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('raise_hand')
def handle_raise_hand(data):
    room_id = data['room_id']
    user_id = data['user_id']
    user_name = data['user_name']
    
    # Emit raise hand
    emit('hand_raised', {
        'user_id': user_id,
        'user_name': user_name,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('lower_hand')
def handle_lower_hand(data):
    room_id = data['room_id']
    user_id = data['user_id']
    user_name = data['user_name']
    
    # Emit lower hand
    emit('hand_lowered', {
        'user_id': user_id,
        'user_name': user_name,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id) 