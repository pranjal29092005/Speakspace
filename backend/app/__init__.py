from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes after app initialization to avoid circular imports
from app.routes import auth, rooms, feedback, resume

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(rooms.bp)
app.register_blueprint(feedback.bp)
app.register_blueprint(resume.bp)

if __name__ == '__main__':
    socketio.run(app, debug=True) 