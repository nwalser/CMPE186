from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agent import run_agent
import os

app = Flask(__name__, static_folder='frontend')
CORS(app)

# In-memory chat history (use Redis/DB for production)
chat_sessions = {}

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get chat history
    chat_history = chat_sessions.get(session_id, [])
    
    try:
        # Run agent
        result = run_agent(user_message, chat_history)
        response = result['output']

        # Update history
        chat_history.append(("human", user_message))
        chat_history.append(("assistant", response))
        chat_sessions[session_id] = chat_history

        return jsonify({
            'response': response,
            'session_id': session_id
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)