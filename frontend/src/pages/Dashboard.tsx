import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

interface Session {
  id: string;
  room_name: string;
  date: string;
  role: string;
  confidence_score: number;
}

interface Feedback {
  id: string;
  session_id: string;
  confidence_score: number;
  ai_feedback: string;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sessionsRes, feedbackRes] = await Promise.all([
          axios.get('/api/sessions/user'),
          axios.get(`/api/feedback/user/${user?.id}`)
        ]);

        setSessions(sessionsRes.data);
        setFeedback(feedbackRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="py-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome, {user?.name}!</h1>
        
        <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Recent Sessions */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Recent Sessions</h2>
              <Link
                to="/room/create"
                className="bg-primary text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-dark"
              >
                Create Room
              </Link>
            </div>
            
            <div className="space-y-4">
              {sessions.length === 0 ? (
                <p className="text-gray-500">No sessions yet. Create a room to get started!</p>
              ) : (
                sessions.map((session) => (
                  <div key={session.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-medium text-gray-900">{session.room_name}</h3>
                        <p className="text-sm text-gray-500">
                          {new Date(session.date).toLocaleDateString()} • {session.role}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Score: {session.confidence_score}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Recent Feedback */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Feedback</h2>
            <div className="space-y-4">
              {feedback.length === 0 ? (
                <p className="text-gray-500">No feedback yet. Join a session to receive AI feedback!</p>
              ) : (
                feedback.map((item) => (
                  <div key={item.id} className="border rounded-lg p-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-500">
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Score: {item.confidence_score}
                        </span>
                      </div>
                      <p className="text-gray-700">{item.ai_feedback}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="mt-8">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Progress Overview</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-500">Total Sessions</h3>
                <p className="mt-1 text-3xl font-semibold text-gray-900">{sessions.length}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-500">Average Score</h3>
                <p className="mt-1 text-3xl font-semibold text-gray-900">
                  {feedback.length > 0
                    ? Math.round(
                        feedback.reduce((acc, item) => acc + item.confidence_score, 0) / feedback.length
                      )
                    : 0}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-500">Total Feedback</h3>
                <p className="mt-1 text-3xl font-semibold text-gray-900">{feedback.length}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 