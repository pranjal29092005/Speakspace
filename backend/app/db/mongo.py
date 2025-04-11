from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MongoDB client
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.get_database()

# Collections
users = db.users
rooms = db.rooms
sessions = db.sessions
feedback = db.feedback
resumes = db.resumes

# Indexes
users.create_index('email', unique=True)
rooms.create_index('name', unique=True)
sessions.create_index([('room_id', 1), ('created_at', -1)])
feedback.create_index([('user_id', 1), ('session_id', 1)])
resumes.create_index([('user_id', 1), ('created_at', -1)]) 