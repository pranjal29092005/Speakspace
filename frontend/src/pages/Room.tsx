import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { io, Socket } from 'socket.io-client';
import axios from 'axios';

interface Message {
  user_id: string;
  user_name: string;
  message: string;
  timestamp: string;
}

interface Participant {
  user_id: string;
  name: string;
  role: string;
  joined_at: string;
}

const Room: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const socketRef = useRef<Socket>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Connect to Socket.IO server
    socketRef.current = io(process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000', {
      auth: {
        token: localStorage.getItem('token')
      }
    });

    // Join room
    socketRef.current.emit('join', {
      room_id: roomId,
      user_id: user?.id,
      user_name: user?.name
    });

    // Listen for new messages
    socketRef.current.on('new_message', (message: Message) => {
      setMessages(prev => [...prev, message]);
    });

    // Listen for participant updates
    socketRef.current.on('user_joined', (data: { user_id: string; user_name: string }) => {
      setParticipants(prev => [
        ...prev,
        {
          user_id: data.user_id,
          name: data.user_name,
          role: 'participant',
          joined_at: new Date().toISOString()
        }
      ]);
    });

    socketRef.current.on('user_left', (data: { user_id: string }) => {
      setParticipants(prev => prev.filter(p => p.user_id !== data.user_id));
    });

    // Fetch room data
    const fetchRoomData = async () => {
      try {
        const response = await axios.get(`/api/rooms/${roomId}`);
        setParticipants(response.data.participants);
      } catch (error) {
        setError('Failed to load room data');
        navigate('/dashboard');
      }
    };

    fetchRoomData();

    return () => {
      if (socketRef.current) {
        socketRef.current.emit('leave', {
          room_id: roomId,
          user_id: user?.id,
          user_name: user?.name
        });
        socketRef.current.disconnect();
      }
    };
  }, [roomId, user, navigate]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    socketRef.current?.emit('message', {
      room_id: roomId,
      user_id: user?.id,
      user_name: user?.name,
      message: newMessage
    });

    setNewMessage('');
  };

  const toggleRecording = () => {
    if (isRecording) {
      socketRef.current?.emit('stop_recording', {
        room_id: roomId,
        user_id: user?.id
      });
    } else {
      socketRef.current?.emit('start_recording', {
        room_id: roomId,
        user_id: user?.id
      });
    }
    setIsRecording(!isRecording);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Participants List */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Participants</h2>
            <div className="space-y-4">
              {participants.map((participant) => (
                <div
                  key={participant.user_id}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{participant.name}</p>
                    <p className="text-sm text-gray-500">{participant.role}</p>
                  </div>
                  {participant.role === 'moderator' && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Moderator
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chat and Controls */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Discussion</h2>
              <button
                onClick={toggleRecording}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  isRecording
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-primary text-white hover:bg-primary-dark'
                }`}
              >
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </button>
            </div>

            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto mb-4 space-y-4 p-4 bg-gray-50 rounded-lg">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.user_id === user?.id ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-xs px-4 py-2 rounded-lg ${
                      message.user_id === user?.id
                        ? 'bg-primary text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <p className="text-sm font-medium">{message.user_name}</p>
                    <p className="text-sm">{message.message}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="mt-4">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
                <button
                  type="submit"
                  className="bg-primary text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-dark"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Room; 