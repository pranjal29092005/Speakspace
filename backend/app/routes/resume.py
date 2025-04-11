from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db.mongo import resumes, users
from bson.objectid import ObjectId
from datetime import datetime
import openai
import os

bp = Blueprint('resume', __name__, url_prefix='/api/resume')

@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file (in production, use cloud storage)
    filename = f"resume_{user_id}_{datetime.utcnow().timestamp()}.pdf"
    file_path = os.path.join('uploads', filename)
    file.save(file_path)
    
    # Store resume record
    resume_data = {
        'user_id': ObjectId(user_id),
        'filename': filename,
        'file_path': file_path,
        'created_at': datetime.utcnow()
    }
    
    resumes.insert_one(resume_data)
    
    return jsonify({
        'message': 'Resume uploaded successfully',
        'filename': filename
    })

@bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_resume():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Generate resume analysis using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer and career counselor."},
                {"role": "user", "content": f"""
                Analyze the following resume content and provide feedback:
                
                {data.get('content', '')}
                
                Please provide:
                1. Overall assessment
                2. Key strengths
                3. Areas for improvement
                4. Specific suggestions for enhancement
                5. Industry-specific recommendations
                """}
            ]
        )
        
        analysis = response.choices[0].message.content
        
        # Store analysis
        resume_data = {
            'user_id': ObjectId(user_id),
            'content': data.get('content', ''),
            'analysis': analysis,
            'created_at': datetime.utcnow()
        }
        
        resumes.insert_one(resume_data)
        
        return jsonify({
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_resume_history():
    user_id = get_jwt_identity()
    
    # Get user's resume history
    user_resumes = resumes.find({
        'user_id': ObjectId(user_id)
    }).sort('created_at', -1)
    
    return jsonify([{
        'id': str(resume['_id']),
        'filename': resume.get('filename'),
        'analysis': resume.get('analysis'),
        'created_at': resume['created_at']
    } for resume in user_resumes]) 