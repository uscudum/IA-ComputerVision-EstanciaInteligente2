from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet

# Configuración de Flask y Socket.IO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.json
    if data and 'message' in data:
        # Emitir el evento 'object_detected' al cliente
        socketio.emit('object_detected', {'message': data['message']})
        return 'Mensaje recibido', 200
    return 'No se recibió ningún mensaje', 400

if __name__ == "__main__":
    # Usar eventlet para el servidor
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
