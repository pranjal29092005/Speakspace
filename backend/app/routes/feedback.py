from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db.mongo import feedback, sessions, users
from bson.objectid import ObjectId
from datetime import datetime
import openai

bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

@bp.route('/session/<session_id>', methods=['POST'])
@jwt_required()
def generate_feedback(session_id):
    user_id = get_jwt_identity()
    
    # Get session
    session = sessions.find_one({'_id': ObjectId(session_id)})
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Get user's participation data
    participation_data = request.get_json()
    
    # Generate AI feedback using OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert communication skills evaluator."},
                {"role": "user", "content": f"""
                Evaluate the following participation data:
                Speaking time: {participation_data.get('speaking_time', 0)} seconds
                Number of contributions: {participation_data.get('contributions', 0)}
                Topics covered: {participation_data.get('topics', [])}
                Key points made: {participation_data.get('key_points', [])}
                
                Provide feedback on:
                1. Communication clarity and effectiveness
                2. Content quality and relevance
                3. Engagement level
                4. Areas for improvement
                """}
            ]
        )
        
        ai_feedback = response.choices[0].message.content
        
        # Calculate confidence score (placeholder)
        confidence_score = min(100, (
            participation_data.get('speaking_time', 0) / 300 * 40 +  # 40% weight for speaking time
            participation_data.get('contributions', 0) * 10 +  # 10 points per contribution
            len(participation_data.get('key_points', [])) * 5  # 5 points per key point
        ))
        
        # Store feedback
        feedback_data = {
            'session_id': ObjectId(session_id),
            'user_id': ObjectId(user_id),
            'confidence_score': confidence_score,
            'ai_feedback': ai_feedback,
            'participation_data': participation_data,
            'created_at': datetime.utcnow()
        }
        
        feedback.insert_one(feedback_data)
        
        return jsonify({
            'confidence_score': confidence_score,
            'ai_feedback': ai_feedback
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_feedback(user_id):
    # Get all feedback for user
    user_feedback = feedback.find({
        'user_id': ObjectId(user_id)
    }).sort('created_at', -1)
    
    return jsonify([{
        'id': str(fb['_id']),
        'session_id': str(fb['session_id']),
        'confidence_score': fb['confidence_score'],
        'ai_feedback': fb['ai_feedback'],
        'created_at': fb['created_at']
    } for fb in user_feedback])

@bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    # Get top 10 users by average confidence score
    pipeline = [
        {
            '$group': {
                '_id': '$user_id',
                'avg_score': {'$avg': '$confidence_score'},
                'total_sessions': {'$sum': 1}
            }
        },
        {'$sort': {'avg_score': -1}},
        {'$limit': 10}
    ]
    
    leaderboard = list(feedback.aggregate(pipeline))
    
    # Get user details
    user_ids = [entry['_id'] for entry in leaderboard]
    users_dict = {
        str(user['_id']): user
        for user in users.find({'_id': {'$in': user_ids}})
    }
    
    return jsonify([{
        'user_id': str(entry['_id']),
        'name': users_dict[str(entry['_id'])]['name'],
        'avg_score': entry['avg_score'],
        'total_sessions': entry['total_sessions']
    } for entry in leaderboard]) 