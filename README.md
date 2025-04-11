# SpeakSpace

A real-time platform for practicing group discussions and interviews with AI-powered feedback.

## Features

- User Authentication (JWT)
- Real-time text and voice chat
- Room system with different roles (Moderator, Participant, Evaluator)
- AI-powered feedback on communication skills
- Progress tracking and leaderboard
- Resume review with GPT-based suggestions

## Tech Stack

- Frontend: React.js (TypeScript), TailwindCSS
- Backend: Flask (Python)
- Real-time: Socket.io
- Database: MongoDB
- AI: OpenAI API (GPT-4) and Whisper API

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- MongoDB
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/speakspace.git
cd speakspace
```

2. Frontend setup:
```bash
cd frontend
npm install
npm start
```

3. Backend setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

4. Configure environment variables:
- Copy `.env.example` to `.env` in the backend directory
- Update the values in `.env` with your configuration

## Development

- Frontend runs on http://localhost:3000
- Backend runs on http://localhost:5000

## License

This project is licensed under the MIT License - see the LICENSE file for details. 