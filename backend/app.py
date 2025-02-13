from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from pydub import AudioSegment
import io, uuid, eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active streams
streams = {}

@app.route('/')
def home():
    return "Real-time Voice Amplifier Running"

@app.route('/stream/<user_id>')
def stream(user_id):
    if user_id in streams:
        return jsonify({"status": "Streaming", "url": f"/stream/{user_id}"})
    return jsonify({"error": "Stream not found"}), 404

@socketio.on('start_recording')
def start_recording():
    user_id = str(uuid.uuid4())  # Generate unique stream ID
    streams[user_id] = []
    emit('stream_id', {"stream_url": f"/stream/{user_id}"})

@socketio.on('audio_chunk')
def process_audio(data):
    user_id = data['user_id']
    audio_chunk = data['audio']

    # Convert and amplify audio
    audio = AudioSegment.from_file(io.BytesIO(audio_chunk), format="wav")
    louder_audio = audio + 10  # Increase by 10 dB
    output = io.BytesIO()
    louder_audio.export(output, format="wav")
    
    streams[user_id].append(output.getvalue())  # Store processed audio chunks
    emit('amplified_audio', output.getvalue(), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
